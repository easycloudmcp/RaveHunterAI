from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from typing import Any
from uuid import UUID

from models.event import Event as LegacyEvent
from ravehunter.domain.confidence import Confidence
from ravehunter.domain.enums import EventSource
from ravehunter.domain.event import Event
from ravehunter.domain.location import Location
from ravehunter.domain.media import Media
from ravehunter.domain.music import MusicProfile
from ravehunter.domain.pricing import Pricing
from ravehunter.domain.promoter import Promoter
from ravehunter.domain.schedule import Schedule
from ravehunter.domain.venue import Venue


class EventRepository:
    """SQLite repository with canonical and explicit legacy compatibility paths."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def insert(self, event: Event | LegacyEvent) -> bool:
        if isinstance(event, LegacyEvent):
            return self._insert_legacy(event)
        if not event.is_valid:
            raise ValueError("; ".join(event.validate()))
        assert event.venue is not None
        assert event.schedule.start is not None
        cursor = self.connection.execute(
            """
            INSERT OR IGNORE INTO canonical_events (
                id, source, external_id, raw_source_id, raw_evidence_refs,
                title, description, venue_id, venue_name, city, country,
                starts_at, ends_at, pricing, promoter, music_metadata,
                media_metadata, source_urls, classification_label,
                confidence, classification_reason, duplicate_key, created_at,
                updated_at, processing_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(event.id),
                event.source.value,
                event.external_id,
                event.raw_source_id,
                json.dumps(event.raw_evidence_refs),
                event.title,
                event.description,
                str(event.venue.id),
                event.venue.name,
                event.venue.location.city,
                event.venue.location.country,
                event.schedule.start.isoformat(),
                event.schedule.end.isoformat() if event.schedule.end else None,
                json.dumps(asdict(event.pricing)),
                json.dumps(asdict(event.promoter)) if event.promoter else None,
                json.dumps(asdict(event.music)),
                json.dumps(asdict(event.media)),
                json.dumps(event.media.source_urls),
                event.classification_label,
                event.confidence.value,
                event.classification_reason,
                event.duplicate_key,
                event.created.isoformat(),
                event.updated.isoformat(),
                event.status.value,
            ),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def _insert_legacy(self, event: LegacyEvent) -> bool:
        cursor = self.connection.execute(
            """
            INSERT OR IGNORE INTO events (
                event_name, event_date, city, country, venue, genre,
                ticket_url, instagram_url, price, dresscode, recommendation,
                drive_time, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_name,
                event.event_date,
                event.city,
                event.country,
                event.venue,
                event.genre,
                event.ticket_url,
                event.instagram_url,
                event.price,
                event.dresscode,
                event.recommendation,
                event.drive_time,
                event.source,
            ),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def get(self, event_id: str) -> Event | None:
        row = self.connection.execute(
            "SELECT * FROM canonical_events WHERE id = ?", (event_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def list(self, *, city: str | None = None) -> list[Event]:
        if city:
            rows = self.connection.execute(
                "SELECT * FROM canonical_events WHERE city = ? ORDER BY starts_at",
                (city,),
            ).fetchall()
        else:
            rows = self.connection.execute(
                "SELECT * FROM canonical_events ORDER BY starts_at"
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def all(self) -> list[Any]:
        canonical = self.list()
        if canonical:
            return canonical
        rows = self.connection.execute(
            """
            SELECT event_name, event_date, city, country, venue, genre,
                   ticket_url, instagram_url, price, dresscode, recommendation,
                   drive_time, source
            FROM events
            """
        ).fetchall()
        return [
            LegacyEvent(
                event_name=row[0],
                event_date=row[1],
                city=row[2],
                country=row[3],
                venue=row[4],
                genre=row[5],
                ticket_url=row[6],
                instagram_url=row[7],
                price=row[8],
                dresscode=row[9],
                recommendation=row[10],
                drive_time=row[11],
                source=row[12],
            )
            for row in rows
        ]

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Event:
        return Event(
            id=UUID(row["id"]),
            source=EventSource(row["source"]),
            external_id=row["external_id"],
            raw_source_id=row["raw_source_id"],
            raw_evidence_refs=json.loads(row["raw_evidence_refs"]),
            title=row["title"],
            description=row["description"],
            venue=Venue(
                id=UUID(row["venue_id"]),
                name=row["venue_name"],
                location=Location(city=row["city"], country=row["country"]),
            ),
            schedule=Schedule(
                start=datetime.fromisoformat(row["starts_at"]),
                end=datetime.fromisoformat(row["ends_at"]) if row["ends_at"] else None,
            ),
            pricing=Pricing(**json.loads(row["pricing"])),
            promoter=(
                Promoter(**json.loads(row["promoter"])) if row["promoter"] else None
            ),
            music=MusicProfile(**json.loads(row["music_metadata"])),
            media=Media(**json.loads(row["media_metadata"])),
            classification_label=row["classification_label"],
            classification_reason=row["classification_reason"],
            confidence=Confidence(
                value=row["confidence"],
                reason=row["classification_reason"],
                source="ai",
            ),
            created=datetime.fromisoformat(row["created_at"]),
            updated=datetime.fromisoformat(row["updated_at"]),
        )
