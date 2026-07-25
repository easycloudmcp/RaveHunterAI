"""
RaveHunter AI
Main Application Entry Point
"""

from rich.console import Console
from rich.panel import Panel

from config.settings import APP_NAME, APP_VERSION
from database.database import Database
from discovery.discovery_engine import DiscoveryEngine

console = Console()


def startup():

    console.print(
        Panel.fit(
            f"{APP_NAME}\nVersion {APP_VERSION}",
            title="Startup",
        )
    )

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    db = Database()
    db.create_tables()

    # ------------------------------------------------------------------
    # Discovery Engine
    # ------------------------------------------------------------------

    engine = DiscoveryEngine()

    events = engine.discover()

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    console.print(f"\n[bold green]Total events: {len(events)}[/bold green]\n")

    for number, event in enumerate(events, start=1):

        console.print(
            f"[bold cyan]{number}.[/bold cyan] {event.event_name}"
        )

        if event.venue:
            console.print(f"   Venue: {event.venue}")

        if event.event_date:
            console.print(f"   Date : {event.event_date}")

        if event.price:
            console.print(f"   Price: {event.price}")

        if event.genre:
            console.print(f"   Genre: {event.genre}")

        if event.ticket_url:
            console.print(f"   URL  : {event.ticket_url}")

        console.print()

    db.close()


if __name__ == "__main__":
    startup()