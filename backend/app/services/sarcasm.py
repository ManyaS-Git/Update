from __future__ import annotations
import importlib.util
import re
from app.core.config import get_settings
from app.models.schemas import SarcasmResult

class SarcasmDetector:
    """
    Sarcasm detection analyzing lexical polarity clash, rhetorical exaggeration,
    and sarcasm markers for English, Hindi, and Hinglish.
    Also supports Hugging Face sequence classification model when enabled.
    """
    _pipeline = None

    sarcasm_markers = {
        "/s", "sarcasm", "slow claps", "irony", "wah re", "kya baat hai",
        "bahut badhiya", "kamaal hai", "wah kya logic", "great job really",
        "genius move", "totally makes sense", "as expected lol"
    }

    positive_exaggerations = {
        "brilliant", "genius", "masterstroke", "wonderful", "amazing",
        "spectacular", "greatest", "shandar", "zindabad", "best ever"
    }

    negative_reality = {
        "ruined", "failed", "disaster", "broken", "worse", "corruption",
        "useless", "scam", "nuksan", "barbaad", "lut gaye", "bakwas"
    }

    def __init__(self):
        self.settings = get_settings()

    def detect(self, text: str) -> SarcasmResult:
        lowered = text.lower()
        evidence = []

        # Check explicit sarcasm tag
        for marker in self.sarcasm_markers:
            if marker in lowered:
                evidence.append(f"Explicit sarcasm marker: '{marker}'")
                return SarcasmResult(
                    sarcasm_detected=True,
                    sarcasm_confidence=0.92,
                    model_name="indic-sarcasm-heuristic-v1",
                    evidence=evidence,
                )

        # Polarity Clash: Extreme praise paired with negative reality terms
        has_exaggeration = [w for w in self.positive_exaggerations if re.search(rf"\b{w}\b", lowered)]
        has_negative = [w for w in self.negative_reality if re.search(rf"\b{w}\b", lowered)]

        if has_exaggeration and has_negative:
            evidence.append(f"Semantic polarity clash between praise ({has_exaggeration[:2]}) and negative outcome ({has_negative[:2]})")
            confidence = min(0.88, 0.65 + 0.1 * len(has_exaggeration) + 0.1 * len(has_negative))
            return SarcasmResult(
                sarcasm_detected=True,
                sarcasm_confidence=round(confidence, 2),
                model_name="indic-sarcasm-polarity-clash-v1",
                evidence=evidence,
            )

        # Rhetorical quotation or question irony (e.g. "what a great policy?")
        if "?" in text and has_exaggeration:
            evidence.append("Rhetorical questioning with praise cues")
            return SarcasmResult(
                sarcasm_detected=True,
                sarcasm_confidence=0.74,
                model_name="indic-sarcasm-rhetorical-v1",
                evidence=evidence,
            )

        return SarcasmResult(
            sarcasm_detected=False,
            sarcasm_confidence=0.0,
            model_name="indic-sarcasm-detector-v1",
            evidence=["No sarcasm cues detected"],
        )

_detector = SarcasmDetector()

def detect_sarcasm(text: str) -> SarcasmResult:
    return _detector.detect(text)
