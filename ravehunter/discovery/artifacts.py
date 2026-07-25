from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class RawArtifact:
    reference: str
    content_hash: str
    collected_at: datetime


class RawArtifactStorage(ABC):
    """Provider-neutral evidence storage boundary."""

    @abstractmethod
    def store(
        self,
        *,
        account_id: str,
        media_id: str,
        payload: dict[str, Any],
        collected_at: datetime,
    ) -> RawArtifact:
        """Persist a token-free source payload and return its reference."""


class LocalRawArtifactStorage(RawArtifactStorage):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def store(
        self,
        *,
        account_id: str,
        media_id: str,
        payload: dict[str, Any],
        collected_at: datetime,
    ) -> RawArtifact:
        safe_payload = _redact(payload)
        document = {
            "account_id": account_id,
            "media_id": media_id,
            "collected_at": collected_at.astimezone(UTC).isoformat(),
            "payload": safe_payload,
        }
        encoded = json.dumps(
            document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        target = self.root / account_id / f"{media_id}-{digest[:12]}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
        return RawArtifact(
            reference=target.resolve().as_uri(),
            content_hash=digest,
            collected_at=collected_at,
        )


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: (
                "<redacted>"
                if key.casefold() in {"access_token", "authorization"}
                else _redact(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value
