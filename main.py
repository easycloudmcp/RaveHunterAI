from rich.console import Console
from rich.panel import Panel

from config.settings import APP_NAME, APP_VERSION
from database.database import Database
from database.event_repository import EventRepository
from collectors.shotgun import ShotgunCollector
# from collectors.residentadvisor import ResidentAdvisorCollector

console = Console()


def startup():

    console.print(
        Panel.fit(
            f"{APP_NAME}\nVersion {APP_VERSION}",
            title="Startup",
        )
    )

    # Database
    db = Database()
    db.create_tables()

    repository = EventRepository(db.connection)

    # Collector
    # collector = ResidentAdvisorCollector()
    collector = ShotgunCollector()

    collected_events = collector.collect()

    # Store events
    for event in collected_events:
        repository.insert(event)

    db.connection.commit()

    # Read back from SQLite
    events = repository.all()

    console.print(f"\nTotal events: {len(events)}\n")

    for number, event in enumerate(events, start=1):
        console.print(f"[bold cyan]{number}.[/bold cyan] {event.event_name}")

        if event.ticket_url:
            console.print(f"   {event.ticket_url}")

        console.print(f"   Source: {event.source}\n")

    db.close()


if __name__ == "__main__":
    startup()