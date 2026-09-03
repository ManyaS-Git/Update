from __future__ import annotations
import math
import re
from typing import Protocol
from app.core.config import get_settings
from app.models.schemas import SentimentAnalysis
from app.services.sarcasm import detect_sarcasm

class SentimentProvider(Protocol):
    def analyse(self, text: str, context: str | None = None) -> SentimentAnalysis: ...

class MultilingualSentimentProvider:
    """
    Multilingual Sentiment Analysis for English, Hindi (Devanagari), and Hinglish (Romanised).
    Incorporates MuRIL model when transformers is present, or an Indic-lexicon statistical model.
    """
    positive_terms = {
        "good", "great", "excellent", "support", "fair", "justice", "right", "progress",
        "beneficial", "success", "appreciate", "empower", "equality", "opportunity",
        "achi", "accha", "sahi", "samarthan", "faida", "vikas", "shandar", "zaroori",
        "ज़रूरी", "अच्छा", "समर्थन", "विकास", "न्याय", "समानता", "सही", "सराहनीय"
    }

    negative_terms = {
        "bad", "terrible", "worst", "wrong", "unfair", "hate", "against", "fail",
        "disaster", "crisis", "corrupt", "oppose", "protest", "problem", "loss", "cheat",
        "hurt", "harm", "damage", "concern", "compromised",
        "galat", "bekar", "nuksan", "virodh", "barbaad", "dhokha", "bhrashtachar", "mushkil",
        "नफ़रत", "गलत", "विरोध", "नुकसान", "बर्बाद", "धोखा", "भ्रष्टाचार", "मुश्किल", "अन्याय"
    }

    def __init__(self):
        self.settings = get_settings()

    def analyse(self, text: str, context: str | None = None) -> SentimentAnalysis:
        # Check sarcasm first
        sarcasm_res = detect_sarcasm(text)

        # Try MuRIL prediction from intelligence service if available
        try:
            from app.services.intelligence import MuRILSentimentProvider
            muril = MuRILSentimentProvider(self.settings)
            pred = muril.predict(text)
            if pred and pred.model != "multilingual-heuristic-fallback":
                sentiment = pred.label
                confidence = pred.score
                if sarcasm_res.sarcasm_detected:
                    sentiment = "negative"
                    confidence = max(confidence, sarcasm_res.sarcasm_confidence)
                stance = "opposing" if sentiment == "negative" else "supportive" if sentiment == "positive" else "neutral"
                return SentimentAnalysis(
                    sentiment=sentiment,
                    sentiment_score=round(confidence, 3),
                    confidence=round(confidence, 3),
                    stance=stance,
                    emotion="concern" if sentiment == "negative" else "optimism" if sentiment == "positive" else "neutral",
                    sarcasm=sarcasm_res,
                    language="hindi" if any("\u0900" <= c <= "\u097f" for c in text) else "english",
                    context_used=bool(context),
                )
        except Exception:
            pass

        # Robust Indic + English statistical evaluation
        lowered = f"{context or ''} {text}".lower()
        words = set(re.findall(r"[\w'-]+", lowered))

        pos_matches = words & self.positive_terms
        neg_matches = words & self.negative_terms

        pos_count = len(pos_matches)
        neg_count = len(neg_matches)

        # Script & Language check
        is_hindi = any("\u0900" <= c <= "\u097f" for c in text)
        is_hinglish = any(w in words for w in ("hai", "hain", "nahi", "kya", "kyun", "sahi", "galat", "zaroori"))
        language = "hindi" if is_hindi else "hinglish" if is_hinglish else "english"

        # Apply Sarcasm inversion
        if sarcasm_res.sarcasm_detected:
            sentiment = "negative"
            confidence = round(max(0.75, sarcasm_res.sarcasm_confidence), 2)
            stance = "opposing"
            emotion = "cynicism"
        elif neg_count > pos_count:
            sentiment = "negative"
            diff = neg_count - pos_count
            confidence = round(min(0.95, 0.65 + 0.08 * diff), 2)
            stance = "opposing"
            emotion = "concern"
        elif pos_count > neg_count:
            sentiment = "positive"
            diff = pos_count - neg_count
            confidence = round(min(0.95, 0.65 + 0.08 * diff), 2)
            stance = "supportive"
            emotion = "optimism"
        elif "?" in text:
            sentiment = "neutral"
            confidence = 0.72
            stance = "questioning"
            emotion = "curiosity"
        else:
            sentiment = "neutral"
            confidence = 0.60
            stance = "neutral"
            emotion = "calm"

        return SentimentAnalysis(
            sentiment=sentiment,
            sentiment_score=confidence,
            confidence=confidence,
            stance=stance,
            emotion=emotion,
            sarcasm=sarcasm_res,
            language=language,
            context_used=bool(context),
        )

class SentimentService:
    def __init__(self, provider: SentimentProvider | None = None):
        self.provider = provider or MultilingualSentimentProvider()

    def analyse(self, text: str, context: str | None = None) -> SentimentAnalysis:
        return self.provider.analyse(text, context)

    def analyse_batch(self, texts: list[str]) -> list[SentimentAnalysis]:
        return [self.analyse(text) for text in texts]
