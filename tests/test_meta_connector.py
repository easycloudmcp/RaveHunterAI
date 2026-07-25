import json
import logging

import pytest

from ravehunter.collectors.meta import (
    MetaAuthenticationError,
    MetaConfig,
    MetaConnectorError,
    MetaGraphClient,
    MetaMalformedResponseError,
    MetaRateLimitError,
)


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


def test_meta_pagination_and_media_fields():
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
                    "paging": {"next": "https://fixture/page-2"},
                }
            )
        return response({"data": [{"id": "2"}]})

    records = MetaGraphClient(config(), transport=transport).collect(max_pages=2)
    assert [record.external_id for record in records] == ["1", "2"]
    assert records[0].media_type == "IMAGE"
    assert len(calls) == 2


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
    client = MetaGraphClient(
        config(), transport=lambda url, timeout: response(payload)
    )
    with pytest.raises(MetaMalformedResponseError):
        client.collect()


def test_invalid_json():
    client = MetaGraphClient(
        config(), transport=lambda url, timeout: (200, b"{", {})
    )
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
        return response(
            {"data": []}, status=status, headers={"Retry-After": "0.25"}
        )

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
