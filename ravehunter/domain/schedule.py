from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Schedule:
    start: datetime | None = None
    end: datetime | None = None
    doors_open: datetime | None = None
    last_entry: datetime | None = None
    timezone: str = "Europe/Berlin"