# RaveHunter AI

# Architecture Decision Log (ADR)

---

# ADR-0001

Date

2026-07-11

Status

Accepted

Title

RaveHunter is an AI Event Intelligence Platform

Decision

The project is not an event scraper.

It is an AI Event Intelligence Platform capable of discovering, understanding, enriching and recommending electronic music and lifestyle events.

Reason

Scrapers collect data.

Platforms create knowledge.

Consequence

Every architectural decision must support long-term intelligence rather than one-off scraping.

---

# ADR-0002

Date

2026-07-11

Status

Accepted

Title

Collectors return Event objects

Decision

All collectors return Event domain objects.

Never dictionaries.

Reason

A unified domain model allows every downstream component to operate independently of the original data source.

Consequence

Dashboard

SQLite

AI

Calendar

Excel

API

all consume exactly the same Event object.

---

# ADR-0003

Date

2026-07-11

Status

Accepted

Title

Discovery separated from Parsing

Decision

Collectors discover.

Parsers extract.

Reason

Finding an event URL and understanding an event page are two different responsibilities.

Consequence

Every collector becomes simpler.

Every parser becomes reusable.

---

# ADR-0004

Date

2026-07-11

Status

Accepted

Title

Playwright chosen over Requests

Decision

Modern event platforms use JavaScript rendering and anti-bot protection.

Playwright is the default browser engine.

Reason

One browser automation framework can support almost every collector.

Consequence

Instagram

Shotgun

Resident Advisor

Facebook

Dice

Ticket.io

share the same automation layer.

---

# ADR-0005

Date

2026-07-11

Status

Accepted

Title

Git Feature Branch Workflow

Decision

Development occurs on feature branches.

main remains stable.

Reason

Never break the stable release.

Consequence

Experiments remain isolated.

Releases remain reproducible.

---

# ADR-0006

Date

2026-07-11

Status

Accepted

Title

SQLite first

Decision

The first persistence layer is SQLite.

Reason

Fast development.

No external infrastructure.

Easy local debugging.

Consequence

Migration to PostgreSQL remains possible later.

---

# ADR-0007

Date

2026-07-11

Status

Accepted

Title

One Collector Interface

Decision

Every collector implements exactly one public method.

```python
collect()
```

Reason

Simple orchestration.

Predictable behaviour.

Easy testing.

Consequence

Discovery Engine can execute collectors without knowing implementation details.

---

# ADR-0008

Date

2026-07-11

Status

Accepted

Title

One Responsibility per Module

Decision

Each module has one responsibility.

Collectors

Discover URLs

Parsers

Extract Event information

Repositories

Persist data

AI

Enrich Event data

Dashboard

Present data

Reason

Lower coupling.

Higher maintainability.

---

# ADR-0009

Date

2026-07-11

Status

Accepted

Title

AI is an enrichment layer

Decision

AI is not used for information already available through deterministic parsing.

AI is reserved for tasks where it genuinely improves results.

Examples

Genre detection

Recommendation scoring

Flyer interpretation

Dress code detection

Duplicate detection

Reason

Deterministic data is more reliable than LLM inference.

---

# ADR-0010

Date

2026-07-11

Status

Accepted

Title

Discovery before Intelligence

Decision

The project will first discover events reliably.

AI recommendations come later.

Reason

Poor input produces poor recommendations.

Reliable discovery is the foundation of intelligent recommendations.

---

# ADR-0011

Date

2026-07-11

Status

Accepted

Title

Source Independence

Decision

The platform must never depend on a single provider.

Reason

Websites change.

Anti-bot measures evolve.

Services disappear.

Consequence

Multiple discovery sources ensure resilience.

---

# ADR-0012

Date

2026-07-11

Status

Accepted

Title

Discovery Sources and Ticket Sources are different

Decision

The system distinguishes between:

Discovery Sources

Instagram

Facebook

In-München

Resident Advisor

Promoters

Club websites

Ticket Sources

Shotgun

Eventbrite

Dice

Ticket.io

Reason

Discovery identifies opportunities.

Ticket platforms provide structured purchase data.

Consequence

Different collectors can complement each other instead of competing.

---

# ADR-0013

Date

2026-07-11

Status

Accepted

Title

Architecture evolves from working software

Decision

Functionality is implemented first.

Architecture is refactored after successful proof of concept.

Reason

Avoid premature abstraction.

Consequence

Every sprint produces visible progress while steadily improving code quality.

---

# Future Decisions

Reserve this section for future ADRs.

Examples

PostgreSQL migration

Distributed crawling

Vision AI

OCR strategy

Recommendation engine

Graph database

Mobile application

Cloud deployment

Vector search

Local LLM support