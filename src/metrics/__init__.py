"""
Prometheus metrics for monitoring the ingestion pipeline.

Provides metrics for source availability, event counts, and latency tracking.
"""
from prometheus_client import Counter, Gauge, Histogram

# Source availability metrics
source_up = Gauge(
    "conflictpulse_source_up",
    "Whether a source is currently up (1) or down (0)",
    ["source"],
)

# Event ingestion metrics
events_ingested = Counter(
    "conflictpulse_events_ingested_total",
    "Total number of events ingested per source",
    ["source", "status"],  # status: success, failed, dlq
)

events_ingested_by_type = Counter(
    "conflictpulse_events_ingested_by_type_total",
    "Total number of events by type (conflict, economic)",
    ["source", "event_type"],
)

# Latency metrics
ingestion_latency = Histogram(
    "conflictpulse_ingestion_latency_seconds",
    "Time taken to fetch and process events from a source",
    ["source"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)

# Retry metrics
retry_attempts = Counter(
    "conflictpulse_retry_attempts_total",
    "Total number of retry attempts",
    ["source", "outcome"],  # outcome: success, failed, dlq
)

# Kafka metrics
kafka_messages_published = Counter(
    "conflictpulse_kafka_messages_published_total",
    "Total number of Kafka messages published",
    ["topic", "source"],
)

kafka_publish_errors = Counter(
    "conflictpulse_kafka_publish_errors_total",
    "Total number of Kafka publish errors",
    ["topic", "source"],
)

# Health check metrics
health_check_duration = Histogram(
    "conflictpulse_health_check_duration_seconds",
    "Time taken for health check to complete",
    ["source"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
)


def record_event_ingested(source: str, status: str = "success") -> None:
    """Record an event ingestion."""
    events_ingested.labels(source=source, status=status).inc()


def record_event_by_type(source: str, event_type: str) -> None:
    """Record an event by type."""
    events_ingested_by_type.labels(source=source, event_type=event_type).inc()


def record_latency(source: str, latency_seconds: float) -> None:
    """Record ingestion latency."""
    ingestion_latency.labels(source=source).observe(latency_seconds)


def record_retry(source: str, outcome: str) -> None:
    """Record a retry attempt."""
    retry_attempts.labels(source=source, outcome=outcome).inc()


def record_kafka_published(topic: str, source: str) -> None:
    """Record a successful Kafka publish."""
    kafka_messages_published.labels(topic=topic, source=source).inc()


def record_kafka_error(topic: str, source: str) -> None:
    """Record a Kafka publish error."""
    kafka_publish_errors.labels(topic=topic, source=source).inc()


def set_source_up(source: str, up: bool) -> None:
    """Set source up/down status."""
    source_up.labels(source=source).set(1 if up else 0)


def record_health_check_duration(source: str, duration_seconds: float) -> None:
    """Record health check duration."""
    health_check_duration.labels(source=source).observe(duration_seconds)


# Export
__all__ = [
    "source_up",
    "events_ingested",
    "events_ingested_by_type",
    "ingestion_latency",
    "retry_attempts",
    "kafka_messages_published",
    "kafka_publish_errors",
    "health_check_duration",
    "record_event_ingested",
    "record_event_by_type",
    "record_latency",
    "record_retry",
    "record_kafka_published",
    "record_kafka_error",
    "set_source_up",
    "record_health_check_duration",
]