from sqlite3 import Connection

from models.event import Event


class EventRepository:

    def __init__(self, connection: Connection):
        self.connection = connection

    def insert(self, event: Event) -> bool:
        cursor = self.connection.execute(
            """
            INSERT OR IGNORE INTO events (
                event_name,
                event_date,
                city,
                country,
                venue,
                genre,
                ticket_url,
                instagram_url,
                price,
                dresscode,
                recommendation,
                drive_time,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    def all(self) -> list[Event]:
        cursor = self.connection.execute(
            """
            SELECT
                event_name,
                event_date,
                city,
                country,
                venue,
                genre,
                ticket_url,
                instagram_url,
                price,
                dresscode,
                recommendation,
                drive_time,
                source
            FROM events
            """
        )

        return [
            Event(
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
            for row in cursor.fetchall()
        ]
