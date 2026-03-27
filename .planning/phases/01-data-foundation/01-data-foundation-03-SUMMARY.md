---
phase: 01-data-foundation
plan: "03"
subsystem: data-ingestion
tags: orchestration, retry, health-monitoring, prometheus, fastapi, kafka, dlq

# Dependency graph
requires:
  - phase: 01-data-foundation-01
    provides: ConflictEvent and EconomicIndicator schemas, Kafka client, configuration
  - phase: 01-data-foundation-02
    provides: SourceAdapter interface, 7 source adapters, AdapterRegistry
provides:
  - IngestionOrchestrator for polling all sources on configured intervals
  - Retry logic with exponential backoff and DLQ
  - Health tracking system with Prometheus metrics
  - FastAPI health endpoints
affects: [ml-pipeline, data-ingestion, api-layer]

# Tech tracking
tech-stack:
  added:
    - prometheus-client 0.21.x
  patterns:
    - Exponential backoff with jitter (base=1s, max=60s, base=2.0)
    - Health status thresholds (degraded=3 failures, down=10 failures)
    - Parallel polling with asyncio.gather

key-files:
  created:
    - src/ingestion/orchestrator.py - Main ingestion loop
    - src/ingestion/retry.py - Retry logic with DLQ
    - src/ingestion/health.py - Health tracking
    - src/metrics/__init__.py - Prometheus metrics
    - src/api/health.py - FastAPI health endpoints
  modified: []

key-decisions:
  - Used asyncio.gather for parallel polling of independent sources
  - Implemented DLQ pattern for permanent failures
  - Health thresholds: degraded after 3 failures, down after 10

patterns-established:
  - Ingestion orchestrator pattern with start/stop methods
  - Health tracker with status enum (HEALTHY/DEGRADED/DOWN/UNKNOWN)
  - FastAPI health endpoints returning status per source

# Metrics
duration: 20min
completed: 2026-03-27
---

# Phase 1 Plan 3: Pipeline Orchestration & Health Monitoring Summary

**Ingestion orchestrator with parallel polling, exponential backoff retry with DLQ, health tracking with Prometheus metrics, and FastAPI health endpoints for all 7 data sources**

## Performance

- **Duration:** 20 min
- **Started:** 2026-03-27T11:30:00Z
- **Completed:** 2026-03-27T11:50:00Z
- **Tasks:** 4 completed
- **Files modified:** 5

## Accomplishments

- Created IngestionOrchestrator that polls all 7 sources on their configured intervals
- Implemented retry logic with exponential backoff (base=1s, max=60s, 5 retries, 10% jitter)
- Created health tracking with SourceHealth dataclass and HealthTracker
- Built FastAPI endpoints: /health/sources, /health/kafka, /health

## Task Commits

Each task was committed atomically:

1. **Task 1: Create ingestion orchestrator** - `0415e09` (feat)
   - IngestionOrchestrator with start/stop/poll_sources methods
   - Parallel polling with asyncio.gather
   - Poll intervals: gdelt=15min, acled=6h, unhcr=12h, imf=1d, worldbank=1d, sipri=7d, un_voting=30d

2. **Task 2: Create retry logic with DLQ** - `3653318` (feat)
   - Exponential backoff: base=1s, max=60s, exponential_base=2.0, 10% jitter
   - Max retries: 5
   - DLQ handler sends to dlq.events topic with original event, error, retry_count

3. **Task 3: Create health tracking system** - `202577a` (feat)
   - SourceHealth dataclass: source, status, last_success, consecutive_failures, avg_latency_ms
   - HealthTracker with thresholds: degraded after 3 failures, down after 10
   - Prometheus metrics: source_up gauge, events_ingested counter, ingestion_latency histogram

4. **Task 4: Create health API endpoints** - `aefc143` (feat)
   - GET /health/sources: Status for all 7 sources
   - GET /health/kafka: Kafka connectivity check
   - GET /health: Overall system health

## Files Created/Modified

- `src/ingestion/orchestrator.py` - Main ingestion orchestrator with parallel polling
- `src/ingestion/retry.py` - Retry logic with exponential backoff and DLQ
- `src/ingestion/health.py` - Health tracking with SourceHealth and HealthTracker
- `src/metrics/__init__.py` - Prometheus metrics definitions
- `src/api/health.py` - FastAPI health endpoints

## Decisions Made

- Used asyncio.gather for parallel polling of independent sources
- Implemented DLQ pattern for permanent failures (invalid API keys, malformed requests)
- Health thresholds: DEGRADED after 3 consecutive failures, DOWN after 10
- Latency thresholds: DEGRADED at 5s, DOWN at 30s

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all tasks completed without issues.

## User Setup Required

**External services require manual configuration.** See [01-data-foundation-01-USER-SETUP.md](./01-data-foundation-01-USER-SETUP.md) for:
- Environment variables (DATABASE_URL, KAFKA_BOOTSTRAP_SERVERS, API keys)
- Dashboard configuration steps

## Self-Check: PASSED

- All 5 files created in src/ingestion/ and src/api/
- Task 1 committed (0415e09)
- Task 2 committed (3653318)
- Task 3 committed (202577a)
- Task 4 committed (aefc143)
- Plan metadata committed (aefc143)
- All modules import successfully

## Next Phase Readiness

- Ingestion orchestrator ready to run when adapters configured
- Health endpoints ready to expose source status
- Retry logic integrated for error handling
- Ready for Phase 2 (ML Pipeline) when complete

---
*Phase: 01-data-foundation*
*Plan: 03*
*Completed: 2026-03-27*