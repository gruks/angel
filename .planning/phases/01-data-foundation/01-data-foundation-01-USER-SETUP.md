---
phase: 01-data-foundation
plan: "01"
status: incomplete
---

# User Setup: Data Foundation - Schema & Infrastructure

External services require manual configuration before the data ingestion pipeline can function.

## Status: INCOMPLETE

The following setup tasks must be completed before proceeding to Phase 2 (ML Pipeline).

---

## Environment Variables

### Database (Required)

| Variable | Description | Example | Status |
|----------|-------------|---------|--------|
| `DATABASE_URL` | PostgreSQL/TimescaleDB connection string | `postgresql://user:pass@host:5432/db` | ❌ Required |

**Setup:**
1. Ensure PostgreSQL 17+ is running with TimescaleDB extension
2. Create a database named `conflictpulse`
3. Add `DATABASE_URL` to your environment or `.env` file

### Kafka (Required)

| Variable | Description | Example | Status |
|----------|-------------|---------|--------|
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker addresses | `localhost:9092` | ❌ Required |

**Setup:**
1. Start Kafka cluster (Docker Compose or native)
2. Ensure topics can be created (or auto-creation is enabled)
3. Add `KAFKA_BOOTSTRAP_SERVERS` to environment

### Data Source API Keys (Optional - for Phase 2)

| Variable | Source | Status |
|----------|--------|--------|
| `GDELT_API_KEY` | GDELT Cloud API | Optional |
| `ACLED_USERNAME` | ACLED API | Optional |
| `ACLED_PASSWORD` | ACLED API | Optional |
| `UNHCR_API_KEY` | UNHCR API | Optional |

**Note:** These are needed for Phase 2 (ML Pipeline) data source adapters. You can proceed without them for now.

---

## Service Setup

### PostgreSQL + TimescaleDB

```bash
# Using Docker
docker run -d \
  --name conflictpulse-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=conflictpulse \
  -p 5432:5432 \
  timescale/timescaledb:latest-pg17

# After starting, enable TimescaleDB extension
docker exec -it conflictpulse-db psql -U postgres -d conflictpulse -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
docker exec -it conflictpulse-db psql -U postgres -d conflictpulse -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### Kafka

```bash
# Using Docker Compose (recommended)
# docker-compose.yml
version: '3.8'
services:
  kafka:
    image: apache/kafka:4.2.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_LOG_DIRS: /var/lib/kafka/data
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk
```

---

## Verification Commands

After setting up, verify configuration loads correctly:

```bash
# Verify database URL (requires PostgreSQL running)
python -c "from src.config import settings; print(f'DB: {settings.database_url}')"

# Verify Kafka (requires Kafka running)
python -c "from src.config import settings; print(f'Kafka: {settings.kafka_bootstrap_servers}')"

# Verify Prisma schema
npx prisma generate

# Verify Pydantic schemas
python -c "from src.schemas.event import ConflictEvent, EventSource; print('Event schemas OK')"
python -c "from src.schemas.economic import EconomicIndicator, EconomicSource; print('Economic schemas OK')"

# Verify Kafka topics defined
python -c "from src.kafka.topics import get_topic_names; print('Topics:', get_topic_names())"
```

---

## Next Steps

1. **Complete Database Setup**: Ensure PostgreSQL with TimescaleDB is running
2. **Complete Kafka Setup**: Ensure Kafka broker is accessible
3. **Run Verification**: All verification commands should pass
4. **Proceed to Phase 2**: Once setup is complete, execute `/gsd-execute-phase 01-data-foundation-02`

---

*Phase: 01-data-foundation Plan: 01*
*Last Updated: 2026-03-27*