from pathlib import Path
import sqlite3

from config.settings import DATABASE_FILE


class Database:

    def __init__(self):

        self.database = Path(DATABASE_FILE)

        self.connection = sqlite3.connect(self.database)

        self.cursor = self.connection.cursor()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            event_name TEXT,

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

            source TEXT
        )
        """)

        self.connection.commit()

    def close(self):

        self.connection.close()