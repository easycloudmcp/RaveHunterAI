from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from ravehunter.domain.enums import EventSource


@dataclass(frozen=True, slots=True)
class NormalizedSourceRecord:
    """Typed Meta record handed from collectors to service boundaries."""

    source: EventSource
    account_id: str
    media_id: str
    caption: str
    media_type: str | None
    media_url: str | None
    permalink: str
    published_at: datetime | None = None
    collected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    raw_evidence_reference: str = ""

    @property
    def external_id(self) -> str:
        return self.media_id

    @property
    def content(self) -> str:
        return self.caption

    @property
    def raw_evidence_refs(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                value
                for value in (
                    self.raw_evidence_reference,
                    self.permalink,
                    self.media_url,
                )
                if value
            )
        )
