# RaveHunterAI Architecture

## Vision

RaveHunterAI is an AI Event Intelligence Platform.

Instead of simply scraping event listings, the platform continuously discovers, stores, enriches and recommends electronic music and lifestyle events from multiple public sources.

Current data sources:

- Instagram
- Shotgun

Planned:

- Resident Advisor
- Eventbrite
- Facebook Events
- Club websites
- Ticket providers

---

# High Level Architecture

                Instagram
                 Shotgun
          Resident Advisor
             Eventbrite
                    │
                    ▼
              Collectors
                    │
                    ▼
          Raw Data Models
     (InstagramPost / Event)
                    │
                    ▼
            Repository Layer
               (SQLite)
                    │
                    ▼
           AI Enrichment Layer
        Classification + NLP
                    │
                    ▼
             Event Database
                    │
                    ▼
          Discovery Engine
                    │
                    ▼
 Dashboard / API / Exports

---

# Layers

## Collectors

Responsibility:

Only collect raw information.

Collectors never contain business logic.

Output:

- InstagramPost
- Event
- Raw metadata

---

## Parser

Responsibility:

Extract structured information from HTML.

Examples:

- caption
- post date
- URLs

Parsers never decide whether something is an event.

---

## Repository

Responsible for persistence.

No AI logic.

Examples:

save_post()

save_event()

get_posts()

get_events()

---

## Services

AI enrichment.

Examples:

Post classifier

Event parser

Future:

LLM enrichment

Genre detection

City detection

Duplicate detection

Confidence scoring

Recommendation scoring

---

## Database

SQLite currently.

Later:

PostgreSQL.

Tables:

instagram_posts

events

promoters

venues

artists

genres

crawl_history

---

## Dashboard

Visualisation layer.

Examples:

Today's events

Map

Calendar

Promoters

Genres

Statistics

Recommendations

---

# Design Principles

Single Responsibility

Collectors only crawl.

Parser only extracts.

Services only enrich.

Repository only persists.

Dashboard only visualises.

Every layer should be independently testable.

---

# Future Architecture

Instagram
Shotgun
Resident Advisor
Facebook
Eventbrite
Club Websites
RSS

↓

Unified Collector Interface

↓

Repository

↓

AI Processing Pipeline

↓

Knowledge Graph

↓

Recommendation Engine

↓

Dashboard

↓

REST API

↓

Mobile App