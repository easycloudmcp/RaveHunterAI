from dataclasses import dataclass
from enum import StrEnum
import re


class PostCategory(StrEnum):
    EVENT_ANNOUNCEMENT = "event_announcement"
    EVENT_RECAP = "event_recap"
    MEME_OR_CULTURE = "meme_or_culture"
    VENUE_OR_ARTIST_PROMOTION = "venue_or_artist_promotion"
    OTHER = "other"


@dataclass(slots=True)
class ClassificationResult:
    category: PostCategory
    confidence: int
    reason: str


class InstagramPostClassifier:
    EVENT_TERMS = {
        "tickets",
        "ticket",
        "lineup",
        "doors",
        "einlass",
        "vorverkauf",
        "presale",
        "save the date",
        "festival",
        "open air",
        "club night",
        "tonight",
        "morgen",
        "samstag",
        "freitag",
    }

    RECAP_TERMS = {
        "war dabei",
        "danke",
        "thank you",
        "last night",
        "gestern",
        "ausverkauft",
        "sold out",
        "was für eine nacht",
        "unvergessliche momente",
        "recap",
        "after movie",
        "aftermovie",
    }

    PROMOTION_TERMS = {
        "new release",
        "out now",
        "stream now",
        "neue single",
        "neues album",
        "tour",
        "artist",
        "dj",
        "producer",
        "venue",
        "club",
    }

    CULTURE_TERMS = {
        "techno ist",
        "bass ist",
        "meme",
        "lebenseinstellung",
        "mehr bass",
        "weniger hass",
        "techno verbindet",
        "quote",
    }

    DATE_PATTERN = re.compile(
        r"\b("
        r"\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?"
        r"|"
        r"\d{1,2}\.\s*(?:januar|februar|märz|april|mai|juni|juli|"
        r"august|september|oktober|november|dezember)"
        r")\b",
        re.IGNORECASE,
    )

    TIME_PATTERN = re.compile(
        r"\b\d{1,2}(?::\d{2})?\s*(?:uhr|pm|am)\b",
        re.IGNORECASE,
    )

    def classify(self, caption: str) -> ClassificationResult:
        normalized = " ".join(caption.lower().split())

        if not normalized:
            return ClassificationResult(
                category=PostCategory.OTHER,
                confidence=100,
                reason="Caption is empty.",
            )

        event_score = self._keyword_score(normalized, self.EVENT_TERMS)
        recap_score = self._keyword_score(normalized, self.RECAP_TERMS)
        promotion_score = self._keyword_score(
            normalized,
            self.PROMOTION_TERMS,
        )
        culture_score = self._keyword_score(
            normalized,
            self.CULTURE_TERMS,
        )

        if self.DATE_PATTERN.search(normalized):
            event_score += 3

        if self.TIME_PATTERN.search(normalized):
            event_score += 2

        if "http://" in normalized or "https://" in normalized:
            event_score += 1

        scores = {
            PostCategory.EVENT_ANNOUNCEMENT: event_score,
            PostCategory.EVENT_RECAP: recap_score,
            PostCategory.VENUE_OR_ARTIST_PROMOTION: promotion_score,
            PostCategory.MEME_OR_CULTURE: culture_score,
        }

        category, highest_score = max(
            scores.items(),
            key=lambda item: item[1],
        )

        if highest_score == 0:
            return ClassificationResult(
                category=PostCategory.OTHER,
                confidence=50,
                reason="No strong classification signals found.",
            )

        confidence = min(95, 55 + highest_score * 8)

        return ClassificationResult(
            category=category,
            confidence=confidence,
            reason=f"Highest rule score: {highest_score}.",
        )

    @staticmethod
    def _keyword_score(
        text: str,
        keywords: set[str],
    ) -> int:
        return sum(1 for keyword in keywords if keyword in text)