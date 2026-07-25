from __future__ import annotations

import re

from bs4 import BeautifulSoup


class InstagramPostParser:

    def extract_caption(self, html: str) -> str:

        soup = BeautifulSoup(html, "html.parser")

        meta = soup.find(
            "meta",
            attrs={"property": "og:description"},
        )

        if meta:

            content = meta.get("content", "")

            match = re.search(
                r':\s*"(.+)"',
                content,
                re.DOTALL,
            )

            if match:
                return match.group(1).strip()

        return ""