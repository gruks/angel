# Phase 1: Data Foundation - Research

**Researched:** 2026-03-27  
**Domain:** Data ingestion, normalization, and event streaming for conflict prediction  
**Confidence:** MEDIUM-HIGH

## Summary

This phase establishes the data foundation for ConflictPulse by implementing ingestion pipelines for 7 external data sources plus internal normalization and Kafka event bus. Key findings:

1. **External APIs vary significantly** - Some have robust APIs (ACLED, World Bank, GDELT), others require scraping or have limited access (SIPRI, UN voting)
2. **Common event schema is essential** - Use CAMEO-based taxonomy for conflict events, standardize economic indicators separately
3. **Kafka with Schema Registry** - Required for reliable event streaming with schema evolution
4. **Retry + DLQ pattern** - Critical for handling rate limits and transient failures from external APIs
5. **15-minute latency achievable** - With async HTTP clients and efficient polling intervals

**Primary recommendation:** Build modular source adapters with a unified normalization layer, using Kafka as the backbone for event distribution.

---

## User Constraints

*No CONTEXT.md exists - this phase has full research discretion.*

---

## Standard Stack

### Core Libraries
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `httpx` | Latest | Async HTTP client | Required for concurrent API polling across 7 sources |
| `aiokafka` | Latest | Async Kafka client | Python-native async consumer/producer for real-time streaming |
| `tenacity` | Latest | Retry logic | Standard for exponential backoff, circuit breaker patterns |
| `fastapi` | 0.135.x | API framework | Health endpoints, configuration management |
| `pydantic` | 2.9+ | Data validation | Schema validation for external API responses |

### Supporting Libraries
| Library | Purpose | When to Use |
|---------|---------|-------------|
| `psycopg2-binary` / `asyncpg` | PostgreSQL drivers | TimescaleDB connection |
| `python-dotenv` | Configuration | API key management |
| `prometheus-client` | Metrics | Health monitoring |
| `structlog` | Structured logging | Ingestion logs |

**Installation:**
```bash
pip install httpx aiokafka tenacity fastapi pydantic asyncpg psycopg2-binary python-dotenv prometheus-client structlog
```

---

## Data Source Integration

### Source 1: GDELT (Global Database of Events, Language and Tone)

| Aspect | Details |
|--------|---------|
| **API Endpoint** | `https://gdeltcloud.com/api/v1/media-events` |
| **Authentication** | Bearer token (API key format: `gdelt_sk_*`) |
| **Data Format** | JSON with CAMEO event codes |
| **Update Frequency** | Hourly |
| **Rate Limits** | Per-plan (Analyst/Professional) |
| **Key Fields** | `cluster_id`, `event_type`, `actor1/actor2`, `location`, `tone`, `goldstein` |

**Integration Pattern:**
```python
# Source: GDELT Cloud API Documentation
import httpx

async def fetch_gdelt_events(days: int = 1, limit: int = 50):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://gdeltcloud.com/api/v1/media-events",
            params={"days": days, "limit": limit},
            headers={"Authorization": f"Bearer {GDELT_API_KEY}"}
        )
        return response.json()["clusters"]
```

**Notes:**
- Requires paid plan for API access
- Data starts from January 2025, expanding historically
- Supports semantic search via embeddings
- Use `days=1` for real-time streaming, `days=7` for batch backfill

---

### Source 2: ACLED (Armed Conflict Location & Event Data)

| Aspect | Details |
|--------|---------|
| **API Endpoint** | `https://acleddata.com/api/acled/read` |
| **Authentication** | OAuth 2.0 password flow (requires myACLED account) |
| **Data Format** | JSON/CSV with structured event data |
| **Update Frequency** | Daily updates (varies by region) |
| **Rate Limits** | Per-account (request-based, not explicit RPM) |
| **Key Fields** | `event_id_cnty`, `event_date`, `event_type`, `actor1`, `actor2`, `fatalities`, `latitude`, `longitude` |

