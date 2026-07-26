from __future__ import annotations

import ipaddress
import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ravehunter.discovery.artifacts import LocalRawArtifactStorage, RawArtifactStorage
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


class MetaURLPolicyError(MetaConnectorError):
    """An outbound Meta URL violated the configured origin policy."""


@dataclass(frozen=True, slots=True)
class MetaConfig:
    access_token: str
    account_ids: tuple[str, ...]
    api_version: str = "v23.0"
    timeout_seconds: float = 10.0
    max_pages: int = 2
    max_retries: int = 3
    graph_api_base_url: str = "https://graph.facebook.com"

    @classmethod
    def from_env(cls) -> MetaConfig:
        token = os.environ.get("META_ACCESS_TOKEN", "")
        accounts = tuple(
            item.strip()
            for item in os.environ.get("META_INSTAGRAM_ACCOUNT_IDS", "").split(",")
            if item.strip()
        )
        if not token or not accounts:
            raise MetaConnectorError(
                "META_ACCESS_TOKEN and META_INSTAGRAM_ACCOUNT_IDS must be configured."
            )
        return cls(
            access_token=token,
            account_ids=accounts,
            api_version=os.environ.get("META_GRAPH_API_VERSION", "v23.0"),
            timeout_seconds=float(os.environ.get("META_REQUEST_TIMEOUT_SECONDS", "10")),
            max_pages=int(os.environ.get("META_MAX_PAGES", "2")),
            max_retries=int(os.environ.get("META_MAX_RETRIES", "3")),
            graph_api_base_url=os.environ.get(
                "META_GRAPH_API_BASE_URL", "https://graph.facebook.com"
            ),
        )


