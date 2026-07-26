from __future__ import annotations

from datetime import UTC, datetime

from collectors.instagram.models import InstagramPost
from models.event import Event as LegacyEvent
from ravehunter.discovery.source import NormalizedSourceRecord
from ravehunter.domain.confidence import Confidence
from ravehunter.domain.enums import EventSource
from ravehunter.domain.event import Event
from ravehunter.domain.location import Location
from ravehunter.domain.media import Media
from ravehunter.domain.schedule import Schedule
from ravehunter.domain.venue import Venue


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    candidate = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(candidate)
    except ValueError:
        for pattern in ("%d.%m.%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(value, pattern).replace(tzinfo=UTC)
            except ValueError:
                continue
    return None


def legacy_event_to_canonical(event: LegacyEvent) -> Event:
    """Adapt a legacy Shotgun/general event without hiding data loss."""

    source = (
        EventSource.SHOTGUN
        if event.source.casefold() == "shotgun"
        else EventSource.MANUAL
    )
    source_url = event.ticket_url or event.instagram_url
    return Event(
        source=source,
        external_id=source_url,
        raw_source_id=source_url,
        raw_evidence_refs=[source_url] if source_url else [],
        title=event.event_name,
        description=event.description or "",
        venue=Venue(
            name=event.venue or "Unknown venue",
            location=Location(city=event.city, country=event.country),
        ),
        schedule=Schedule(start=_parse_datetime(event.event_date)),
        media=Media(
            cover_image=event.image_url,
            source_urls=[url for url in (event.ticket_url, event.instagram_url) if url],
        ),
        confidence=Confidence(
            value=1.0,
            source="legacy-adapter",
            reason="Fields copied deterministically from the legacy event.",
        ),
        classification_label="event",
        classification_reason="Legacy Shotgun event object.",
    )


def instagram_post_to_source(post: InstagramPost) -> NormalizedSourceRecord:
    """Adapt a browser-collected Instagram post to a normalized record."""

    evidence = tuple(url for url in (post.url, post.image_url, post.video_url) if url)
    return NormalizedSourceRecord(
        source=EventSource.INSTAGRAM,
        account_id="legacy-browser-collector",
        media_id=str(post.id) if post.id is not None else post.url,
        caption=post.caption,
        permalink=post.url,
        published_at=_parse_datetime(post.post_date),
        media_type="VIDEO" if post.video_url else "IMAGE",
        media_url=post.video_url or post.image_url,
        raw_evidence_reference=evidence[0] if evidence else "",
    )