**Integration Pattern:**
```python
# Source: ACLED API Documentation (adapted)
import httpx
from datetime import datetime, timedelta

async def get_acled_token(username: str, password: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://acleddata.com/oauth/token",
            data={
                "username": username,
                "password": password,
                "grant_type": "password",
                "client_id": "acled"
            }
        )
        return response.json()["access_token"]

async def fetch_acled_events(token: str, country: str, year: int = 2026):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://acleddata.com/api/acled/read?_format=json",
            params={"country": country, "year": year},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()["data"]
```

**Notes:**
- Requires registration and may have data access restrictions
- Supports both dyadic and monadic export formats
- Numeric codes for regions/interactions need translation (see ACLED codebook)
- Good for conflict event validation and ground truth

---

### Source 3: IMF (International Monetary Fund)

| Aspect | Details |
|--------|---------|
| **API Endpoint** | `https://dataservices.imf.org/REST/SDMX_JSON.svc` |
| **Authentication** | None (public data) |
| **Data Format** | SDMX-JSON |
| **Update Frequency** | Varies by indicator (monthly/quarterly) |
| **Rate Limits** | Not publicly documented, recommend polite polling |
| **Key Indicators** | GDP, inflation, current account, reserves, unemployment |

**Integration Pattern:**
```python
# Source: IMF API Documentation
import httpx

IMF_INDICATORS = {
    "gdp": "NGDPD",  # GDP Current Prices
    "inflation": "FPICPI",  # Consumer Price Index
    "unemployment": "LUR":  # Unemployment Rate
}

async def fetch_imf_indicator(indicator: str, country: str = "USA"):
    async with httpx.AsyncClient() as client:
        # Compact data endpoint
        url = f"https://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/{indicator}.{country}"
        response = await client.get(url)
        return response.json()
```

**Notes:**
- SDMX format requires parsing; consider using `pandasdmx` library
- Historical data goes back decades
- Some indicators have lags of several months
- Good for economic stress indicators (inflation spikes, GDP contraction)

---

### Source 4: World Bank

| Aspect | Details |
|--------|---------|
| **API Endpoint** | `https://api.worldbank.org/v2` |
| **Authentication** | None (public data) |
| **Data Format** | JSON |
| **Update Frequency** | Annually (most indicators) |
| **Rate Limits** | Reasonable limits, polite caching recommended |
| **Key Indicators** | Population, GDP per capita, trade, military expenditure |

**Integration Pattern:**
```python
# Source: World Bank API Documentation
import httpx

async def fetch_worldbank_indicator(indicator: str, country: str = "all", date: str = "2020:2025"):
    async with httpx.AsyncClient() as client:
        url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
        params = {"format": "json", "date": date, "per_page": 500}
        response = await client.get(url, params=params)
        data = response.json()
        # First element is metadata, second is data array
        return data[1] if len(data) > 1 else []
```

**Common Indicators:**
- `SP.POP.TOTL` - Total population
- `NY.GDP.PCAP.CD` - GDP per capita
- `MS.MIL.XPND.GD.ZS` - Military expenditure (% of GDP)
- `NE.EXP.GNFS.ZS` - Exports (% of GDP)

---

### Source 5: SIPRI (Stockholm International Peace Research Institute)

| Aspect | Details |
|--------|---------|
| **API Endpoint** | No official API |
| **Data Access** | Web interface + CSV download |
| **Alternative** | PyPI package `sipri` (unofficial), GitHub scrapers |
| **Data Format** | CSV (manual download or scraping) |
| **Update Frequency** | Annual (arms trade database) |

**Integration Pattern:**
```python
# Option 1: Use sipri PyPI package (unofficial)
# pip install sipri

# Option 2: Manual CSV download + parse
# URL: https://armstrade.sipri.org/armstrade/page/trade_register.php
# Use BeautifulSoup for web scraping if needed
```

