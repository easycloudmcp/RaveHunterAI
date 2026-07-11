from rich.console import Console
from rich.panel import Panel

from config.settings import APP_NAME, APP_VERSION
from database.database import Database
from collectors.residentadvisor import ResidentAdvisorCollector

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

    collector = ResidentAdvisorCollector()

    events = collector.collect()

    console.print(f"\nTotal events: {len(events)}")

    db.close()


if __name__ == "__main__":
    startup()