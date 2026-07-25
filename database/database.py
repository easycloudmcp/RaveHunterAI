import sqlite3
from pathlib import Path
from typing import Final

from config.settings import DATABASE_FILE as CONFIGURED_DATABASE_FILE

DATABASE_FILE: Final = Path(CONFIGURED_DATABASE_FILE)


def get_connection(database_file: str | Path = DATABASE_FILE) -> sqlite3.Connection:
    path = Path(database_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS instagram_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_url TEXT UNIQUE NOT NULL,
            caption TEXT,
            post_date TEXT,
            category TEXT,
            ai_processed INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            event_date TEXT,
            city TEXT,
            country TEXT,
            venue TEXT,
            genre TEXT,
            ticket_url TEXT UNIQUE,
            instagram_url TEXT,
            price TEXT,
            dresscode TEXT,
            recommendation INTEGER,
            drive_time TEXT,
            source TEXT NOT NULL,
            instagram_post_id INTEGER,
            confidence REAL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(instagram_post_id) REFERENCES instagram_posts(id)
        );

        CREATE TABLE IF NOT EXISTS canonical_events (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            external_id TEXT,
            raw_source_id TEXT,
            raw_evidence_refs TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            venue_id TEXT NOT NULL,
            venue_name TEXT NOT NULL,
            city TEXT,
            country TEXT,
            starts_at TEXT NOT NULL,
            ends_at TEXT,
            pricing TEXT NOT NULL,
            promoter TEXT,
            music_metadata TEXT NOT NULL,
            media_metadata TEXT NOT NULL,
            source_urls TEXT NOT NULL,
            classification_label TEXT NOT NULL,
            confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
            classification_reason TEXT NOT NULL,
            duplicate_key TEXT NOT NULL UNIQUE,
            processing_state TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(source, external_id)
        );
        CREATE INDEX IF NOT EXISTS idx_canonical_events_city
            ON canonical_events(city);
        """
    )
    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(canonical_events)")
    }
    migrations = {
        "pricing": "TEXT NOT NULL DEFAULT '{}'",
        "promoter": "TEXT",
        "music_metadata": "TEXT NOT NULL DEFAULT '{}'",
        "media_metadata": "TEXT NOT NULL DEFAULT '{}'",
        "processing_state": "TEXT NOT NULL DEFAULT 'discovered'",
    }
    for column, definition in migrations.items():
        if column not in existing_columns:
            connection.execute(
                f"ALTER TABLE canonical_events ADD COLUMN {column} {definition}"
            )
    connection.commit()


def initialize_database(database_file: str | Path = DATABASE_FILE) -> None:
    with get_connection(database_file) as connection:
        create_tables(connection)


class Database:
    """Compatibility wrapper used by the application entry point."""

    def __init__(self, database_file: str | Path = DATABASE_FILE) -> None:
        self.connection = get_connection(database_file)

    def create_tables(self) -> None:
        create_tables(self.connection)

    def close(self) -> None:
        self.connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized.")
