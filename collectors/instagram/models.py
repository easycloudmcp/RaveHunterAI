from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from services.instagram_event_parser import ParsedInstagramEvent


@dataclass
class InstagramPost:
    url: str
    caption: str
    post_date: Optional[str] = None

    image_url: Optional[str] = None
    video_url: Optional[str] = None

    category: Optional[str] = None

    parsed_event: Optional[ParsedInstagramEvent] = None