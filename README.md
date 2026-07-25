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

feature/shotgun-collector

Current Sprint

v0.3.0 — SQLite Persistence

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

Current development

experiment/residentadvisor-persistent-profile

Research branch

---

# Roadmap

Sprint 0.5

- Parse Shotgun Event Pages
- Populate complete Event objects

Sprint 0.6

- SQLite Repository
- Event Persistence

Sprint 0.7

- Instagram Discovery

Sprint 0.8

- Facebook Events

Sprint 0.9

- In-München Collector

Sprint 1.0

- AI Enrichment
- Dashboard
- Calendar Export
- Excel Export

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
