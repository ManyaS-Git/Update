from __future__ import annotations
import importlib.util
import os
import re
import threading
from dataclasses import dataclass
from typing import Any
from app.core.config import get_settings
from app.services.muril_service import get_muril_service
from app.services.sarcasm import detect_sarcasm, SarcasmResult

@dataclass
class SentiMixOutput:
    model_sentiment: str  # Raw output from SentiMix model: positive, negative, neutral, mixed
    final_sentiment: str  # Post-sarcasm-corrected sentiment: positive, negative, neutral, mixed
    confidence: float
    is_sarcastic: bool
    sarcasm_explanation: str
    language: str
    model_name: str
    status: str
    evidence: list[str]

class SentiMixService:
    """
    SentiMix Sentiment Engine.
    Specialized for social-media code-mixed Indian discourse (Hindi, Hinglish, English).
    Accepts text + MuRIL representation, computes initial SentiMix prediction,
    and applies contextual polarity-clash sarcasm augmentation.
    """
    _pipeline = None
    _lock = threading.Lock()
    _active_status = "uninitialized"

    positive_lexicon = {
        "good", "great", "excellent", "support", "fair", "justice", "right", "progress",
        "beneficial", "success", "appreciate", "empower", "equality", "opportunity", "love",
        "achi", "accha", "sahi", "samarthan", "faida", "vikas", "shandar", "zaroori", "kamaal",
        "ज़रूरी", "अच्छा", "समर्थन", "विकास", "न्याय", "समानता", "सही", "सराहनीय", "सुधार"
    }

    negative_lexicon = {
        "bad", "terrible", "worst", "wrong", "unfair", "hate", "against", "fail", "ruin",
        "disaster", "crisis", "corrupt", "oppose", "protest", "problem", "loss", "cheat",
        "hurt", "harm", "damage", "concern", "compromised", "pathetic",
        "galat", "bekar", "nuksan", "virodh", "barbaad", "dhokha", "bhrashtachar", "mushkil",
        "नफ़रत", "गलत", "विरोध", "नुकसान", "बर्बाद", "धोखा", "भ्रष्टाचार", "मुश्किल", "अन्याय"
    }

    def __init__(self, checkpoint: str | None = None):
        self.settings = get_settings()
        self.checkpoint = checkpoint or self.settings.sentimix_model_checkpoint
        self.muril = get_muril_service()

    def predict(self, text: str, context: str | None = None) -> SentiMixOutput:
        clean_text = text.strip()
        if not clean_text:
            return SentiMixOutput(
                model_sentiment="neutral",
                final_sentiment="neutral",
                confidence=0.5,
                is_sarcastic=False,
                sarcasm_explanation="",
                language="english",
                model_name=self.checkpoint,
                status="empty",
                evidence=["Empty input text"],
            )

        # 1. Obtain Multilingual Representation via MuRIL
        muril_rep = self.muril.extract_representation(clean_text)

        # 2. Check Sarcasm Polarity Clash First
        sarcasm_res: SarcasmResult = detect_sarcasm(clean_text)

        # 3. Model Inference: Try Transformers SentiMix Checkpoint
        model_sentiment = "neutral"
        model_conf = 0.55
        model_evidence = []
        model_status = "active_fallback"

        if importlib.util.find_spec("transformers") and importlib.util.find_spec("torch"):
            try:
                with self._lock:
                    if self._pipeline is None:
                        from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
                        tokenizer = AutoTokenizer.from_pretrained(
                            self.checkpoint,
                            cache_dir=self.settings.hf_model_cache,
                            token=self.settings.hf_token,
                        )
                        model = AutoModelForSequenceClassification.from_pretrained(
                            self.checkpoint,
                            cache_dir=self.settings.hf_model_cache,
                            token=self.settings.hf_token,
                        )
                        self._pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer, device=self.settings.model_device)
                        SentiMixService._active_status = "executed_local_weights"

                if self._pipeline:
                    res = self._pipeline(clean_text[:512], top_k=3)
                    rows = res[0] if isinstance(res[0], list) else res
                    best = max(rows, key=lambda r: r["score"])
                    lbl = str(best["label"]).lower()
                    if "pos" in lbl or "label_2" in lbl:
                        model_sentiment = "positive"
                    elif "neg" in lbl or "label_0" in lbl:
                        model_sentiment = "negative"
                    else:
                        model_sentiment = "neutral"
                    model_conf = float(best["score"])
                    model_status = "executed"
                    model_evidence.append(f"SentiMix classifier output: {model_sentiment} ({int(model_conf*100)}% confidence)")
            except Exception:
                SentiMixService._active_status = "active_fallback"

        # 4. Statistical SentiMix Social Code-Mixed Analysis (Fallback or baseline validation)
        if model_status != "executed":
            lowered = clean_text.lower()
            words = set(re.findall(r"[\w'-]+", lowered))
            pos_matches = words & self.positive_lexicon
            neg_matches = words & self.negative_lexicon

            if pos_matches and neg_matches and abs(len(pos_matches) - len(neg_matches)) <= 1:
                model_sentiment = "mixed"
                model_conf = 0.70
                model_evidence.append(f"Mixed positive and negative sentiment tokens observed: {', '.join(list(pos_matches)[:2])} vs {', '.join(list(neg_matches)[:2])}")
            elif len(neg_matches) > len(pos_matches):
                model_sentiment = "negative"
                model_conf = min(0.95, 0.65 + 0.08 * (len(neg_matches) - len(pos_matches)))
                model_evidence.append(f"SentiMix negative markers: {', '.join(list(neg_matches)[:3])}")
            elif len(pos_matches) > len(neg_matches):
                model_sentiment = "positive"
                model_conf = min(0.95, 0.65 + 0.08 * (len(pos_matches) - len(neg_matches)))
                model_evidence.append(f"SentiMix positive markers: {', '.join(list(pos_matches)[:3])}")
            else:
                model_sentiment = "neutral"
                model_conf = 0.60
                model_evidence.append("Balanced or neutral conversational phrasing")

        # 5. Sarcasm Augmentation (Post-Processing Correction)
        final_sentiment = model_sentiment
        sarcasm_explanation = ""

        if sarcasm_res.sarcasm_detected:
            if model_sentiment == "positive":
                final_sentiment = "negative"
                model_conf = max(model_conf, sarcasm_res.sarcasm_confidence)
                sarcasm_explanation = f"Sarcasm detected with {int(sarcasm_res.sarcasm_confidence*100)}% confidence: positive praise was paired with negative contextual markers."
                model_evidence.append(sarcasm_explanation)
            elif model_sentiment == "neutral":
                final_sentiment = "negative"
                sarcasm_explanation = f"Sarcasm detected with {int(sarcasm_res.sarcasm_confidence*100)}% confidence: cynical or ironic polarity clash identified."
                model_evidence.append(sarcasm_explanation)

        return SentiMixOutput(
            model_sentiment=model_sentiment,
            final_sentiment=final_sentiment,
            confidence=round(model_conf, 3),
            is_sarcastic=sarcasm_res.sarcasm_detected,
            sarcasm_explanation=sarcasm_explanation,
            language=muril_rep.language,
            model_name=self.checkpoint,
            status=model_status,
            evidence=model_evidence,
        )

_sentimix_instance = SentiMixService()

def get_sentimix_service() -> SentiMixService:
    return _sentimix_instance