**Notes:**
- No official API - treat as batch/scrape source
- Primary value: arms transfer trends (weapons, military equipment)
- Data available as CSV for manual download
- Consider building a periodic Airflow DAG to fetch latest data

---

### Source 6: UN Voting Records

| Aspect | Details |
|--------|---------|
| **API Endpoint** | `https://unvoting.org/API` (UN Voting Data Initiative) |
| **Alternative** | Princeton's `unvotes` R package, UN Digital Library |
| **Authentication** | None (public data) |
| **Data Format** | JSON |
| **Update Frequency** | Per UN General Assembly session |

**Integration Pattern:**
```python
# Source: UN Voting Data Initiative
import httpx

async def fetch_un_votes(session: int = 79):
    async with httpx.AsyncClient() as client:
        # Get all votes for a session
        url = f"https://unvoting.org/API/session/{session}"
        response = await client.get(url)
        return response.json()
```

**Notes:**
- Good for diplomatic tension indicators
- Voting alignment between countries can signal alliances/hostilities
- Alternative: Princeton's data dump (more comprehensive historical)
- Good for batch processing, not real-time

---

### Source 7: UNHCR (Refugee Statistics)

| Aspect | Details |
|--------|---------|
| **API Endpoint** | `https://api.unhcr.org/docs/refugee-statistics.html` |
| **Authentication** | None for public endpoints, registration for some datasets |
| **Data Format** | JSON |
| **Update Frequency** | Monthly |
| **Key Data** | Refugee populations, asylum applications, resettlement |

**Integration Pattern:**
```python
# Source: UNHCR API Documentation
import httpx

async def fetch_refugee_stats(country: str = "VEN", year: int = 2025):
    async with httpx.AsyncClient() as client:
        # UNHCR Population Statistics API
        url = "https://api.unhcr.org/population/v1/refugees/"
        params = {"country": country, "year": year}
        response = await client.get(url, params=params)
        return response.json()
```

**Notes:**
- Good for displacement crises indicator
- Track refugee flows as leading indicator for conflict escalation
- Registration may be required for full dataset access

---

## Data Normalization

### Common Event Schema Design

The normalization layer transforms heterogeneous source data into a unified schema. Based on ACLED's CAMEO-derived taxonomy:

```python
# Source: Adapted from ARCHITECTURE.md Pattern 1
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class EventSource(str, Enum):
    GDELT = "gdelt"
    ACLED = "acled"
    UNHCR = "unhcr"
    UN_VOTING = "un_voting"
    ECONOMIC = "economic"  # IMF + World Bank
    SIPRI = "sipri"

class DisorderType(str, Enum):
    POLITICAL_VIOLENCE = "political_violence"
    PROTEST = "protest"
    STRATEGIC_DEVELOPMENTS = "strategic_developments"
    DEMOGRAPHICS = "demographics"  # refugee flows

class ConflictEvent(BaseModel):
    # Primary identifiers
    event_id: str  # Source-specific ID + source prefix
    source: EventSource
    event_date: datetime
    ingestion_timestamp: datetime
    
    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_iso: Optional[str] = None
    country_name: Optional[str] = None
    admin_region: Optional[str] = None
    
    # Event classification
    disorder_type: Optional[DisorderType] = None
    event_type: Optional[str] = None
    sub_event_type: Optional[str] = None
    
    # Actors (if applicable)
    actor1: Optional[str] = None
    actor2: Optional[str] = None
    
    # Severity
    fatalities: Optional[int] = 0
    confidence: Optional[float] = 1.0
    
    # Source-specific metadata preserved for audit
    raw_data: dict
    
    # Computed fields for conflict prediction
    goldstein_scale: Optional[float] = None  # -10 to +10
    tone: Optional[float] = None  # negative = negative
```

### Economic Indicator Schema

```python
class EconomicIndicator(BaseModel):
    indicator_id: str  # e.g., "GDP", "INFLATION", "REFUGEES"
    source: str  # "imf" or "worldbank"
    country_iso: str
    year: int
    value: float
    unit: str
    ingestion_timestamp: datetime
    raw_data: dict
```

