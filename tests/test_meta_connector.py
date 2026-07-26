import json
import logging
from datetime import UTC, datetime

import pytest

from ravehunter.collectors.meta import (
    MetaAuthenticationError,
    MetaConfig,
    MetaConnectorError,
    MetaGraphClient,
    MetaMalformedResponseError,
    MetaRateLimitError,
    MetaURLPolicyError,
)
from ravehunter.discovery.artifacts import LocalRawArtifactStorage


def response(payload, status=200, headers=None):
    return status, json.dumps(payload).encode(), headers or {}


def config(**changes):
    values = {
        "access_token": "secret-token",
        "account_ids": ("account-1",),
        "max_retries": 2,
    }
    values.update(changes)
    return MetaConfig(**values)


def test_meta_pagination_and_media_fields(tmp_path):
    calls = []

    def transport(url, timeout):
        calls.append((url, timeout))
        if len(calls) == 1:
            return response(
                {
                    "data": [
                        {
                            "id": "1",
                            "caption": "Night",
                            "media_type": "IMAGE",
                            "media_url": "https://cdn/1.jpg",
                            "permalink": "https://ig/p/1",
                            "timestamp": "2026-08-15T20:00:00Z",
                        }
                    ],
                    "paging": {"next": "https://graph.facebook.com/page-2"},
                }
            )
        return response({"data": [{"id": "2"}]})

    records = MetaGraphClient(
        config(),
        transport=transport,
        artifact_storage=LocalRawArtifactStorage(tmp_path),
    ).collect(max_pages=2)
    assert [record.external_id for record in records] == ["1", "2"]
    assert records[0].media_type == "IMAGE"
    assert len(calls) == 2


def test_relative_pagination_stays_on_approved_origin(tmp_path):
    calls = []

    def transport(url, timeout):
        calls.append(url)
        if len(calls) == 1:
            return response({"data": [], "paging": {"next": "/v23.0/page-2"}})
        return response({"data": []})

    client = MetaGraphClient(
        config(),
        transport=transport,
        artifact_storage=LocalRawArtifactStorage(tmp_path),
    )
    client.collect(max_pages=2)
    assert calls[1] == "https://graph.facebook.com/v23.0/page-2"


@pytest.mark.parametrize(
    "hostile_url",
    [
        "http://graph.facebook.com/page-2",
        "https://localhost/page-2",
        "https://127.0.0.1/page-2",
        "https://[::1]/page-2",
        "https://10.1.2.3/page-2",
        "https://172.16.0.1/page-2",
        "https://192.168.1.1/page-2",
        "https://169.254.169.254/latest/meta-data",
        "https://example.com/page-2",
        "https://graph.facebook.com.evil.example/page-2",
        "https://graph.facebook.com@evil.example/page-2",
        "https://evil-graph.facebook.com/page-2",
        "https://graph.facebook.com:8443/page-2",
        "https://[invalid/page-2",
    ],
)
def test_hostile_pagination_is_rejected_without_request(hostile_url, tmp_path):
    calls = []

    def transport(url, timeout):
        calls.append(url)
        return response({"data": [], "paging": {"next": hostile_url}})

    client = MetaGraphClient(
        config(),
        transport=transport,
        artifact_storage=LocalRawArtifactStorage(tmp_path),
    )
    with pytest.raises(MetaURLPolicyError, match="approved origin"):
        client.collect(max_pages=2)
    assert len(calls) == 1


def test_redirect_destination_uses_same_origin_policy(tmp_path):
    calls = []

    def transport(url, timeout):
        calls.append(url)
        return 302, b"", {"Location": "https://169.254.169.254/latest/meta-data"}

    client = MetaGraphClient(
        config(),
        transport=transport,
        artifact_storage=LocalRawArtifactStorage(tmp_path),
    )
    with pytest.raises(MetaURLPolicyError, match="approved origin") as caught:
        client.collect()
    assert len(calls) == 1
    assert "secret-token" not in str(caught.value)


def test_safe_redirect_is_followed(tmp_path):
    calls = []

    def transport(url, timeout):
        calls.append(url)
        if len(calls) == 1:
            return 302, b"", {"Location": "/v23.0/redirected"}
        return response({"data": []})

    client = MetaGraphClient(
        config(),
        transport=transport,
        artifact_storage=LocalRawArtifactStorage(tmp_path),
    )
    assert client.collect() == []
    assert calls[1] == "https://graph.facebook.com/v23.0/redirected"


