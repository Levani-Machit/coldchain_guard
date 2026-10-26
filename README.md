# Coldchain Guard

A REST API for monitoring temperature-sensitive
pharmaceutical storage using Python, FastAPI,
and PostgreSQL.

## Overview

ColdChain Guard helps track storage locations,
temperature sensors, medication batches,
and temperature readings.

Each medication batch has its own permitted
temperature range. When a new temperature
reading is recorded, the system automatically
checks all batches stored in the sensor's
location and records temperature violations.

The application maintains historical readings
and provides reporting endpoints for reviewing
temperature excursions.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- Psycopg 3
- Pydantic

## Database Structure

ColdChain Guard uses five PostgreSQL tables:

- `storage_locations` — Physical locations where medications are stored.
- `sensors` — Temperature sensors assigned to storage locations.
- `batches` — Medication batches with individual temperature limits.
- `temperature_readings` — Historical temperature measurements.
- `violations` — Records of temperatures outside permitted ranges.

### Relationships

- One storage location can have multiple sensors.
- One storage location can contain multiple medication batches.
- One sensor can produce multiple temperature readings.
- One reading can generate violations for multiple batches.
- Each violation links a medication batch to a temperature reading.

## API Endpoints

### Storage Locations
- `POST /storage-locations` — Create a storage location.
- `GET /storage-locations` — List storage locations.
- `GET /storage-locations/{location_id}` — Retrieve one location.
- `PATCH /storage-locations/{location_id}` — Update a location.
- `DELETE /storage-locations/{location_id}` — Delete a location.

### Sensors
- `POST /sensors` — Register a sensor.
- `GET /sensors` — List sensors.
- `GET /sensors/{sensor_id}` — Retrieve one sensor.
- `PATCH /sensors/{sensor_id}` — Update a sensor.
- `DELETE /sensors/{sensor_id}` — Delete a sensor.

### Medication Batches
- `POST /batches` — Create a medication batch.
- `GET /batches` — List batches.
- `GET /batches/{batch_id}` — Retrieve one batch.
- `PATCH /batches/{batch_id}` — Update a batch.
- `DELETE /batches/{batch_id}` — Delete a batch.

### Temperature Readings
- `POST /readings` — Record a temperature and detect violations.
- `GET /readings` — List readings, optionally filtered by sensor.
- `GET /readings/{reading_id}` — Retrieve one reading.

### Violations and Reports
- `GET /violations` — List violations with optional filters.
- `GET /violations/{violation_id}` — Retrieve one violation.
- `GET /reports/violations` — View detailed violation reports.

## Automatic Violation Detection

When a temperature reading is submitted:

1. The API verifies that the sensor exists and is active.
2. It checks that the sensor's storage location is active.
3. It saves the temperature reading.
4. It retrieves medication batches assigned to that location.
5. It compares the reading against each batch's temperature limits.
6. It creates `too_low` or `too_high` violations where necessary.

The reading and its violations are saved in a single
database transaction. If an operation fails, the
transaction is rolled back.

Sensors with historical readings cannot be moved
to another storage location, preserving the meaning
of existing temperature records.

## Installation and Setup

### Prerequisites

- Python 3.10 or newer
- PostgreSQL
- Git

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd coldchain_guard
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and update the
database credentials.

### 5. Create the database

Create a PostgreSQL database named `coldchain_guard`.

Execute `schema.sql` against that database using
pgAdmin or another PostgreSQL client.

### 6. Start the API

From the repository root:

```bash
uvicorn coldchain_guard.main:app --reload --app-dir ..
```

### 7. Explore the API

Open:

http://127.0.0.1:8000/docs

FastAPI provides interactive Swagger documentation
for testing the endpoints.