---

## Kafka Architecture

### Topic Design

| Topic | Purpose | Partition Strategy | Retention |
|-------|---------|-------------------|-----------|
| `raw.events.gdelt` | Raw GDELT events | By source region | 7 days |
| `raw.events.acled` | Raw ACLED events | By country | 30 days |
| `raw.events.unhcr` | Raw UNHCR refugee stats | By origin country | 30 days |
| `normalized.events` | Normalized events | By event_type + country | 90 days |
| `enriched.events` | ML-enriched events | By risk_score | 90 days |
| `dlq.events` | Dead letter queue | Single partition | 7 days |

### Partitioning Strategy

```python
# Partition by composite key: source + country + day
# This ensures ordering within source-country-day while enabling parallelism

def get_partition_key(event: ConflictEvent) -> str:
    day = event.event_date.strftime("%Y-%m-%d")
    return f"{event.source.value}:{event.country_iso or 'XXX'}:{day}"
```

### Schema Registry

Use **Confluent Schema Registry** with Avro serialization:

```python
# Source: Confluent Schema Registry Documentation
# Schema evolution strategy: BACKWARD (consumers can read old and new)

{
  "type": "record",
  "name": "ConflictEvent",
  "namespace": "conflictpulse.events",
  "fields": [
    {"name": "event_id", "type": "string"},
    {"name": "source", "type": {"type": "enum", "symbols": ["gdelt", "acled", "unhcr"]}},
    {"name": "event_date", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    {"name": "latitude", "type": ["null", "double"], "default": null},
    {"name": "longitude", "type": ["null", "double"], "default": null},
    {"name": "country_iso", "type": ["null", "string"], "default": null},
    {"name": "disorder_type", "type": ["null", "string"], "default": null},
    {"name": "event_type", "type": ["null", "string"], "default": null},
    {"name": "actor1", "type": ["null", "string"], "default": null},
    {"name": "actor2", "type": ["null", "string"], "default": null},
    {"name": "fatalities", "type": "int", "default": 0},
    {"name": "confidence", "type": "double", "default": 1.0},
    {"name": "raw_data", "type": "string"}  # JSON string
  ]
}
```

### Producer/Consumer Pattern

```python
# Source: aiokafka documentation
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json

# Producer
producer = AIOKafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

async def produce_event(topic: str, event: dict):
    await producer.send_and_wait(topic, event)

# Consumer
consumer = AIOKafkaConsumer(
    "normalized.events",
    bootstrap_servers="localhost:9092",
    group_id="ingestion-consumer-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

async def consume_events():
    await consumer.start()
    try:
        async for msg in consumer:
            process_event(msg.value)
    finally:
        await consumer.stop()
```

---

## Health Monitoring

### Connection Status Tracking

```python
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import structlog

logger = structlog.get_logger()

class SourceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"

@dataclass
class SourceHealth:
    source: str
    status: SourceStatus
    last_success: datetime
    last_failure: Optional[datetime]
    consecutive_failures: int
    avg_latency_ms: float
    
    def is_healthy(self) -> bool:
        return self.status == SourceStatus.HEALTHY

# Health check pattern
async def check_source_health(source: str, fetch_fn) -> SourceHealth:
    start = datetime.now()
    try:
        await asyncio.wait_for(fetch_fn(), timeout=10.0)
        latency = (datetime.now() - start).total_seconds() * 1000
        return SourceHealth(
            source=source,
            status=SourceStatus.HEALTHY,
            last_success=datetime.now(),
            last_failure=None,
            consecutive_failures=0,
            avg_latency_ms=latency
        )
    except Exception as e:
        logger.error(f"Health check failed for {source}", error=str(e))
        return SourceHealth(
            source=source,
            status=SourceStatus.DOWN,
            last_success=None,
            last_failure=datetime.now(),
            consecutive_failures=1,
            avg_latency_ms=0
        )
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
events_ingested = Counter(
    "conflictpulse_events_ingested_total",
    "Total events ingested",
    ["source", "status"]
)

ingestion_latency = Histogram(
    "conflictpulse_ingestion_latency_seconds",
    "Time to ingest and process events",
    ["source"]
)

source_up = Gauge(
    "conflictpulse_source_up",
    "Whether source is currently reachable",
    ["source"]
)
```

