# Sprint 1.0 — Unified Meta Discovery Pipeline

The vertical slice accepts authorized Instagram Professional-account media and
produces validated canonical events:

`Meta collector → NormalizedSourceRecord → raw evidence → AIProvider → Event → validation → deduplication → SQLite → query`

Classification always carries a label, confidence in the inclusive range
0.0–1.0, and an evidence-based reason. The pipeline copies raw media identity
and the local evidence reference into the canonical event before persistence.
SQLite uniqueness
constraints cover both `(source, external_id)` and the semantic duplicate key.

Automated tests inject deterministic HTTP fixtures and `MockProvider`. They make
no Meta, cloud-AI, or local live-AI calls.

Local evidence defaults to `data/raw-evidence/meta`. The storage contract is
provider-neutral so a future Antoris OS integration can supply S3-compatible
storage without changing the connector or pipeline. Evidence is retained as
immutable, content-addressed JSON: recollecting changed media creates a new
artifact without replacing prior evidence, while an identical replay reuses the
same reference. Deletion follows the operator's filesystem retention policy.
Authorization headers and access tokens are recursively redacted and are never
persisted.
