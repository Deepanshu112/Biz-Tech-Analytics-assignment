# AI-Powered Worker Productivity Dashboard

This repository contains a full-stack web application designed to ingest, process, and display worker productivity metrics based on AI-generated computer vision events. 

## Run the Application

**Prerequisites:** Docker and Docker Compose installed.

1. Clone the repository and navigate to the project root.
2. Run `docker-compose up --build`
3. Access the application at `http://localhost:3000` or `http://localhost:80`
4. Use the "Seed/Refresh Data" button in the frontend (or explicitly call `POST /api/seed`) to populate database with meaningful mock activity data.

## 1. Architecture Overview (Edge → Backend → Dashboard)
- **Edge (CCTV + CV Model):** Cameras capture video feeds, and an edge computing node runs CV models to infer states (working, idle, absent) or counts (product). It formats these into structured JSON messages which are sent to the backend.
- **Backend (FastAPI + SQLite):** A highly concurrent async API built in Python receives these events at high throughput, validates them using Pydantic, and commits them to the database. It exposes REST endpoints for aggregation and metric computation.
- **Dashboard (React + Vite):** A responsive, rich-UI frontend fetches aggregations from the backend and visualizes real-time performance indicators (KPIs) at the factory, workstation, and worker levels.

## 2. Database Schema
- **Workers:** `id` (PK), `name`
- **Workstations:** `id` (PK), `name`, `type`
- **Events:** `id` (PK), `timestamp` (Indexed), `worker_id` (FK), `workstation_id` (FK), `event_type`, `confidence`, `count`

We store all events persistently in `Events` to allow point-in-time querying and resilient metric reconstruction. 

## 3. Metric Definitions
- **Worker Level:** 
  - *Active Time:* Sum of time between `working` event and the subsequent event.
  - *Idle Time:* Sum of time between `idle` event and the subsequent event.
  - *Utilization %:* Active Time / (Active Time + Idle Time) * 100
  - *Total Units / UPH:* Absolute sum of units produced / Total Active time evaluated in hours.
- **Workstation Level:**
  - *Occupancy Time:* Sum of active and idle time at a workstation.
  - *Throughput rate:* Units / Occupancy hours.
- **Factory Level:**
  - *Total Productive Time / Units:* Sum across all workers.

## 4. Assumptions & Tradeoffs
- **Time Difference Assumption:** Since events represent state changes, the duration spent in state X is the time difference between event X and the *next* event `timestamp` for that worker/station. If there is no next event, a default fixed interval (like 60 seconds) is assumed to prevent 0 division.
- **Tradeoff - SQL vs Compute:** Currently metrics are calculated in real-time in Python loops (`backend/metrics.py`) from raw event rows. This guarantees flexibility while drafting KPIs, but for a massive production system, these should be moved to SQL aggregations, materialized views, or time-series databases to scale better.

## Theoretical Questions

### How to Handle:
- **Intermittent Connectivity:** The Edge devices should implement a local buffer (e.g., local queue or SQLite on the edge) to store events when offline, and bulk-sync/flush to the backend when the connection restores.
- **Duplicate events:** Use an idempotency key (e.g., hash of timestamp + worker + station + event_type) or upsert mechanisms to dismiss identical events. 
- **Out-of-order timestamps:** Because the API persists all raw events and metrics are dynamically calculated by `ORDER BY timestamp` in the querying phase, delayed or out-of-order events naturally fall into their correct chronological slot when evaluating metric durations.

### ML Ops:
- **Add Model Versioning:** Every event payload sent by edge devices should contain a `model_version` tag. We store this in the event DB so we can correlate model accuracy and metrics to a specific model version.
- **Detect Model Drift:** Run periodic statistical tests on the distribution of `confidence` scores and event frequencies (e.g. if the "idle" event predictions suddenly spike by 400% or average confidence plummets from 0.95 to 0.60, raise an alert for drift).
- **Trigger Retraining:** When drift triggers an alert, sample recent video chunks, annotate them with humans conceptually, and queue an automated pipeline (e.g., Kubeflow/MLFlow) to resume training on the new data, then shadow-deploy the new model container via a registry.

### Scaling:
- **5 to 100+ Cameras:** Replace SQLite with PostgreSQL for heavy write concurrency. Introduce an asynchronous message broker (like Kafka or RabbitMQ) between Edge and Backend. The FastAPI backend becomes horizontally scaled workers consuming from Kafka to insert events simultaneously.
- **Multi-site:** Introduce a Timeseries Database specifically for metrics (e.g. TimescaleDB, Influx). Data should be tagged with `site_id`. Use a global load balancer and regional Kafka clusters so edge devices connect to their lowest-latency ingest node.