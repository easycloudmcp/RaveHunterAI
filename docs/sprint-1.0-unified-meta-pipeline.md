# Sprint 1.0 — Unified Meta Discovery Pipeline

The vertical slice accepts authorized Instagram Professional-account media and
produces validated canonical events:

`Meta collector → NormalizedSourceRecord → AIProvider → Event → validation → SQLite`

Classification always carries a label, confidence in the inclusive range
0.0–1.0, and an evidence-based reason. The pipeline copies raw media identity
and evidence URLs into the canonical event before persistence. SQLite uniqueness
constraints cover both `(source, external_id)` and the semantic duplicate key.

Automated tests inject deterministic HTTP fixtures and `MockProvider`. They make
no Meta, cloud-AI, or local live-AI calls.