---

## Retry Mechanisms

### Exponential Backoff with Jitter

```python
# Source: tenacity / httpx-retries patterns
import asyncio
import random

async def fetch_with_retry(
    fetch_fn,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
):
    """Fetch with exponential backoff and jitter."""
    for attempt in range(max_retries):
        try:
            return await fetch_fn()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Calculate delay with jitter
            delay = min(base_delay * (exponential_base ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)  # 10% jitter
            total_delay = delay + jitter
            
            logger.warning(
                f"Fetch failed, retrying in {total_delay:.2f}s",
                attempt=attempt + 1,
                error=str(e)
            )
            await asyncio.sleep(total_delay)
```

### Dead Letter Queue (DLQ) Pattern

```python
# Source: Kafka DLQ best practices
async def process_with_dlq(consumer, producer, dlq_topic: str):
    """Process messages with DLQ fallback."""
    async for msg in consumer:
        try:
            event = parse_event(msg.value)
            await process_event(event)
        except TransientError as e:
            # Retry with backoff - could use Kafka consumer retry
            logger.warning(f"Transient error, will retry", error=str(e))
            raise  # Let consumer handle retry
        except PermanentError as e:
            # Send to DLQ
            logger.error(f"Permanent error, sending to DLQ", error=str(e))
            await producer.send(
                dlq_topic,
                value={
                    "original_message": msg.value,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "retry_count": msg.headers.get("retry_count", 0)
                }
            )
        except Exception as e:
            # Unexpected error - send to DLQ
            logger.exception(f"Unexpected error, sending to DLQ")
            await producer.send(dlq_topic, value=msg.value)
```

---

## Architecture Patterns

### Ingestion Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ GDELT        │  │ ACLED        │  │ UNHCR        │  │ IMF/WorldBank  │  │
│  │ Adapter      │  │ Adapter      │  │ Adapter      │  │ Adapter        │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                 │                 │                  │          │
│         ▼                 ▼                 ▼                  ▼          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    NORMALIZATION LAYER                                │  │
│  │  - Schema transformation                                              │  │
│  │  - CAMEO code mapping                                                 │  │
│  │  - Deduplication                                                     │  │
│  └──────────────────────────────┬───────────────────────────────────────┘  │
│                                 │                                            │
│                                 ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    KAFKA EVENT BUS                                     │  │
│  │  - Topic: normalized.events                                           │  │
│  │  - Schema Registry (Avro)                                             │  │
│  │  - DLQ: dlq.events                                                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                 │                                            │
│                                 ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    STORAGE LAYER                                       │  │
│  │  - TimescaleDB (time-series events)                                  │  │
│  │  - PostGIS (geospatial)                                              │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pattern: Polling + Push Hybrid

- **Real-time sources (GDELT)**: Poll every 15-60 minutes
- **Daily sources (ACLED)**: Poll daily, track last-update timestamp
- **Batch sources (SIPRI, Economic)**: Airflow DAG for periodic sync

