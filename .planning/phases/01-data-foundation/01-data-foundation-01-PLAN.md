---
phase: 01-data-foundation
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - prisma/schema.prisma
  - src/db/models.py
  - src/schemas/event.py
  - src/config.py
  - src/kafka/topics.py
autonomous: true
user_setup:
  - service: kafka
    why: "Event streaming backbone"
    env_vars:
      - name: KAFKA_BOOTSTRAP_SERVERS
        source: "Kafka broker configuration"
  - service: timescale
    why: "Time-series database for events"
    env_vars:
      - name: DATABASE_URL
        source: "PostgreSQL/TimescaleDB connection string"

must_haves:
  truths:
    - "Database schema exists for normalized events and indicators"
    - "Kafka topics created for raw and normalized event streams"
    - "Application can connect to both Kafka and TimescaleDB"
  artifacts:
    - path: "prisma/schema.prisma"
      provides: "Database schema for conflict events, economic indicators"
      contains: "model ConflictEvent"
    - path: "src/schemas/event.py"
      provides: "Pydantic models for normalized event schema"
      exports: ["ConflictEvent", "EconomicIndicator", "EventSource"]
    - path: "src/kafka/topics.py"
      provides: "Kafka topic creation and management"
      functions: ["create_topics", "get_topic_names"]
  key_links:
    - from: "src/schemas/event.py"
      to: "prisma/schema.prisma"
      via: "Pydantic → SQLAlchemy → Prisma mapping"
      pattern: "class ConflictEvent.*BaseModel"
---

<objective>
Create database schema, event schemas, and Kafka topic infrastructure. This is the foundational layer that all data source adapters depend on.

Purpose: Without database schema and Kafka topics, no data can be stored or streamed. This plan establishes the foundation.
Output: Prisma schema, Pydantic event models, Kafka topic definitions
</objective>

<execution_context>
@C:/Users/HP/.config/opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/HP/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/research/STACK.md
@.planning/research/ARCHITECTURE.md
@.planning/phases/01-data-foundation/01-data-foundation-RESEARCH.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create database schema for events and indicators</name>
  <files>prisma/schema.prisma, src/db/models.py</files>
  <action>
Create Prisma schema with:
- ConflictEvent model: event_id, source, event_date, latitude, longitude, country_iso, country_name, disorder_type, event_type, sub_event_type, actor1, actor2, fatalities, confidence, goldstein_scale, tone, raw_data, created_at, updated_at
- EconomicIndicator model: indicator_id, source, country_iso, country_name, year, value, unit, raw_data, created_at
- SourceHealth model: source, status, last_success, last_failure, consecutive_failures, avg_latency_ms, created_at, updated_at
- Enable TimescaleDB hypertables and PostGIS extensions

Use UUID for primary keys, timestamps with createdAt/updatedAt pattern.
  </action>
  <verify>
Run `npx prisma generate` to validate schema syntax, then `npx prisma db push` to create tables in dev database.
  </verify>
  <done>
Database tables exist: ConflictEvent, EconomicIndicator, SourceHealth. TimescaleDB hypertable enabled on ConflictEvent.event_date.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create Pydantic event schemas for normalization</name>
  <files>src/schemas/event.py, src/schemas/economic.py</files>
  <action>
Create Pydantic models matching the RESEARCH.md common event schema:
- EventSource enum: GDELT, ACLED, UNHCR, UN_VOTING, ECONOMIC, SIPRI
- DisorderType enum: POLITICAL_VIOLENCE, PROTEST, STRATEGIC_DEVELOPMENTS, DEMOGRAPHICS
- ConflictEvent model with all fields from schema (event_id, source, event_date, location fields, classification, actors, severity, source-specific metadata)
- EconomicIndicator model matching research schema

Use Optional for nullable fields, datetime for timestamps, validation on required fields.
  </verify>
  <verify>
Run `python -c "from src.schemas.event import ConflictEvent, EventSource; print('OK')"` to validate imports.
  </verify>
  <done>
Pydantic models imported successfully. EventSource and ConflictEvent classes available.
  </done>
</task>

<task type="auto">
  <name>Task 3: Create Kafka topic definitions and bootstrap</name>
  <files>src/kafka/topics.py, src/kafka/client.py</files>
  <action>
Create Kafka topic management:
- Topic names: raw.events.gdelt, raw.events.acled, raw.events.unhcr, normalized.events, enriched.events, dlq.events
- Partition strategy: source + country + day
- Retention: 7 days for raw, 90 days for normalized/enriched, 7 days for DLQ

Create Kafka client wrapper using aiokafka:
- AIOKafkaProducer for publishing events
- AIOKafkaConsumer for consuming
- Connection configuration via KAFKA_BOOTSTRAP_SERVERS env var
  </action>
  <verify>
Run `python -c "from src.kafka.topics import get_topic_names; print(get_topic_names())"` to verify topic names exported.
  </verify>
  <done>
Kafka topics defined. Client wrapper can connect to broker (will verify in later plan when Kafka is available).
  </done>
</task>

<task type="auto">
  <name>Task 4: Create configuration management</name>
  <files>src/config.py</files>
  <action>
Create FastAPI configuration:
- Database URL from DATABASE_URL env var
- Kafka bootstrap servers from KAFKA_BOOTSTRAP_SERVERS env var
- Source API keys from environment (GDELT_API_KEY, ACLED_* etc)
- Poll intervals per source (matching RESEARCH.md: gdelt=15min, acled=6h, unhcr=12h, imf=1d, etc)

Use pydantic-settings for configuration management.
  </action>
  <verify>
Run `python -c "from src.config import settings; print(settings.database_url)"` to verify config loads.
  </verify>
  <done>
Configuration loads from environment variables. All required settings present.
  </done>
</task>

</tasks>

<verification>
- Prisma schema generates without errors
- Pydantic models import correctly
- Kafka topic names are defined
- Configuration loads from environment
</verification>

<success_criteria>
Database schema exists and can be created. Event schemas match research specifications. Kafka topic infrastructure ready for adapters.
</success_criteria>

<output>
After completion, create `.planning/phases/01-data-foundation/01-data-foundation-01-SUMMARY.md`
</output>
