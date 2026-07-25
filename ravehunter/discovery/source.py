from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ravehunter.domain.enums import EventSource


@dataclass(frozen=True, slots=True)
class NormalizedSourceRecord:
    """Provider-neutral record handed from collectors to the pipeline."""

    source: EventSource
    external_id: str
    content: str
    permalink: str
    published_at: datetime | None = None
    media_type: str | None = None
    media_url: str | None = None
    raw_evidence_refs: tuple[str, ...] = ()
    raw_evidence: dict[str, object] = field(default_factory=dict)