```python
# Polling scheduler example
import asyncio
from datetime import datetime, timedelta

POLL_INTERVALS = {
    "gdelt": timedelta(minutes=15),
    "acled": timedelta(hours=6),
    "unhcr": timedelta(hours=12),
    "imf": timedelta(days=1),
    "worldbank": timedelta(days=1),
    "sipri": timedelta(days=7),  # Batch via Airflow
    "un_voting": timedelta(days=30)
}

async def ingestion_loop(sources: list[str]):
    while True:
        for source in sources:
            try:
                await poll_source(source)
            except Exception as e:
                logger.error(f"Polling failed for {source}", error=str(e))
        
        await asyncio.sleep(60)  # Check every minute which sources need polling
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP retry logic | Custom exponential backoff | `tenacity` or `httpx-retry` | Handles edge cases: jitter, circuit breaker, retry conditions |
| Event serialization | JSON strings | Confluent Schema Registry + Avro | Schema evolution, backward compatibility, compact encoding |
| Connection pooling | Manual socket management | `httpx.AsyncClient` | Connection reuse, timeouts, HTTP/2 support |
| Kafka consumer | threading.Thread | `aiokafka` | True async, proper offset management |
| JSON parsing | json module | `orjson` or `ujson` | 3-10x faster for high-volume ingestion |

---

## Common Pitfalls

### Pitfall 1: Rate Limit Aggressive Polling
**What goes wrong:** API access gets throttled or blocked
**Why it happens:** Polling too frequently, no backoff on 429 responses
**How to avoid:** 
- Implement exponential backoff on rate limit errors
- Cache etag/last-modified headers
- Use async with connection pooling to be polite

### Pitfall 2: Schema Evolution Without Compatibility
**What goes wrong:** New fields break existing consumers
**Why it happens:** Adding required fields without default values
**How to avoid:**
- Always use Avro with schema registry
- Set backward compatibility: add optional fields only
- Version schemas explicitly

### Pitfall 3: Inconsistent Event IDs
**What goes wrong:** Duplicate events after restart
**Why it happens:** Source-specific IDs conflict or aren't unique enough
**How to avoid:**
- Prefix event IDs with source: `gdelt:{cluster_id}`, `acled:{event_id}`
- Use composite key: source + original_id + event_date

### Pitfall 4: Ignoring Data Quality at Ingestion
**What goes wrong:** Bad data pollutes entire pipeline
**Why it happens:** No validation on incoming data before Kafka
**How to avoid:**
- Validate against schema at ingestion layer
- Track data quality metrics (null rates, malformed records)
- Route bad data to DLQ, not main topic

### Pitfall 5: Synchronous Batch Processing
**What goes wrong:** Pipeline can't keep up with real-time
**Why it happens:** Using synchronous requests in loops
**How to avoid:**
- Use `httpx.AsyncClient` with `asyncio.gather` for parallel fetches
- Process events in batches, not one-by-one

---

## Code Examples

### Complete Ingestion Adapter Pattern

```python
# Source: Adapted from patterns above
from abc import ABC, abstractmethod
from typing import AsyncIterator
import asyncio

class SourceAdapter(ABC):
    """Base class for all data source adapters."""
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def poll_interval(self) -> timedelta:
        pass
    
    @abstractmethod
    async def fetch_new_events(self, last_update: datetime) -> list[dict]:
        """Fetch events newer than last_update."""
        pass
    
    @abstractmethod
    def normalize(self, raw_event: dict) -> ConflictEvent:
        """Convert raw source event to normalized schema."""
        pass

class GDELTAdapter(SourceAdapter):
    source_name = "gdelt"
    poll_interval = timedelta(minutes=15)
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def fetch_new_events(self, last_update: datetime) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://gdeltcloud.com/api/v1/media-events",
                params={"days": 1, "limit": 50},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json().get("clusters", [])
    
    def normalize(self, raw_event: dict) -> ConflictEvent:
        return ConflictEvent(
            event_id=f"gdelt:{raw_event['cluster_id']}",
            source=EventSource.GDELT,
            event_date=datetime.fromisoformat(raw_event["time_bucket"]),
            latitude=raw_event.get("resolved_metrics", {}).get("primary_location", {}).get("lat"),
            longitude=raw_event.get("resolved_metrics", {}).get("primary_location", {}).get("long"),
            country_name=raw_event.get("resolved_metrics", {}).get("primary_location", {}).get("country_name"),
            event_type=raw_event.get("event_type"),
            goldstein_scale=raw_event.get("resolved_metrics", {}).get("avg_goldstein"),
            tone=raw_event.get("resolved_metrics", {}).get("avg_tone"),
            raw_data=raw_event
        )
