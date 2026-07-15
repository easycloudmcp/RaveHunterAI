Below is a proposed `HISTORY.md` for the project up to **Sprint 0.7**.

# RaveHunterAI

## HISTORY.md

Project History and Milestones

---

# Version 0.1.0

Initial public milestone.

## Completed

* Project repository created
* GitHub repository established
* Git workflow configured
* Homebrew Python environment installed
* Virtual environment configured
* VS Code development environment configured
* Feature branching introduced
* Initial project architecture created
* First tagged release
* Release tag:

  * `v0.1.0`

---

# Sprint 0.1

## Objective

Build the project foundation.

## Completed

* Repository structure
* Python project layout
* Git workflow
* Virtual environment
* Configuration folder
* Documentation folder
* Initial project planning

---

# Sprint 0.2

## Objective

Prepare the data model.

## Completed

* Designed Event data model
* Created `Event` dataclass
* Defined common event properties
* Established standard object format for all future collectors

The project transitioned from using raw dictionaries toward strongly typed Event objects.

---

# Sprint 0.3

## Objective

Build the persistence layer.

## Completed

* SQLite database introduced
* Database layer created
* Repository abstraction created
* Event persistence implemented
* Event retrieval implemented

The application gained permanent storage for discovered events.

---

# Sprint 0.4

## Objective

Build the first collector.

## Completed

* Playwright installed
* Chromium installed
* Browser automation configured
* Shotgun collector created
* Cookie handling implemented
* Initial event extraction working

The project successfully collected live event data from Shotgun.

---

# Sprint 0.5

## Objective

Improve collector architecture.

## Completed

* Collector structure standardised
* Event parsing improved
* Error handling improved
* Project folders reorganised
* Collector separation introduced

Project folders include:

* collectors
* models
* database
* repository
* dashboard
* exports
* scheduler
* tests
* docs
* config

---

# Sprint 0.6

## Objective

Integrate the complete data pipeline.

## Completed

Pipeline successfully implemented:

Shotgun

↓

Collector

↓

Event dataclass

↓

Repository

↓

SQLite

↓

Read back

↓

Console output

This was the first complete end-to-end pipeline.

The collector no longer depended on temporary in-memory data.

---

# Sprint 0.7

## Objective

Prepare the platform architecture for multiple data sources.

## Completed

* Stable Shotgun collector
* Stable SQLite persistence
* Stable repository layer
* Stable Event dataclass
* Clean feature branch
* GitHub fully synchronised
* Architecture documentation expanded
* Multi-source architecture defined
* AI Event Intelligence Platform vision established

Target discovery sources:

* Shotgun
* Instagram
* Resident Advisor (experimental)
* Facebook (planned)
* In München (planned)
* Eventbrite
* Dice
* Ticket.io

Overall platform architecture defined:

Discovery Sources

↓

Discovery Engine

↓

Event Objects

↓

Repository

↓

SQLite

↓

AI Enrichment

↓

Dashboard

↓

Calendar Export

↓

Excel Export

The project evolved from an event scraper into an AI Event Intelligence Platform.

---

# Current Status

Current branch:

`feature/shotgun-collector`

Latest stable release:

`main`

Release tag:

`v0.1.0`

---

# Next Milestones

## Sprint 0.8

* Streamlit Dashboard MVP
* View collected events
* Filtering
* Sorting

## Sprint 0.9

* Instagram collector

## Sprint 1.0

* Merge multiple collectors
* Duplicate detection

## Sprint 1.1

* AI enrichment
* Genre detection
* Recommendation scoring

## Sprint 1.2

* Personal recommendation engine

## Sprint 1.3

* Calendar exports
* ICS
* Google Calendar
* Outlook

## Sprint 1.4

* Dashboard v2
* Maps
* Timeline
* Heatmaps
* Analytics

## Sprint 2.x

AI Event Intelligence Platform

* Intelligent discovery
* Venue intelligence
* Promoter intelligence
* DJ intelligence
* Recommendation engine
* Trend prediction
* Event relationship graph
* European expansion
