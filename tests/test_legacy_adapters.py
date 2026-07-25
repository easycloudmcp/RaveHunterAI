from collectors.instagram.models import InstagramPost
from models.event import Event as LegacyEvent
from ravehunter.adapters import instagram_post_to_source, legacy_event_to_canonical
from ravehunter.domain.enums import EventSource


def test_shotgun_legacy_event_becomes_canonical():
    legacy = LegacyEvent(
        event_name="Warehouse Night",
        source="Shotgun",
        venue="Blitz",
        city="München",
        event_date="2026-08-15",
        ticket_url="https://shotgun.live/events/123",
    )
    event = legacy_event_to_canonical(legacy)
    assert event.source is EventSource.SHOTGUN
    assert event.title == "Warehouse Night"
    assert event.raw_evidence_refs == ["https://shotgun.live/events/123"]
    assert event.is_valid


def test_instagram_legacy_post_becomes_normalized_record():
    post = InstagramPost(
        id=42,
        url="https://instagram.com/p/example",
        caption="Rave",
        post_date="2026-08-15T20:00:00+00:00",
        image_url="https://cdn.example/flyer.jpg",
    )
    record = instagram_post_to_source(post)
    assert record.external_id == "42"
    assert record.source is EventSource.INSTAGRAM
    assert record.raw_evidence_refs == (
        "https://instagram.com/p/example",
        "https://cdn.example/flyer.jpg",
    )