```

### Health Check Endpoint

```python
# FastAPI health endpoint
from fastapi import APIRouter

router = APIRouter()

@router.get("/health/sources")
async def get_source_health():
    """Return health status for all data sources."""
    return {
        "sources": {
            source: health_dict
            for source, health in source_health_registry.items()
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health/kafka")
async def get_kafka_health():
    """Check Kafka connectivity and topic status."""
    # Check broker connectivity, topic lag, consumer offsets
    return {"status": "healthy", "topics": topic_status}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| GDELT raw CSV export | GDELT Cloud API | 2025 | Real-time access, semantic search |
| Batch-only conflict data | ACLED API streaming | 2022 | Daily updates, filtered queries |
| Manual SIPRI downloads | PyPI + scraping | 2020+ | Automated batch ingestion |
| JSON for Kafka events | Avro + Schema Registry | 2020+ | Schema evolution, compact encoding |

**Deprecated/outdated:**
- GDELT's legacy GKG exports (replaced by Cloud API)
- ACLED's old numeric inter codes (now text-based by default)
- Direct PostgreSQL inserts for real-time events (use Kafka → TimescaleDB connector)

---

## Open Questions

1. **SIPRI API Access**
   - What's unclear: No official API exists; need to confirm best approach for automated data retrieval
   - Recommendation: Start with manual CSV download via Airflow DAG, investigate scraping if needed

2. **ACLED Access Restrictions**
   - What's unclear: May have limited API access based on organization type
   - Recommendation: Register for API access early; prepare fallback to bulk download

3. **UNHCR Real-time Data**
   - What's unclear: What data is truly real-time vs. monthly aggregates?
   - Recommendation: Test API endpoints to measure actual latency

4. **Schema Registry Deployment**
   - What's unclear: Self-hosted vs. Confluent Cloud for Schema Registry
   - Recommendation: Start with self-hosted (Kafka Schema Registry), migrate if needed

---

## Sources

### Primary (HIGH confidence)
- **GDELT Cloud API**: https://docs.gdeltcloud.com/api-reference - REST API with Bearer auth, hourly updates
- **ACLED API Documentation**: https://acleddata.com/api-documentation/acled-endpoint - OAuth2, query filters
- **aiokafka Documentation**: https://aiokafka.readthedocs.io/en/stable - Async Kafka client
- **Confluent Schema Registry**: https://docs.confluent.io/platform/current/schema-registry/avro.html - Schema evolution

### Secondary (MEDIUM confidence)
- **IMF API**: https://www.imf.org/external/datamapper/api/help - SDMX format
- **World Bank API**: https://datahelpdesk.worldbank.org/knowledgebase/articles/898599-indicator-api-queries - v2 API
- **UNHCR Population Stats**: https://api.unhcr.org/docs/refugee-statistics.html - Public API
- **UN Voting Data Initiative**: https://unvoting.org/ - Academic API for UNGA voting

### Tertiary (LOW confidence)
- **SIPRI Arms Transfers**: https://armstrade.sipri.org/armstrade/page/trade_register.php - No API, web scraping required
- **Kafka DLQ Patterns**: WebSearch verified via multiple blog posts (Medium, OneUptime)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - aiokafka, httpx, tenacity all verified via official docs
- Architecture: HIGH - Based on established patterns from ARCHITECTURE.md
- External APIs: MEDIUM - GDELT/ACLED well-documented; others need verification
- Pitfalls: HIGH - Common issues verified through research
- Kafka patterns: HIGH - Confluent best practices documented

**Research date:** 2026-03-27
**Valid until:** 2026-04-27 (30 days - APIs change infrequently, but verify rate limits periodically)
