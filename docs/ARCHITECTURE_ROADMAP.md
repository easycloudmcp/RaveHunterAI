# RaveHunter AI -- Architecture & Roadmap

**Version:** Sprint 0.3\
**Branch:** `feature/shotgun-collector`

## Project Goal

RaveHunter AI is an event aggregation platform focused on discovering
electronic music, festivals, underground culture and related events from
multiple online sources.

The long-term pipeline is:

``` text
Internet
    ↓
Collectors (Playwright / APIs)
    ↓
Parser
    ↓
Event Dataclass
    ↓
SQLite Repository
    ↓
Search / Dashboard / AI Ranking
    ↓
Exports / API
```

The objective is to collect events once, normalize them into a common
data model, enrich them with AI, and make them searchable.

------------------------------------------------------------------------

# Current Project Structure

``` text
RaveHunterAI/
│
├── collectors/
├── config/
├── dashboard/
├── database/
├── docs/
├── exports/
├── models/
├── scheduler/
├── tests/
└── main.py
```

## collectors/

Contains one collector per event source.

Examples:

-   Shotgun
-   Resident Advisor
-   Instagram
-   Dice
-   Eventbrite

Each collector is responsible only for:

-   opening the website
-   collecting raw event information
-   returning Event objects

Collectors should **not** contain business logic or database logic.

------------------------------------------------------------------------

## database/

Responsible for persistence.

### database.py

Creates the SQLite database.

Creates tables.

Opens and closes connections.

### event_repository.py

Implements the Repository Pattern.

Responsibilities:

-   insert Event objects
-   read Event objects
-   later:
    -   update events
    -   delete events
    -   search events

The rest of the application never talks directly to SQLite.

------------------------------------------------------------------------

## models/

Contains domain objects.

Currently:

### event.py

Defines the Event dataclass.

Every collector returns this object.

Every repository stores this object.

Every dashboard displays this object.

This becomes the canonical model used throughout the application.

------------------------------------------------------------------------

## config/

Application configuration.

Examples:

-   application name
-   version
-   database location
-   API keys
-   browser settings

------------------------------------------------------------------------

## dashboard/

Reserved for the future web interface.

Possible technologies:

-   Streamlit
-   FastAPI
-   NiceGUI

------------------------------------------------------------------------

## exports/

Export formats.

Examples:

-   CSV
-   JSON
-   Excel
-   iCalendar (.ics)

------------------------------------------------------------------------

## scheduler/

Responsible for automation.

Future examples:

-   run every hour
-   nightly crawl
-   weekly refresh
-   automatic cleanup

------------------------------------------------------------------------

## tests/

Unit tests and integration tests.

Future goals:

-   parser tests
-   repository tests
-   collector tests
-   regression tests

------------------------------------------------------------------------

## main.py

Application entry point.

Current workflow:

``` text
Start
 ↓
Create Database
 ↓
Run Collector
 ↓
Create Event objects
 ↓
Store in SQLite
 ↓
Read back
 ↓
Print
```

------------------------------------------------------------------------

# Current Architecture

``` text
Playwright
      ↓
Shotgun Collector
      ↓
Event Dataclass
      ↓
Repository
      ↓
SQLite
      ↓
Console
```

------------------------------------------------------------------------

# Design Principles

-   One Event model everywhere.
-   One repository for persistence.
-   One collector per source.
-   Duplicate prevention using UNIQUE(ticket_url) and INSERT OR IGNORE.
-   Small incremental development with working software after every
    step.

------------------------------------------------------------------------

# Completed (Sprint 0.3)

-   Project structure
-   Git & GitHub workflow
-   Feature branching
-   SQLite database
-   Event dataclass
-   Repository pattern
-   Playwright integration
-   Shotgun collector
-   Duplicate protection
-   End-to-end persistence

------------------------------------------------------------------------

# Roadmap

## Sprint 0.4

Improve Shotgun parser.

Extract:

-   event name
-   venue
-   date
-   price
-   genres
-   city
-   country

Normalize dates to ISO 8601.

------------------------------------------------------------------------

## Sprint 0.5

Instagram collector.

------------------------------------------------------------------------

## Sprint 0.6

Resident Advisor collector.

------------------------------------------------------------------------

## Sprint 0.7

Additional collectors:

-   Dice
-   Eventbrite
-   Facebook Events
-   Club websites

------------------------------------------------------------------------

## Sprint 0.8

AI enrichment.

Examples:

-   recommendation score
-   travel time
-   event similarity
-   music genre classification
-   duplicate detection across websites

------------------------------------------------------------------------

## Sprint 0.9

Dashboard.

Features:

-   search
-   filtering
-   maps
-   favourites
-   export

------------------------------------------------------------------------

## Sprint 1.0

Production-ready crawler with scheduled collection, multiple sources, AI
enrichment and a searchable event database.

------------------------------------------------------------------------

# Long-Term Vision

``` text
Multiple Sources
        ↓
Collectors
        ↓
Parser
        ↓
Event Model
        ↓
Repository
        ↓
SQLite
        ↓
AI Enrichment
        ↓
Dashboard
        ↓
REST API
        ↓
Mobile App
```

The architecture is intentionally modular so that adding a new event
source requires implementing only a new collector while the rest of the
application remains unchanged.
