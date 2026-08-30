import re
from collections import Counter
from app.models.schemas import SignalQualification

class CSQEService:
    """Explainable pre-NLP qualification; retains all records and returns a weight."""
    low_context = {"binod", "lol", "lmao", "first", "nice", "ok", "wow"}
    topic_terms = {"reservation","policy","student","education","job","fair","merit","equality","caste","admission","opportunity"}
    def qualify(self, text: str) -> SignalQualification:
        clean = re.sub(r"\s+", " ", text.strip())
        words = re.findall(r"[\w'-]+", clean.lower())
        if not clean:
            return self._result(text, .02, "LOW_SIGNAL", "Empty content")
        if clean.lower() in self.low_context or len(words) <= 1:
            return self._result(text, .12, "LOW_SIGNAL", "Contextless / insufficient semantic contribution")
        emoji_like = not any(character.isalnum() for character in clean)
        if emoji_like:
            return self._result(text, .06, "LOW_SIGNAL", "Emoji or symbol-only content")
        repetition = max(Counter(words).values()) / len(words)
        if len(words) >= 4 and repetition > .7:
            return self._result(text, .18, "LOW_SIGNAL", "Bot-like or repetitive text pattern")
        relevance = len(set(words) & self.topic_terms)
        length_score = min(len(words) / 15, 1)
        score = min(.98, .32 + length_score * .38 + min(relevance, 3) * .1)
        if score >= .7: return self._result(text, score, "HIGH_SIGNAL", "Directly relevant and semantically substantive")
        return self._result(text, score, "MEDIUM_SIGNAL", "Meaningful text with limited explicit topic evidence")
    @staticmethod
    def _result(text: str, score: float, classification: str, reason: str) -> SignalQualification:
        return SignalQualification(text=text,signal_quality=round(score,2),classification=classification,reason=reason)
