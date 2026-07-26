from __future__ import annotations

from dataclasses import dataclass, replace

from ravehunter.ai.provider import AIProvider
from ravehunter.discovery.source import NormalizedSourceRecord
from ravehunter.domain.confidence import Confidence
from ravehunter.domain.media import Media
from repositories.event_repository import EventRepository


@dataclass(frozen=True, slots=True)
class PipelineResult:
    received: int = 0
    classified_as_event: int = 0
    rejected: int = 0
    duplicates: int = 0
    persisted: int = 0


class DiscoveryPipeline:
    def __init__(self, provider: AIProvider, repository: EventRepository) -> None:
        self.provider = provider
        self.repository = repository

    def run(self, records: list[NormalizedSourceRecord]) -> PipelineResult:
        classified = rejected = duplicates = persisted = 0
        for record in records:
            classification = self.provider.classify(record.content)
            confidence = min(1.0, max(0.0, classification.confidence))
            if classification.label.casefold() != "event":
                rejected += 1
                continue
            classified += 1
            extracted = self.provider.extract_event(record.content)
            event = replace(
                extracted,
                source=record.source,
                external_id=record.external_id,
                raw_source_id=record.external_id,
                raw_evidence_refs=list(record.raw_evidence_refs),
                media=Media(
                    cover_image=record.media_url,
                    source_urls=list(record.raw_evidence_refs),
                ),
                classification_label=classification.label,
                classification_reason=classification.reason,
                confidence=Confidence(
                    value=confidence,
                    reason=classification.reason,
                    source=type(self.provider).__name__,
                ),
            )
            if not event.is_valid:
                rejected += 1
                continue
            if self.repository.insert(event):
                persisted += 1
            else:
                duplicates += 1
        return PipelineResult(
            received=len(records),
            classified_as_event=classified,
            rejected=rejected,
            duplicates=duplicates,
            persisted=persisted,
        )
