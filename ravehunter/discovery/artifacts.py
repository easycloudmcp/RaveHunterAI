from __future__ import annotations

import hashlib
import json
import os
import tempfile
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
        self.root = Path(root).resolve()

    def _contained_path(
        self, account_id: str, media_id: str, content_hash: str
    ) -> Path:
        account_hash = hashlib.sha256(account_id.encode("utf-8")).hexdigest()
        media_hash = hashlib.sha256(media_id.encode("utf-8")).hexdigest()
        account_directory = self.root / account_hash
        account_directory.mkdir(parents=True, exist_ok=True)
        resolved_account_directory = account_directory.resolve()
        try:
            resolved_account_directory.relative_to(self.root)
        except ValueError as error:
            raise RuntimeError(
                "Raw evidence path escaped its configured root."
            ) from error

        media_directory = resolved_account_directory / media_hash
        media_directory.mkdir(exist_ok=True)
        resolved_media_directory = media_directory.resolve()
        try:
            resolved_media_directory.relative_to(self.root)
        except ValueError as error:
            raise RuntimeError(
                "Raw evidence path escaped its configured root."
            ) from error
        target = resolved_media_directory / f"{content_hash}.json"
        try:
            target.resolve(strict=False).relative_to(self.root)
        except ValueError as error:
            raise RuntimeError(
                "Raw evidence path escaped its configured root."
            ) from error
        if target.is_symlink():
            raise RuntimeError("Raw evidence target must not be a symlink.")
        return target

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
        target = self._contained_path(account_id, media_id, digest)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=target.parent,
                prefix=".raw-evidence-",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary.write(encoded)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = Path(temporary.name)
            try:
                os.link(temporary_path, target)
            except FileExistsError:
                if target.read_bytes() != encoded:
                    raise RuntimeError(
                        "Immutable raw evidence conflicts with existing content."
                    )
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
        return RawArtifact(
            reference=target.as_uri(),
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
