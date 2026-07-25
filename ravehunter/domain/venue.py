from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .location import Location


@dataclass(slots=True)
class Venue:
    """
    Canonical venue definition.

    A venue is a physical place where one or more events occur.
    """

    id: UUID = field(default_factory=uuid4)

    name: str = ""

    location: Location = field(default_factory=Location)

    website: str | None = None
    instagram: str | None = None
    facebook: str | None = None

    capacity: int | None = None

    @property
    def is_valid(self) -> bool:
        return bool(self.name.strip())

    def __str__(self) -> str:
        if self.location.city:
            return f"{self.name} ({self.location.city})"
        return self.name