Transport = Callable[[str, float], tuple[int, bytes, dict[str, str]]]


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _default_transport(url: str, timeout: float) -> tuple[int, bytes, dict[str, str]]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    opener = urllib.request.build_opener(_NoRedirectHandler())
    try:
        with opener.open(request, timeout=timeout) as response:
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
        artifact_storage: RawArtifactStorage | None = None,
    ) -> None:
        self.config = config
        self._transport = transport
        self._sleep = sleeper
        self._artifact_storage = artifact_storage or LocalRawArtifactStorage(
            Path("data") / "raw-evidence" / "meta"
        )
        self._approved_origin = self._parse_approved_origin(
            self.config.graph_api_base_url
        )

    @staticmethod
    def _parse_approved_origin(base_url: str) -> tuple[str, str, int]:
        try:
            parsed = urllib.parse.urlsplit(base_url)
            port = parsed.port
        except ValueError as error:
            raise MetaURLPolicyError("Meta Graph API base URL is invalid.") from error
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or (port is not None and port != 443)
        ):
            raise MetaURLPolicyError("Meta Graph API base URL is invalid.")
        host = parsed.hostname.rstrip(".").casefold()
        if MetaGraphClient._is_forbidden_host(host):
            raise MetaURLPolicyError("Meta Graph API base URL host is not allowed.")
        return ("https", host, 443)

    @staticmethod
    def _is_forbidden_host(host: str) -> bool:
        if host == "localhost" or host.endswith(".localhost"):
            return True
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            return False
        return not address.is_global

    def _validated_url(self, candidate: str) -> str:
        try:
            resolved = urllib.parse.urljoin(
                self.config.graph_api_base_url.rstrip("/") + "/", candidate
            )
            parsed = urllib.parse.urlsplit(resolved)
            port = parsed.port
        except (TypeError, ValueError) as error:
            raise MetaURLPolicyError(
                "Meta URL failed the approved origin policy."
            ) from error
        host = parsed.hostname.rstrip(".").casefold() if parsed.hostname else ""
        origin = (parsed.scheme.casefold(), host, port or 443)
        if (
            origin != self._approved_origin
            or parsed.username is not None
            or parsed.password is not None
            or self._is_forbidden_host(host)
        ):
            raise MetaURLPolicyError("Meta URL failed the approved origin policy.")
        return resolved

    def _initial_url(self, account_id: str) -> str:
        query = urllib.parse.urlencode(
            {"fields": self.FIELDS, "access_token": self.config.access_token}
        )
        return (
            f"{self.config.graph_api_base_url.rstrip('/')}/{self.config.api_version}/"
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

    def _request(self, url: str, *, redirect_count: int = 0) -> dict[str, Any]:
        url = self._validated_url(url)
        if redirect_count > 5:
            raise MetaConnectorError("Meta redirect budget exhausted.")
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
                raise MetaAuthenticationError(
                    "Meta rejected the configured credentials."
                )
            if status == 400:
                try:
                    error_document = json.loads(body)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    error_document = {}
                meta_error = (
                    error_document.get("error")
                    if isinstance(error_document, dict)
                    else None
                )
                if isinstance(meta_error, dict) and meta_error.get("code") == 190:
                    raise MetaAuthenticationError(
                        "Meta rejected an invalid or expired access token."
                    )
            if 300 <= status < 400:
                location = headers.get("Location") or headers.get("location")
                if not location:
                    raise MetaConnectorError("Meta redirect omitted its destination.")
                return self._request(location, redirect_count=redirect_count + 1)
            if status == 429 or status >= 500:
                if attempt >= self.config.max_retries:
                    if status == 429:
                        raise MetaRateLimitError(
                            "Meta rate limit retry budget exhausted."
                        )
                    raise MetaConnectorError("Meta retry budget exhausted.")
                retry_after = headers.get("Retry-After")
                self._sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if status >= 400:
                raise MetaConnectorError(f"Meta request failed with HTTP {status}.")
            try:
                payload = json.loads(body)
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                raise MetaMalformedResponseError(
                    "Meta returned invalid JSON."
                ) from error
            if not isinstance(payload, dict):
                raise MetaMalformedResponseError("Meta response must be an object.")
            LOGGER.debug("Meta request completed: %s", self._safe_url(url))
            return payload
        raise AssertionError("unreachable")

    def iter_media(
        self, account_id: str, *, max_pages: int | None = None
    ) -> Iterator[NormalizedSourceRecord]:
        page_limit = self.config.max_pages if max_pages is None else max_pages
        if page_limit < 1:
            raise MetaConnectorError("Meta maximum pages must be at least 1.")
        url: str | None = self._initial_url(account_id)
        pages = 0
        seen_media_ids: set[str] = set()
        while url and pages < page_limit:
            payload = self._request(url)
            data = payload.get("data")
            if not isinstance(data, list):
                raise MetaMalformedResponseError("Meta response data must be a list.")
            for item in data:
                if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                    raise MetaMalformedResponseError("Meta media item is malformed.")
                if item["id"] in seen_media_ids:
                    continue
                seen_media_ids.add(item["id"])
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
                collected_at = datetime.now(UTC)
                artifact = self._artifact_storage.store(
                    account_id=account_id,
                    media_id=item["id"],
                    payload=item,
                    collected_at=collected_at,
                )
                yield NormalizedSourceRecord(
                    source=EventSource.INSTAGRAM,
                    account_id=account_id,
                    media_id=item["id"],
                    caption=str(item.get("caption", "")),
                    permalink=str(permalink),
                    published_at=published,
                    media_type=str(item.get("media_type", "")) or None,
                    media_url=str(media_url) if media_url else None,
                    collected_at=collected_at,
                    raw_evidence_reference=artifact.reference,
                )
            paging = payload.get("paging", {})
            if not isinstance(paging, dict):
                raise MetaMalformedResponseError("Meta paging value is malformed.")
            next_url = paging.get("next")
            if next_url is not None and not isinstance(next_url, str):
                raise MetaMalformedResponseError("Meta next page URL is malformed.")
            url = next_url
            pages += 1

    def collect(self, *, max_pages: int | None = None) -> list[NormalizedSourceRecord]:
        return [
            record
            for account_id in self.config.account_ids
            for record in self.iter_media(account_id, max_pages=max_pages)
        ]
