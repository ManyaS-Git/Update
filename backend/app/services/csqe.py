from __future__ import annotations
import hashlib
import re
from collections import Counter
from app.core.config import get_settings
from app.models.schemas import SignalQualification

class CSQEService:
    """
    Contextual Signal Quality Engine (CSQE).
    Filters noise, spam, duplicates, near-duplicates, and bot patterns before expensive NLP.
    Never aggressively discards genuine short opinions.
    """
    _seen_hashes: set[str] = set()
    _recent_token_sets: list[set[str]] = []
    _max_history: int = 1000

    low_context_words = {
        "binod", "lol", "lmao", "rofl", "first", "nice", "ok", "okay",
        "k", "wow", "yes", "no", "cool", "super", "great", "agree", "disagree",
        "sahi", "theek", "achha", "badhiya", "hi", "hello", "hmm", "hmmm"
    }

    spam_indicators = {
        "whatsapp", "telegram channel", "crypto", "free money", "earn daily",
        "airdrop", "giveaway", "dm for promo", "invest now", "guaranteed profit",
        "check bio", "click link", "subscribe to my", "follow back", "free followers"
    }

    opinion_markers = {
        "think", "believe", "agree", "disagree", "support", "oppose", "against",
        "court", "government", "policy", "right", "wrong", "unfair", "fair",
        "decision", "impact", "people", "student", "rules", "lagta", "chahiye",
        "galat", "sahi", "virodh", "samarthan"
    }

    def __init__(self, min_threshold: float | None = None):
        settings = get_settings()
        self.min_threshold = min_threshold or settings.csqe_min_threshold

    def qualify(self, text: str) -> SignalQualification:
        clean = re.sub(r"\s+", " ", text.strip())
        lowered = clean.lower()
        words = re.findall(r"[\w'-]+", lowered)

        # 1. Empty content
        if not clean or len(words) == 0:
            return self._result(text, 0.01, "LOW_SIGNAL", "Empty content")

        # 2. Emoji or symbol only
        if not any(c.isalnum() for c in clean):
            return self._result(text, 0.05, "LOW_SIGNAL", "Emoji or symbol-only content")

        # 3. Exact Duplicate detection
        text_hash = hashlib.sha256(clean.encode("utf-8")).hexdigest()
        if text_hash in self._seen_hashes:
            return self._result(text, 0.15, "LOW_SIGNAL", "Duplicate: identical post already processed")
        self._add_hash(text_hash)

        # 4. Spam patterns
        for spam_term in self.spam_indicators:
            if spam_term in lowered:
                return self._result(text, 0.10, "LOW_SIGNAL", f"Spam pattern detected: '{spam_term}'")

        # 5. Near-duplicate detection (Jaccard similarity > 0.85)
        current_tokens = set(words)
        if len(current_tokens) >= 4:
            for past_tokens in self._recent_token_sets[-200:]:
                intersection = len(current_tokens & past_tokens)
                union = len(current_tokens | past_tokens)
                if union > 0 and (intersection / union) > 0.85:
                    return self._result(text, 0.20, "LOW_SIGNAL", "Near-duplicate content pattern")
            self._add_tokens(current_tokens)

        # 6. Repetition / Bot pattern
        word_counts = Counter(words)
        max_freq = max(word_counts.values())
        if len(words) >= 4 and (max_freq / len(words)) > 0.65:
            return self._result(text, 0.18, "LOW_SIGNAL", "Repetitive or automated word repetition pattern")

        char_repeat = re.search(r"(.)\1{5,}", lowered)
        if char_repeat:
            return self._result(text, 0.22, "LOW_SIGNAL", "Excessive character repetition spam")

        # 7. Contextless one-word or two-word reactions
        if len(words) <= 2:
            if lowered in self.low_context_words or all(w in self.low_context_words for w in words):
                return self._result(text, 0.12, "LOW_SIGNAL", "Extremely low-information reaction without context")

        # 8. Genuine short opinion preservation
        has_opinion = any(marker in lowered for marker in self.opinion_markers)
        word_count = len(words)
        length_factor = min(word_count / 16.0, 1.0)

        # Base scoring calculation
        base_score = 0.35 + (length_factor * 0.35)
        if has_opinion:
            base_score += 0.20

        # Lexical diversity check
        unique_ratio = len(set(words)) / max(1, len(words))
        score = min(0.98, base_score * (0.8 + 0.2 * unique_ratio))

        if score >= 0.70:
            return self._result(text, score, "HIGH_SIGNAL", "Substantive public opinion or discourse signal")
        elif score >= self.min_threshold:
            return self._result(text, score, "MEDIUM_SIGNAL", "Informational signal eligible for aggregate analysis")
        else:
            return self._result(text, score, "LOW_SIGNAL", "Low informational content below qualification threshold")

    def _add_hash(self, text_hash: str) -> None:
        if len(self._seen_hashes) > self._max_history:
            self._seen_hashes.clear()
        self._seen_hashes.add(text_hash)

    def _add_tokens(self, tokens: set[str]) -> None:
        if len(self._recent_token_sets) > self._max_history:
            self._recent_token_sets = self._recent_token_sets[-500:]
        self._recent_token_sets.append(tokens)

    @staticmethod
    def _result(text: str, score: float, classification: str, reason: str) -> SignalQualification:
        return SignalQualification(
            text=text,
            signal_quality=round(score, 3),
            classification=classification,
            reason=reason,
        )
