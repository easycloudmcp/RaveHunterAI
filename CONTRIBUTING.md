# Contributing to RaveHunter AI

Welcome.

This document defines the engineering principles used throughout the RaveHunter AI project.

The objective is simple:

> Build working software continuously while keeping the architecture clean and maintainable.

---

# Core Philosophy

We are **not** building another event scraper.

We are building an **AI Event Intelligence Platform**.

Every design decision should support that goal.

---

# Development Principles

## 1. Working Software First

Every sprint must end with a working application.

Never leave the project in a broken state.

---

## 2. Small Iterations

Large changes are difficult to debug.

Prefer:

- small commits
- small pull requests
- small refactorings

---

## 3. One Responsibility Per Component

Collectors discover.

Parsers extract.

Repositories store.

Discovery orchestrates.

AI enriches.

Dashboards display.

Do not mix responsibilities.

---

# Architecture

```
Discovery Sources

Instagram
Facebook
Shotgun
Resident Advisor
Dice
Eventbrite
Ticket.io
Club Websites

        │

        ▼

Collectors

        ▼

Event URLs

        ▼

Parsers

        ▼

Event Objects

        ▼

Repositories

        ▼

SQLite

        ▼

AI Enrichment

        ▼

Dashboard
Calendar
Excel
API
```

---

# Event Model

Every collector MUST return an Event object.

Never return dictionaries.

Never return tuples.

Never return raw HTML.

Good:

```python
Event(...)
```

Bad:

```python
{
    "text": "...",
    "href": "..."
}
```

---

# Collector Rules

Collectors only discover.

Collectors should:

- open websites
- collect event URLs
- perform light filtering

Collectors should NOT:

- perform AI
- enrich data
- write to SQLite
- generate reports

---

# Parser Rules

A parser receives

```
Event URL
```

and returns

```
Event
```

Parsers extract:

- Event Name
- Venue
- City
- Country
- Date
- Time
- Genres
- Price
- Ticket Link
- Description
- Organizer

---

# Repository Rules

Repositories only talk to the database.

Repositories never scrape websites.

Repositories never call AI.

---

# AI Rules

AI should only be used where it adds value.

Examples:

- Genre classification
- Dress code detection
- Flyer interpretation
- Recommendation scoring
- Duplicate detection
- Description summarisation

AI should never replace deterministic parsing when structured HTML already provides the information.

---

# Branch Strategy

```
main

Stable Releases
```

```
feature/<feature-name>

Feature Development
```

Example

```
feature/shotgun-collector

feature/instagram

feature/dashboard
```

```
experiment/<topic>

Research
```

Example

```
experiment/residentadvisor
```

---

# Commit Messages

Good

```
Sprint 0.5: Parse Shotgun event pages

Add Instagram discovery

Fix SQLite repository

Improve Event model
```

Bad

```
update

fix

stuff

changes
```

---

# Pull Requests

One feature.

One objective.

One review.

Do not combine unrelated work.

---

# Coding Style

Follow standard Python style.

Prefer readability over cleverness.

Avoid premature optimisation.

---

# Error Handling

Fail loudly.

Never silently ignore exceptions.

Log meaningful messages.

---

# Logging

Every collector should log:

```
Starting collector...

Loading page...

Found 27 event URLs

Parsed 24 events

Saved 24 events

Done.
```

---

# Testing

Every new parser should be tested against:

- one valid event
- one missing event
- one malformed page

---

# Git Workflow

Development

```
feature/*
```

↓

Commit

↓

Push

↓

Review

↓

Merge into main

↓

Tag release

---

# Versioning

Major

Architecture changes

Minor

New capabilities

Patch

Bug fixes

Example

```
v1.2.3
```

---

# Current Goal

Build the best AI Event Intelligence Platform for electronic music, festivals, club culture and lifestyle events.

The platform should become extensible enough that adding a new discovery source takes hours instead of days.

---

# Motto

> Build once.
> Discover forever.
