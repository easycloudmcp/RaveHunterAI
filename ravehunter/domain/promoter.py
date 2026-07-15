from dataclasses import dataclass


@dataclass(slots=True)
class Promoter:
    name: str
    website: str | None = None
    instagram: str | None = None
    email: str | None = None
    phone: str | None = None