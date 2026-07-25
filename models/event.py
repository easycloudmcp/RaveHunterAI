from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Event:

    # Identity
    event_name: str
    source: str

    # Location
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    # Time
    event_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    # Money
    price: Optional[str] = None
    currency: Optional[str] = None

    # Classification
    genre: Optional[str] = None
    subgenre: Optional[str] = None

    # Links
    ticket_url: Optional[str] = None
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None

    # Metadata
    description: Optional[str] = None
    organizer: Optional[str] = None
    image_url: Optional[str] = None

    # AI
    recommendation: Optional[int] = None
    dresscode: Optional[str] = None
    drive_time: Optional[str] = None