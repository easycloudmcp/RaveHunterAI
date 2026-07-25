from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ravehunter.discovery.source import NormalizedSourceRecord
from ravehunter.domain.enums import EventSource

LOGGER = logging.getLogger(__name__)


class MetaConnectorError(RuntimeError):
    """Safe connector failure whose text never includes credentials."""


class MetaAuthenticationError(MetaConnectorError):
    pass


class MetaRateLimitError(MetaConnectorError):
    pass


class MetaMalformedResponseError(MetaConnectorError):
    pass


@dataclass(frozen=True, slots=True)
class MetaConfig:
    access_token: str
    account_ids: tuple[str, ...]
    api_version: str = "v23.0"
    timeout_seconds: float = 10.0
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> MetaConfig:
        token = os.environ.get("META_ACCESS_TOKEN", "")
        accounts = tuple(
            item.strip()
            for item in os.environ.get("META_IG_ACCOUNT_IDS", "").split(",")
            if item.strip()
        )
        if not token or not accounts:
            raise MetaConnectorError(
                "META_ACCESS_TOKEN and META_IG_ACCOUNT_IDS must be configured."
            )
        return cls(
            access_token=token,
            account_ids=accounts,
            api_version=os.environ.get("META_GRAPH_API_VERSION", "v23.0"),
            timeout_seconds=float(os.environ.get("META_TIMEOUT_SECONDS", "10")),
            max_retries=int(os.environ.get("META_MAX_RETRIES", "3")),
        )


Transport = Callable[[str, float], tuple[int, bytes, dict[str, str]]]


def _default_transport(url: str, timeout: float) -> tuple[int, bytes, dict[str, str]]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(), dict(response.headers.items())
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers.items())


class MetaGraphClient:
    """Read-only Instagram Graph API media client."""

    FIELDS = "id,caption,media_type,media_url,permalink,timestamp"

    def __init__(
        self,
        config: MetaConfig,
        *,
        transport: Transport = _default_transport,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self._transport = transport
        self._sleep = sleeper

    def _initial_url(self, account_id: str) -> str:
        query = urllib.parse.urlencode(
            {"fields": self.FIELDS, "access_token": self.config.access_token}
        )
        return (
            f"https://graph.facebook.com/{self.config.api_version}/"
            f"{urllib.parse.quote(account_id)}/media?{query}"
        )

    def _safe_url(self, url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        safe_query = [
            (key, "<redacted>" if key == "access_token" else value)
            for key, value in query
        ]
        return urllib.parse.urlunsplit(
            (*parsed[:3], urllib.parse.urlencode(safe_query), parsed.fragment)
        )

    def _request(self, url: str) -> dict[str, Any]:
        for attempt in range(self.config.max_retries + 1):
            try:
                status, body, headers = self._transport(
                    url, self.config.timeout_seconds
                )
            except TimeoutError as error:
                if attempt >= self.config.max_retries:
                    raise MetaConnectorError("Meta request timed out.") from error
                self._sleep(2**attempt)
                continue

            if status in (401, 403):
                raise MetaAuthenticationError("Meta rejected the configured credentials.")
            if status == 429 or status >= 500:
                if attempt >= self.config.max_retries:
                    if status == 429:
                        raise MetaRateLimitError("Meta rate limit retry budget exhausted.")
                    raise MetaConnectorError("Meta retry budget exhausted.")
                retry_after = headers.get("Retry-After")
                self._sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if status >= 400:
                raise MetaConnectorError(f"Meta request failed with HTTP {status}.")
            try:
                payload = json.loads(body)
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                raise MetaMalformedResponseError("Meta returned invalid JSON.") from error
            if not isinstance(payload, dict):
                raise MetaMalformedResponseError("Meta response must be an object.")
            LOGGER.debug("Meta request completed: %s", self._safe_url(url))
            return payload
        raise AssertionError("unreachable")

    def iter_media(
        self, account_id: str, *, max_pages: int = 2
    ) -> Iterator[NormalizedSourceRecord]:
        url: str | None = self._initial_url(account_id)
        pages = 0
        while url and pages < max_pages:
            payload = self._request(url)
            data = payload.get("data")
            if not isinstance(data, list):
                raise MetaMalformedResponseError("Meta response data must be a list.")
            for item in data:
                if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                    raise MetaMalformedResponseError("Meta media item is malformed.")
                timestamp = item.get("timestamp")
                try:
                    published = (
                        datetime.fromisoformat(timestamp)
                        if isinstance(timestamp, str)
                        else None
                    )
                except ValueError as error:
                    raise MetaMalformedResponseError(
                        "Meta media timestamp is malformed."
                    ) from error
                permalink = item.get("permalink", "")
                media_url = item.get("media_url")
                yield NormalizedSourceRecord(
                    source=EventSource.INSTAGRAM,
                    external_id=item["id"],
                    content=str(item.get("caption", "")),
                    permalink=str(permalink),
                    published_at=published,
                    media_type=str(item.get("media_type", "")) or None,
                    media_url=str(media_url) if media_url else None,
                    raw_evidence_refs=tuple(
                        str(value) for value in (permalink, media_url) if value
                    ),
                    raw_evidence={"account_id": account_id, "media": item},
                )
            paging = payload.get("paging", {})
            if not isinstance(paging, dict):
                raise MetaMalformedResponseError("Meta paging value is malformed.")
            next_url = paging.get("next")
            if next_url is not None and not isinstance(next_url, str):
                raise MetaMalformedResponseError("Meta next page URL is malformed.")
            url = next_url
            pages += 1

    def collect(self, *, max_pages: int = 2) -> list[NormalizedSourceRecord]:
        return [
            record
            for account_id in self.config.account_ids
            for record in self.iter_media(account_id, max_pages=max_pages)
        ]
