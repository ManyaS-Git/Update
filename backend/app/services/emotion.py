from __future__ import annotations
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

EMOTIONS = ["joy", "anger", "sadness", "fear", "surprise", "disgust", "trust", "neutral"]

EMOTION_KEYWORDS = {
    "joy": {
        "happy", "glad", "joy", "excited", "celebrate", "great", "wonderful", "proud", "congrats",
        "khushi", "badhai", "shandar", "prasann", "उत्साह", "खुशी", "बधाई", "शानदार"
    },
    "anger": {
        "angry", "furious", "outrage", "hate", "protest", "corrupt", "unacceptable", "scam", "shame",
        "gussa", "gusse", "bakwas", "barbaad", "krodh", "गुस्सा", "क्रोध", "बकवास", "बर्बाद", "शर्म"
    },
    "sadness": {
        "sad", "tragic", "loss", "grief", "depressed", "unfortunate", "disappointed", "heartbroken",
        "dukh", "dard", "afsos", "dukhi", "दुख", "दर्द", "अफ़सोस", "निराशा"
    },
    "fear": {
        "fear", "afraid", "scared", "threat", "danger", "crisis", "panic", "worried", "anxious",
        "darr", "khatra", "chinta", "डर", "खतरा", "चिंता", "संकट", "भय"
    },
    "surprise": {
        "shock", "shocking", "surprise", "unexpected", "astonished", "unbelievable",
        "hairan", "hairat", "achambha", "हैरान", "अचंभित", "चौंकाने"
    },
    "disgust": {
        "disgusting", "gross", "filthy", "repulsive", "sickening", "vile",
        "ghinona", "nafrat", "घिनौना", "नफ़रत", "गंदा"
    },
    "trust": {
        "trust", "believe", "faith", "reliable", "confident", "assure", "secure", "honest",
        "bharosa", "vishwas", "yakeen", "ईमानदार", "भरोसा", "विश्वास", "यकीन"
    },
}

@dataclass
class EmotionPrediction:
    emotion: str
    confidence: float
    scores: dict[str, float]
    model_name: str = "Multilingual-Emotion-Engine"

class EmotionService:
    """
    Emotion Engine classifying posts across 8 emotion categories:
    Joy, Anger, Sadness, Fear, Surprise, Disgust, Trust, and Neutral.
    Evaluates topic emotion distributions and detects sudden emotional spikes.
    """

    def predict(self, text: str) -> EmotionPrediction:
        lowered = text.lower()
        words = set(re.findall(r"[\w'-]+", lowered))

        scores = {e: 0.05 for e in EMOTIONS}
        scores["neutral"] = 0.20

        matched_any = False
        for emotion, keywords in EMOTION_KEYWORDS.items():
            hits = words & keywords
            if hits:
                matched_any = True
                scores[emotion] += 0.35 + (0.15 * len(hits))

        if not matched_any:
            if any(w in words for w in ("court", "rule", "order", "statement", "case", "matter")):
                scores["neutral"] = 0.70
            else:
                scores["neutral"] = 0.50

        # Normalize
        total = sum(scores.values())
        norm_scores = {k: round(v / total, 3) for k, v in scores.items()}
        best_emotion = max(norm_scores, key=norm_scores.get)
        confidence = norm_scores[best_emotion]

        return EmotionPrediction(
            emotion=best_emotion,
            confidence=confidence,
            scores=norm_scores,
        )

    def analyze_distribution(self, texts: list[str]) -> dict[str, Any]:
        if not texts:
            return {
                "dominant": "neutral",
                "distribution": {e: (100 if e == "neutral" else 0) for e in EMOTIONS},
                "spikes": [],
            }

        counts = Counter()
        for t in texts:
            pred = self.predict(t)
            counts[pred.emotion] += 1

        total = len(texts)
        dist = {e: round((counts[e] / total) * 100, 1) for e in EMOTIONS}
        dominant = max(dist, key=dist.get)

        spikes = []
        if dist.get("anger", 0) > 30:
            spikes.append({"emotion": "anger", "percentage": dist["anger"], "message": f"Anger spike detected: represents {dist['anger']}% of analyzed discussions"})
        if dist.get("fear", 0) > 25:
            spikes.append({"emotion": "fear", "percentage": dist["fear"], "message": f"Heightened apprehension/fear signals: {dist['fear']}%"})

        return {
            "dominant": dominant,
            "distribution": dist,
            "spikes": spikes,
            "sample_size": total,
        }

_emotion_instance = EmotionService()

def get_emotion_service() -> EmotionService:
    return _emotion_instance
