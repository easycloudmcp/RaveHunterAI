from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path

from database.database import create_tables, get_connection
from repositories.event_repository import EventRepository


def _repository() -> EventRepository:
    database_file = Path(os.environ.get("RAVEHUNTER_DATABASE", "data/ravehunter.db"))
    connection = get_connection(database_file)
    create_tables(connection)
    return EventRepository(connection)


def _event_dict(event: object) -> dict[str, object]:
    from ravehunter.domain.event import Event

    assert isinstance(event, Event)
    return {
        "id": str(event.id),
        "title": event.title,
        "city": event.venue.location.city if event.venue else None,
        "venue": event.venue.name if event.venue else None,
        "starts_at": event.schedule.start.isoformat() if event.schedule.start else None,
        "source": event.source.value,
        "confidence": event.confidence.value,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ravehunter")
    commands = parser.add_subparsers(dest="command", required=True)
    collect = commands.add_parser("collect").add_subparsers(
        dest="collector", required=True
    )
    meta = collect.add_parser("meta")
    meta.add_argument("--max-pages", type=int, default=2)
    collect.add_parser("shotgun")
    events = commands.add_parser("events").add_subparsers(
        dest="event_command", required=True
    )
    listing = events.add_parser("list")
    listing.add_argument("--city")
    show = events.add_parser("show")
    show.add_argument("event_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repository = _repository()
    if args.command == "collect" and args.collector == "meta":
        from ravehunter.ai.mock_provider import MockProvider
        from ravehunter.collectors.meta import MetaConfig, MetaGraphClient
        from ravehunter.discovery.pipeline import DiscoveryPipeline

        records = MetaGraphClient(MetaConfig.from_env()).collect(
            max_pages=args.max_pages
        )
        result = DiscoveryPipeline(MockProvider(), repository).run(records)
        print(json.dumps(asdict(result)))
        return 0
    if args.command == "collect" and args.collector == "shotgun":
        from collectors.shotgun.shotgun import ShotgunCollector
        from ravehunter.adapters import legacy_event_to_canonical

        persisted = rejected = 0
        for legacy_event in ShotgunCollector().collect():
            canonical_event = legacy_event_to_canonical(legacy_event)
            if not canonical_event.is_valid:
                rejected += 1
                continue
            persisted += repository.insert(canonical_event)
        print(json.dumps({"persisted": persisted, "rejected": rejected}))
        return 0
    if args.command == "events" and args.event_command == "list":
        print(
            json.dumps(
                [_event_dict(event) for event in repository.list(city=args.city)]
            )
        )
        return 0
    event = repository.get(args.event_id)
    if event is None:
        print("Event not found.")
        return 1
    print(json.dumps(_event_dict(event)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
