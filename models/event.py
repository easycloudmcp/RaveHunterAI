from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Event:
    event_name: str

    event_date: Optional[str] = None

    city: Optional[str] = None

    country: Optional[str] = None

    venue: Optional[str] = None

    genre: Optional[str] = None

    ticket_url: Optional[str] = None

    instagram_url: Optional[str] = None

    price: Optional[str] = None

    dresscode: Optional[str] = None

    recommendation: Optional[int] = None

    drive_time: Optional[str] = None

    source: str = ""