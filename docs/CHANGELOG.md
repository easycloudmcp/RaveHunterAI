# RaveHunterAI changelog

Project history and engineering milestones.

Last updated: 25 July 2026.

## 0.4.0-alpha — Sprint 1.0

- Added the read-only, paginated Meta Graph connector for explicitly configured
  Instagram Professional account IDs.
- Added typed Meta source records and provider-neutral raw-artifact storage with
  a token-redacting, content-addressed local filesystem adapter that retains
  changed evidence immutably.
- Added the canonical classification, extraction, validation, deduplication,
  SQLite persistence, city query, and CLI vertical slice.
- Kept legacy Shotgun and browser-based Instagram models behind explicit
  compatibility adapters.

## Unreleased — Sprint 0.9

### Goal

Transform RaveHunterAI from an event collector into an AI Event Intelligence
Platform with a canonical domain model and provider-independent AI layer.

### Milestone 1 — Canonical domain model

Completed:

- introduced the canonical `Event` aggregate
- added Venue, Location, Pricing, Schedule, Promoter, Music Profile, Media, and
  Confidence value objects
- added event lifecycle, validation, duplicate detection, and search behaviour
- adopted UTC-aware timestamps and isolated the domain from infrastructure
- added seven focused domain tests

The full deterministic suite now contains 16 passing tests when combined with
the collector and persistence tests merged into `main`.

### Milestone 2 — AI provider layer

Completed:

- defined one abstract provider contract for classification, extraction,
  enrichment, and embeddings
- added normalized classification results
- implemented a deterministic mock provider for local development and tests
- added a provider factory that defaults to the mock and rejects unavailable
  providers
- added fail-closed OpenAI, Azure OpenAI, Ollama, and LM Studio adapters
- added provider-neutral system, classification, and event-extraction prompts
- added prompt-injection boundaries and evidence-only extraction rules
- included the canonical domain package and prompt files in the wheel
- added wheel construction to the Python 3.11 and 3.13 CI matrix
- expanded the deterministic test suite to 52 passing tests

No API keys, external AI calls, live model requests, or provider costs were
introduced. Live providers remain unavailable until their individual
integration and security reviews are complete.

## 25 July 2026 — Stabilization and CI

Completed:

- merged `feature/shotgun-collector` into `main`
- restored a working database API
- aligned the SQLite schema with the event repository
- added deterministic tests for persistence, deduplication, parsing,
  classification, and Shotgun mapping
- added `pyproject.toml` and pinned dependencies
- documented a reproducible local test command
- added GitHub Actions coverage for Python 3.11 and 3.13
- passed both CI jobs before merge

Live browser collectors remain outside the automated test suite.

## Sprint 0.8 — Repository and persistence stabilization

Completed:

- redesigned the repository layer
- completed SQLite persistence for Instagram posts and events
- separated collector, parser, service, and persistence responsibilities
- removed unused database models
- documented the architecture and engineering workflow

## Sprint 0.7 — Instagram collector MVP

Completed:

- added Instagram browser and collector foundations
- implemented profile URL discovery and caption extraction
- added rule-based post classification
- added initial event parsing
- added Instagram persistence services

## Sprints 0.4–0.6 — Shotgun discovery pipeline

Completed:

- introduced Playwright browser automation
- implemented Shotgun link discovery and event mapping
- added cookie-banner handling
- connected discovery, event objects, repositories, and SQLite
- established the first end-to-end ingestion pipeline

## Sprint 0.3 — Event model and persistence

Completed:

- introduced the initial shared `Event` dataclass
- added SQLite storage
- created the first repository abstraction
- implemented event save and load operations

## Sprints 0.1–0.2 — Engineering foundation

Completed:

- created the repository and Python project structure
- established the Git workflow and development environment
- added configuration and initial documentation
- moved collector output from loose dictionaries to structured event objects

## Version 0.1.0

Initial public foundation release:

- repository and development workflow
- Python and Playwright prototype
- SQLite backend
- initial event model
- first Shotgun collector experiments

Release tag: `v0.1.0`.

## Forward plan

### Sprint 0.9

- AI provider contract and factory
- deterministic mock provider
- prompt library
- enrichment and validation pipeline
- event extraction
- confidence and cost tracking

### Sprint 1.0

- unified discovery engine
- normalized Instagram and Shotgun inputs
- additional collectors only after explicit review

### Sprint 1.1

- duplicate merging
- embeddings and semantic search
- recommendation scoring

### Later

- personal recommendations and calendar intelligence
- maps, timelines, and venue/promoter analytics
- provider-backed AI integrations
- additional website collectors
- multi-language and European expansion
