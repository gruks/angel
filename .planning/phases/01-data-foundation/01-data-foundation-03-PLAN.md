---
phase: 01-data-foundation
plan: "03"
type: execute
wave: 3
depends_on: ["01-data-foundation-01-PLAN", "01-data-foundation-02-PLAN"]
files_modified:
  - src/ingestion/orchestrator.py
  - src/ingestion/retry.py
  - src/ingestion/health.py
  - src/api/health.py
  - src/metrics/__init__.py
autonomous: false
user_setup: []

must_haves:
  truths:
    - "Ingestion orchestrator polls all sources on their configured intervals"
    - "Failed fetches trigger retry with exponential backoff"
    - "Health endpoint displays status for all 7 data sources"
    - "Normalized events published to Kafka topics"
  artifacts:
    - path: "src/ingestion/orchestrator.py"
      provides: "Main ingestion loop coordinating all adapters"
      functions: ["start_ingestion", "stop_ingestion", "poll_sources"]
    - path: "src/ingestion/retry.py"
      provides: "Retry logic with exponential backoff and DLQ"
      functions: ["fetch_with_retry", "send_to_dlq"]
    - path: "src/ingestion/health.py"
      provides: "Source health tracking and status updates"
      functions: ["SourceHealth", "HealthTracker", "update_health"]
    - path: "src/api/health.py"
      provides: "FastAPI health endpoints"
      endpoints: ["/health/sources", "/health/kafka"]
  key_links:
    - from: "src/ingestion/orchestrator.py"
      to: "src/adapters/registry.py"
      via: "Calls get_adapter() to fetch from each source"
      pattern: "adapter = get_adapter"
    - from: "src/ingestion/orchestrator.py"
      to: "src/kafka/client.py"
      via: "producer.send() publishes normalized events to Kafka"
      pattern: "await producer.send.*normalized"
    - from: "src/api/health.py"
      to: "src/ingestion/health.py"
      via: "HealthTracker provides current status"
      pattern: "health_tracker.get_all_health"
---

<objective>
Create ingestion orchestration, retry mechanisms, health monitoring, and Kafka integration. This ties all adapters together and provides operational visibility.

Purpose: Without orchestration, adapters are just code. This plan makes the data flow live and observable.
Output: Running ingestion pipeline with health monitoring
</objective>

<execution_context>
@C:/Users/HP/.config/opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/HP/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/01-data-foundation/01-data-foundation-01-SUMMARY.md
@.planning/phases/01-data-foundation/01-data-foundation-02-SUMMARY.md
@.planning/phases/01-data-foundation/01-data-foundation-RESEARCH.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create ingestion orchestrator</name>
  <files>src/ingestion/orchestrator.py</files>
  <action>
Create main ingestion orchestrator:
- Async loop that polls each source on its configured interval
- Parallel polling with asyncio.gather for independent sources
- Track last_update per source for incremental fetches
- Publish normalized events to Kafka raw topics first
- Then normalize and publish to normalized.events topic

Use the poll intervals from research: gdelt=15min, acled=6h, unhcr=12h, imf=1d, worldbank=1d, sipri=7d, un_voting=30d
  </action>
  <verify>
Run `python -c "from src.ingestion.orchestrator import IngestionOrchestrator; print('OK')"` to verify imports.
  </verify>
  <done>
Ingestion orchestrator can start/stop and poll all sources.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create retry logic with DLQ</name>
  <files>src/ingestion/retry.py</files>
  <action>
Implement retry logic per RESEARCH.md:
- Exponential backoff: base=1s, max=60s, exponential_base=2.0
- Jitter: 10% random jitter
- Max retries: 5
- Distinguish transient errors (retry) from permanent errors (DLQ)

Implement DLQ handler:
- Send failed events to dlq.events topic
- Include original message, error, timestamp, retry_count in DLQ record
- Log all retry attempts and DLQ movements
  </action>
  <verify>
Run `python -c "from src.ingestion.retry import fetch_with_retry, send_to_dlq; print('OK')"` to verify imports.
  </verify>
  <done>
Retry logic implements exponential backoff with jitter. DLQ receives permanent failures.
  </done>
</task>

<task type="auto">
  <name>Task 3: Create health tracking system</name>
  <files>src/ingestion/health.py, src/metrics/__init__.py</files>
  <action>
Create health tracking:
- SourceHealth dataclass: source, status (HEALTHY/DEGRADED/DOWN), last_success, last_failure, consecutive_failures, avg_latency_ms
- HealthTracker class: stores health in memory, updates on each fetch attempt
- Prometheus metrics: source_up gauge, events_ingested counter, ingestion_latency histogram

Store health in database for persistence (using SourceHealth model from plan 01).
  </action>
  <verify>
Run `python -c "from src.ingestion.health import SourceHealth, HealthTracker; print('OK')"` to verify imports.
  </verify>
  <done>
Health tracker monitors all sources. Prometheus metrics exported for monitoring.
  </done>
</task>

<task type="auto">
  <name>Task 4: Create health API endpoints</name>
  <files>src/api/health.py</files>
  <action>
Create FastAPI health endpoints:
- GET /health/sources: Returns health status for all 7 data sources
- GET /health/kafka: Checks Kafka connectivity, topic lag, consumer offsets
- GET /health: Overall system health (DB, Kafka, sources)

Include timestamps, latency metrics, and status details in responses.
  </action>
  <verify>
Run `python -c "from src.api.health import router; print('OK')"` to verify imports.
  </verify>
  <done>
Health endpoints accessible. /health/sources returns status for all 7 sources.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Complete data foundation: schema, adapters, orchestration, health monitoring</what-built>
  <how-to-verify>
1. Start the application and verify database schema created
2. Configure at least one data source API key in environment
3. Run ingestion and verify events flow to Kafka (if available)
4. Visit /health/sources endpoint to see source status
5. Check logs for successful ingestion events
  </how-to-verify>
  <resume-signal>Type "approved" or describe issues</resume-signal>
</task>

</tasks>

<verification>
- Ingestion orchestrator runs and polls sources
- Retry logic handles failures with backoff
- Health endpoints return source statuses
- Metrics available for Prometheus scraping
</verification>

<success_criteria>
Data flows from all configured sources through normalization to Kafka. Health monitoring displays live status. Failed events go to DLQ with retry.
</success_criteria>

<output>
After completion, create `.planning/phases/01-data-foundation/01-data-foundation-03-SUMMARY.md`
</output>