def test_empty_response():
    client = MetaGraphClient(
        config(), transport=lambda url, timeout: response({"data": []})
    )
    assert client.collect() == []


@pytest.mark.parametrize(
    "payload",
    [{"data": {}}, {"data": [None]}, {"data": [{"caption": "missing id"}]}],
)
def test_malformed_response(payload):
    client = MetaGraphClient(config(), transport=lambda url, timeout: response(payload))
    with pytest.raises(MetaMalformedResponseError):
        client.collect()


def test_invalid_json():
    client = MetaGraphClient(config(), transport=lambda url, timeout: (200, b"{", {}))
    with pytest.raises(MetaMalformedResponseError):
        client.collect()


def test_invalid_token_is_redacted():
    client = MetaGraphClient(
        config(), transport=lambda url, timeout: response({}, status=401)
    )
    with pytest.raises(MetaAuthenticationError) as caught:
        client.collect()
    assert "secret-token" not in str(caught.value)


def test_rate_limit_retries_then_succeeds():
    statuses = iter([429, 200])
    sleeps = []

    def transport(url, timeout):
        status = next(statuses)
        return response({"data": []}, status=status, headers={"Retry-After": "0.25"})

    client = MetaGraphClient(config(), transport=transport, sleeper=sleeps.append)
    assert client.collect() == []
    assert sleeps == [0.25]


def test_rate_limit_exhaustion():
    client = MetaGraphClient(
        config(max_retries=1),
        transport=lambda url, timeout: response({}, status=429),
        sleeper=lambda seconds: None,
    )
    with pytest.raises(MetaRateLimitError):
        client.collect()


def test_server_retry_exhaustion():
    client = MetaGraphClient(
        config(max_retries=1),
        transport=lambda url, timeout: response({}, status=503),
        sleeper=lambda seconds: None,
    )
    with pytest.raises(MetaConnectorError, match="retry budget"):
        client.collect()


def test_timeout_exhaustion():
    def timeout(url, seconds):
        raise TimeoutError()

    client = MetaGraphClient(
        config(max_retries=1), transport=timeout, sleeper=lambda seconds: None
    )
    with pytest.raises(MetaConnectorError, match="timed out"):
        client.collect()


def test_debug_log_redacts_token(caplog):
    caplog.set_level(logging.DEBUG)
    client = MetaGraphClient(
        config(), transport=lambda url, timeout: response({"data": []})
    )
    client.collect()
    assert "secret-token" not in caplog.text
    assert "%3Credacted%3E" in caplog.text


def test_expired_token_error_is_normalized():
    client = MetaGraphClient(
        config(),
        transport=lambda url, timeout: response(
            {"error": {"code": 190, "message": "expired secret-token"}},
            status=400,
        ),
    )
    with pytest.raises(MetaAuthenticationError) as caught:
        client.collect()
    assert "secret-token" not in str(caught.value)


def test_duplicate_media_is_emitted_once(tmp_path):
    payload = {"data": [{"id": "same"}, {"id": "same"}]}
    client = MetaGraphClient(
        config(),
        transport=lambda url, timeout: response(payload),
        artifact_storage=LocalRawArtifactStorage(tmp_path),
    )
    assert [record.media_id for record in client.collect()] == ["same"]


def test_raw_artifact_storage_redacts_credentials(tmp_path):
    storage = LocalRawArtifactStorage(tmp_path)
    artifact = storage.store(
        account_id="account-1",
        media_id="media-1",
        payload={"caption": "safe", "access_token": "secret-token"},
        collected_at=datetime.now(UTC),
    )
    stored = next(tmp_path.rglob("*.json")).read_text(encoding="utf-8")
    assert artifact.reference.startswith("file:")
    assert "secret-token" not in stored
    assert "<redacted>" in stored


def test_required_environment_configuration(monkeypatch):
    monkeypatch.delenv("META_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("META_INSTAGRAM_ACCOUNT_IDS", raising=False)
    with pytest.raises(MetaConnectorError, match="must be configured"):
        MetaConfig.from_env()
