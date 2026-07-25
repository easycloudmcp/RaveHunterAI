# Meta connector

The connector uses the official Meta Graph API media edge in read-only mode for
configured Instagram Professional account IDs.

## Environment

- `META_ACCESS_TOKEN` — access token; required and never logged
- `META_IG_ACCOUNT_IDS` — comma-separated professional account IDs; required
- `META_GRAPH_API_VERSION` — optional, defaults to `v23.0`
- `META_TIMEOUT_SECONDS` — optional, defaults to `10`
- `META_MAX_RETRIES` — optional, defaults to `3`
- `RAVEHUNTER_DATABASE` — optional SQLite path

It retrieves `id`, `caption`, `media_type`, `media_url`, `permalink`, and
`timestamp`, follows `paging.next` up to `--max-pages`, retries timeouts, 429s,
and server errors with a bounded exponential delay, and respects `Retry-After`.
Authentication and error messages never contain tokens.

No live Meta calls run in CI. Access still requires a Meta app, an authorized
Instagram Professional account, the appropriate permissions, and a valid token.
