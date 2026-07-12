from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedInstagramEvent:
    title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    ticket_url: Optional[str] = None


class InstagramEventParser:

    DATE_PATTERN = re.compile(
        r"\b(\d{1,2}[./]\d{1,2}[./]\d{2,4})\b"
    )

    TIME_PATTERN = re.compile(
        r"\b((?:[01]?\d|2[0-3]):[0-5]\d)\b"
    )

    URL_PATTERN = re.compile(
        r"https?://\S+"
    )

    CITIES = [
        "München",
        "Berlin",
        "Hamburg",
        "Köln",
        "Frankfurt",
        "Leipzig",
        "Stuttgart",
        "Wien",
        "Vienna",
        "Zürich",
        "Zurich",
        "Innsbruck",
    ]

    def parse(self, caption: str) -> ParsedInstagramEvent:

        event = ParsedInstagramEvent()

        lines = [
            line.strip()
            for line in caption.splitlines()
            if line.strip()
        ]

        if lines:
            event.title = lines[0]

        date = self.DATE_PATTERN.search(caption)
        if date:
            event.date = date.group(1)

        time = self.TIME_PATTERN.search(caption)
        if time:
            event.time = time.group(1)

        url = self.URL_PATTERN.search(caption)
        if url:
            event.ticket_url = url.group(0)

        lower_caption = caption.lower()

        for city in self.CITIES:
            if city.lower() in lower_caption:
                event.city = city
                break

        return event