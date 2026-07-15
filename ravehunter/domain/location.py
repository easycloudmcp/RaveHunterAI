from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Location:
    """
    Physical location of a venue or event.
    """

    country: str | None = None
    state: str | None = None
    city: str | None = None
    postcode: str | None = None
    street: str | None = None

    latitude: float | None = None
    longitude: float | None = None

    timezone: str = "Europe/Berlin"

    def __str__(self) -> str:
        parts = [self.city, self.country]
        return ", ".join(p for p in parts if p)