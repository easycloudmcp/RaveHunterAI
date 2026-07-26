from __future__ import annotations

import hashlib
import json
import os
import stat
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
    """Write-once local evidence storage.

    The configured root and its parent are trusted configuration. Publication
    does not follow target symlinks and detects replacement of the root itself,
    but it cannot defend against a filesystem administrator replacing the
    root's parent or altering files through privileges outside this process.
    """

    def __init__(self, root: str | Path) -> None:
        configured_root = Path(root)
        if configured_root.is_symlink():
            raise RuntimeError("Raw evidence root must not be a symlink.")
        configured_root.mkdir(parents=True, exist_ok=True)
        root_stat = configured_root.lstat()
        if not stat.S_ISDIR(root_stat.st_mode):
            raise RuntimeError("Raw evidence root must be a directory.")
        self.root = configured_root.resolve(strict=True)
        self._root_identity = (root_stat.st_dev, root_stat.st_ino)

    def _target_path(self, account_id: str, media_id: str, content_hash: str) -> Path:
        account_hash = hashlib.sha256(account_id.encode("utf-8")).hexdigest()
        media_hash = hashlib.sha256(media_id.encode("utf-8")).hexdigest()
        return self.root / f"{account_hash}-{media_hash}-{content_hash}.json"

    def _verify_root(self) -> None:
        try:
            root_stat = self.root.lstat()
        except OSError as error:
            raise RuntimeError("Raw evidence root is unavailable.") from error
        if (
            self.root.is_symlink()
            or not stat.S_ISDIR(root_stat.st_mode)
            or (root_stat.st_dev, root_stat.st_ino) != self._root_identity
        ):
            raise RuntimeError("Raw evidence root identity changed.")

    def _before_publish(self, target: Path) -> None:
        """Deterministic test hook immediately before publication."""

    @staticmethod
    def _read_existing(target: Path) -> bytes:
        try:
            path_stat = target.lstat()
        except OSError as error:
            raise RuntimeError(
                "Immutable raw evidence target is not a readable regular file."
            ) from error
        if stat.S_ISLNK(path_stat.st_mode) or not stat.S_ISREG(path_stat.st_mode):
            raise RuntimeError("Immutable raw evidence target must be a regular file.")

        flags = os.O_RDONLY
        flags |= getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(target, flags)
        except OSError as error:
            raise RuntimeError(
                "Immutable raw evidence target is not a readable regular file."
            ) from error
        try:
            opened_stat = os.fstat(descriptor)
            if not stat.S_ISREG(opened_stat.st_mode):
                raise RuntimeError(
                    "Immutable raw evidence target must be a regular file."
                )
            current_path_stat = target.lstat()
            if stat.S_ISLNK(current_path_stat.st_mode) or (
                current_path_stat.st_dev,
                current_path_stat.st_ino,
            ) != (opened_stat.st_dev, opened_stat.st_ino):
                raise RuntimeError("Immutable raw evidence target identity changed.")
            with os.fdopen(descriptor, "rb", closefd=False) as existing:
                return existing.read()
        finally:
            os.close(descriptor)

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
        self._verify_root()
        target = self._target_path(account_id, media_id, digest)
        temporary_path: Path | None = None
        root_descriptor: int | None = None
        try:
            if os.open in os.supports_dir_fd:
                root_descriptor = os.open(self.root, os.O_RDONLY)
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
                    self._before_publish(target)
                except OSError as error:
                    # Windows prevents renaming a directory containing this open
                    # temporary file. Normalize that safe rejection with the
                    # post-hook identity check used on POSIX.
                    raise RuntimeError("Raw evidence root identity changed.") from error
                self._verify_root()
                try:
                    if root_descriptor is not None and os.link in os.supports_dir_fd:
                        os.link(
                            temporary_path.name,
                            target.name,
                            src_dir_fd=root_descriptor,
                            dst_dir_fd=root_descriptor,
                        )
                    else:
                        os.link(temporary_path, target)
                except FileExistsError:
                    if self._read_existing(target) != encoded:
                        raise RuntimeError(
                            "Immutable raw evidence conflicts with existing content."
                        )
        finally:
            if temporary_path is not None:
                if root_descriptor is not None and os.unlink in os.supports_dir_fd:
                    try:
                        os.unlink(temporary_path.name, dir_fd=root_descriptor)
                    except FileNotFoundError:
                        pass
                else:
                    temporary_path.unlink(missing_ok=True)
            if root_descriptor is not None:
                os.close(root_descriptor)
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
