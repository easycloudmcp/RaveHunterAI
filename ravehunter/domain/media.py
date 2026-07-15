from dataclasses import dataclass, field


@dataclass(slots=True)
class Media:
    cover_image: str | None = None
    gallery: list[str] = field(default_factory=list)
    videos: list[str] = field(default_factory=list)
    flyers: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)