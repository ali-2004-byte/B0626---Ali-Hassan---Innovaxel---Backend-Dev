# Event Registration System API

A REST API for managing event registrations with constraints to prevent overbooking, duplicate registrations, and race conditions.

## Overview

The Event Registration System API allows users to:
- Create events with limited seat capacity and future dates
- Register for events with automatic duplicate prevention and seat availability checking
- View events with real-time seat count and filtering/sorting options
- Cancel registrations and automatically free up seats
- Export data to CSV for reporting

**Tech Stack:** Python · FastAPI · SQLite · Pydantic

## Setup

### Prerequisites
- Python 3.8+
- pip

### 1. Create Virtual Environment

```powershell
python -m venv venv

# Activate (PowerShell)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& "venv\Scripts\Activate.ps1"

# Or Bash
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn
```

### 3. Start the Server

```bash
python -m uvicorn main:app --reload
```

**API available at:** `http://127.0.0.1:8000`
- **Swagger UI (interactive docs):** `http://127.0.0.1:8000/docs`
- **Database:** `data/events.db` (auto-created)

## Key Design Decisions

- **Derived available seats** — `available_seats = total_seats - COUNT(active registrations)`. Seat count is always correct.
- **UNIQUE constraint** — `(event_id, user_name)` enforced at database level prevents duplicate registrations.
- **Atomic transactions** — `BEGIN EXCLUSIVE` wraps seat check + insert. Overbooking impossible.
- **SQLite source of truth** — CSV export is read-only presentation layer.