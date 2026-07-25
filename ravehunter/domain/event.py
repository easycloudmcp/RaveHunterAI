from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from .confidence import Confidence
from .enums import EventSource, EventStatus
from .media import Media
from .music import MusicProfile
from .pricing import Pricing
from .promoter import Promoter
from .schedule import Schedule
from .venue import Venue


@dataclass(slots=True)
class Event:
    """
    Canonical RaveHunter event.

    This is the central business object used throughout the application.

    Collectors
        ↓
    AI Enrichment
        ↓
    Repository
        ↓
    API
        ↓
    Dashboard

    Every layer works with this object.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    id: UUID = field(default_factory=uuid4)

    source: EventSource = EventSource.MANUAL

    external_id: str | None = None

    raw_source_id: str | None = None

    raw_evidence_refs: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Core Information
    # ------------------------------------------------------------------

    title: str = ""

    description: str = ""

    # ------------------------------------------------------------------
    # Aggregate Objects
    # ------------------------------------------------------------------

    venue: Venue | None = None

    schedule: Schedule = field(default_factory=Schedule)

    pricing: Pricing = field(default_factory=Pricing)

    promoter: Promoter | None = None

    music: MusicProfile = field(default_factory=MusicProfile)

    media: Media = field(default_factory=Media)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    status: EventStatus = EventStatus.DISCOVERED

    confidence: Confidence = field(
        default_factory=lambda: Confidence(
            value=1.0,
            source="system",
        )
    )

    classification_label: str = "unclassified"

    classification_reason: str = ""

    tags: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    created: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def touch(self) -> None:
        """Update modification timestamp."""
        self.updated = datetime.now(UTC)

    def publish(self) -> None:
        self.status = EventStatus.PUBLISHED
        self.touch()

    def archive(self) -> None:
        self.status = EventStatus.ARCHIVED
        self.touch()

    def cancel(self) -> None:
        self.status = EventStatus.CANCELLED
        self.touch()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> list[str]:
        """
        Validate the event.

        Returns:
            List of validation errors.
            Empty list means the event is valid.
        """

        errors: list[str] = []

        if not self.title.strip():
            errors.append("Missing title")

        if self.venue is None:
            errors.append("Missing venue")

        if self.schedule.start is None:
            errors.append("Missing start date")

        return errors

    @property
    def is_valid(self) -> bool:
        """True if the event passes validation."""
        return len(self.validate()) == 0

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    @property
    def search_text(self) -> str:
        """
        Combined searchable text.

        Used later for:

        - SQLite FTS5
        - PostgreSQL Search
        - Azure AI Search
        - Vector Embeddings
        """

        parts: list[str] = [
            self.title,
            self.description,
        ]

        if self.venue:
            parts.append(self.venue.name)

        parts.extend(self.music.genres)
        parts.extend(self.music.artists)
        parts.extend(self.tags)

        return " ".join(
            part.strip()
            for part in parts
            if part
        )

    # ------------------------------------------------------------------
    # Duplicate Detection
    # ------------------------------------------------------------------

    @property
    def duplicate_key(self) -> str:
        """
        Stable hash used for duplicate detection.
        """

        venue = ""

        if self.venue:
            venue = self.venue.name.lower()

        date = ""

        if self.schedule.start:
            date = self.schedule.start.strftime("%Y-%m-%d")

        raw = "|".join(
            [
                self.title.lower(),
                venue,
                date,
            ]
        )

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"{self.title} "
            f"({self.source.value})"
        )

    def __repr__(self) -> str:
        return (
            f"Event("
            f"title={self.title!r}, "
            f"source={self.source.value!r}, "
            f"status={self.status.value!r}"
            f")"
        )
