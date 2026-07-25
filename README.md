# RaveHunter AI

> AI Event Intelligence Platform for Electronic Music, Festivals, Clubs and Lifestyle Discovery

---

## Vision

RaveHunter AI is an AI-powered discovery platform that automatically finds, collects, enriches and recommends electronic music, festival, club and lifestyle events across Europe.

Instead of relying on a single event website, RaveHunter combines multiple discovery sources into one unified event database.

## Local development

RaveHunterAI requires Python 3.11 or newer. The default test suite is
deterministic and does not launch browsers or contact collector websites.

```bash
python -m venv .venv
.venv/bin/python -m pip install --requirement requirements.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation --editable .
.venv/bin/python -m pytest
```

Live collector experiments are kept separate from the automated test suite.

Current focus:

- Germany
- Austria
- Switzerland
- Northern Italy

Future expansion:

- Europe
- New Zealand
- Australia

---

# Current Status

Current Branch

feature/ai-enrichment-pipeline

Current Sprint

Sprint 1.0 — Unified Meta Discovery Vertical Slice

Latest Stable Release

v0.1.0

Development Status

🟢 Active Development

---

# Current Features

✅ Python Project

✅ Git / GitHub

✅ Version Tags

✅ SQLite Database

✅ Discovery Engine

✅ Event Domain Model

✅ Playwright Browser Automation

✅ Live Shotgun Event Discovery

Current Output

```
Running ShotgunCollector

Total events: 3

1. Munich Last Dance

2. Alceu Valença

3. Fix8...
```

---

# Planned Data Sources

## Discovery Sources

- Instagram
- Facebook Events
- In-München
- Resident Advisor
- Club Websites
- Promoters
- Festival Websites

## Ticket Sources

- Shotgun
- Eventbrite
- Dice
- Ticket.io
- Resident Advisor

---

# Architecture

```
                    Discovery Sources

Instagram
Facebook
Shotgun
Resident Advisor
Eventbrite
Dice
Ticket.io
Club Websites

            │

            ▼

      Discovery Engine

            ▼

        Event Objects

            ▼

      SQLite Repository

            ▼

       AI Enrichment

            ▼

 Dashboard / Calendar / Excel
```

---

# Project Structure

```
RaveHunterAI

collectors/
config/
database/
dashboard/
discovery/
docs/
exports/
models/
scheduler/
tests/
```

---

# Event Lifecycle

```
Website

↓

Collector

↓

Event URL

↓

Parser

↓

Event Object

↓

Repository

↓

SQLite

↓

AI Enrichment

↓

Recommendations
```

---

# Technologies

Python 3.14

Playwright

SQLite

Rich

BeautifulSoup

OpenAI API

Git

GitHub

VS Code

---

# Current Branches

main

Stable releases only

feature/shotgun-collector

Merged into main

experiment/residentadvisor-persistent-profile

Research branch

feature/ai-enrichment-pipeline

Current development

---

# Roadmap

Sprint 0.9

- Canonical Event domain model
- AI provider contract and factory
- Deterministic mock provider
- Prompt library

Sprint 1.0

- Official read-only Meta Graph API collector
- Normalized source record and canonical event pipeline
- Canonical SQLite persistence, deduplication, and query CLI

## Unified discovery CLI

All automated tests use `MockProvider`; no live AI provider is activated. The
Meta collector reads credentials only from the environment:

```powershell
$env:META_ACCESS_TOKEN = "..."
$env:META_INSTAGRAM_ACCOUNT_IDS = "1784...,1784..."
$env:RAVEHUNTER_DATABASE = "data/ravehunter.db"
python -m ravehunter.cli collect meta --max-pages 2
python -m ravehunter.cli collect shotgun
python -m ravehunter.cli events list --city "München"
python -m ravehunter.cli events show EVENT_ID
```

See `docs/meta-connector.md` for configuration and operational constraints.

---

# Long Term Vision

RaveHunter AI is not intended to become another event scraper.

The goal is to build an AI Event Intelligence Platform capable of discovering, understanding and recommending live experiences.

The platform will combine multiple discovery sources, AI analysis, recommendation engines and calendar integration into a single searchable event database.

---

# Author

Dirk Oberste-Berghaus

AI Business Analyst

Software Engineer

ICT Automation Consultant

Munich, Germany

---

# Repository

https://github.com/easycloudmcp/RaveHunterAI
