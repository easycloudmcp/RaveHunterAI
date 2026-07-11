from asyncio import events

from rich.console import Console
from rich.panel import Panel

from config.settings import APP_NAME, APP_VERSION
from database.database import Database
# from collectors.residentadvisor import ResidentAdvisorCollector
from collectors.shotgun import ShotgunCollector
console = Console()


def startup():

    console.print(
        Panel.fit(
            f"{APP_NAME}\nVersion {APP_VERSION}",
            title="Startup"
        )
    )

    db = Database()
    db.create_tables()

   # collector = ResidentAdvisorCollector()
    collector = ShotgunCollector()
    events = collector.collect()

    console.print(f"\nTotal events: {len(events)}\n")

    for number, event in enumerate(events, start=1):

        console.print(f"[bold cyan]{number}.[/bold cyan] {event['text']}")
        console.print(f"   {event['href']}\n")
    db.close()


if __name__ == "__main__":
    startup()