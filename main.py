from rich.console import Console
from rich.panel import Panel

from config.settings import APP_NAME, APP_VERSION
from database.database import Database

console = Console()


def startup():

    db = Database()

    db.create_tables()

    console.print(
        Panel.fit(
            f"""
[bold cyan]{APP_NAME}[/bold cyan]

Version {APP_VERSION}

✓ SQLite Connected

✓ Tables Ready
""",
            title="Startup",
        )
    )

    db.close()


if __name__ == "__main__":

    startup()