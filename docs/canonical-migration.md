# Canonical migration

`ravehunter.domain.Event` is the object crossing discovery, AI, validation, and
repository boundaries. Legacy `models.Event` and `InstagramPost` remain in place
for existing browser collectors.

Compatibility is explicit:

- `legacy_event_to_canonical` converts legacy Shotgun/general events.
- `instagram_post_to_source` converts browser-collected posts into normalized
  source records.

The new `canonical_events` table is intentionally separate from the legacy
`events` table. This preserves existing data and allows a later, audited data
migration. Raw source IDs and evidence URLs are retained. The current adapter
uses `Unknown venue` where legacy data has no venue and does not invent a date;
such undated records fail canonical validation.
