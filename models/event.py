from dataclasses import dataclass, field
from typing import List


@dataclass
class Event:

    title: str

    venue: str = ""

    city: str = ""

    country: str = ""

    date: str = ""

    time: str = ""

    price: str = ""

    genres: List[str] = field(default_factory=list)

    url: str = ""

    source: str = ""

    description: str = ""