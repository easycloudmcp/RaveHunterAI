from dataclasses import dataclass, field


@dataclass(slots=True)
class MusicProfile:
    genres: list[str] = field(default_factory=list)
    subgenres: list[str] = field(default_factory=list)
    artists: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)