"""
Kafka topic definitions and management for ConflictPulse event streaming.

This module defines the canonical topic names and partitioning strategy
for the event streaming pipeline.
"""
from dataclasses import dataclass
from typing import Optional


# Topic naming conventions:
# - raw.events.* : Unprocessed events from external sources
# - normalized.events : Events after schema transformation
# - enriched.events : Events after ML processing
# - dlq.events : Dead letter queue for failed processing

RAW_TOPICS = {
    "gdelt": "raw.events.gdelt",
    "acled": "raw.events.acled",
    "unhcr": "raw.events.unhcr",
    "un_voting": "raw.events.un_voting",
}

NORMALIZED_TOPIC = "normalized.events"
ENRICHED_TOPIC = "enriched.events"
DLQ_TOPIC = "dlq.events"

# All topics in order of the pipeline
ALL_TOPICS = [
    # Raw topics (one per source)
    "raw.events.gdelt",
    "raw.events.acled",
    "raw.events.unhcr",
    "raw.events.un_voting",
    # Processed topics
    "normalized.events",
    "enriched.events",
    # Error handling
    "dlq.events",
]


@dataclass
class TopicConfig:
    """Configuration for a Kafka topic."""
    name: str
    num_partitions: int = 3
    replication_factor: int = 1
    retention_ms: int = 7 * 24 * 60 * 60 * 1000  # 7 days default
    retention_bytes: int = -1  # Unlimited
    compression_type: str = "lz4"


# Topic-specific configurations
TOPIC_CONFIGS = {
    "raw.events.gdelt": TopicConfig(
        name="raw.events.gdelt",
        num_partitions=6,
        retention_ms=7 * 24 * 60 * 60 * 1000,  # 7 days
    ),
    "raw.events.acled": TopicConfig(
        name="raw.events.acled",
        num_partitions=10,
        retention_ms=30 * 24 * 60 * 60 * 1000,  # 30 days
    ),
    "raw.events.unhcr": TopicConfig(
        name="raw.events.unhcr",
        num_partitions=5,
        retention_ms=30 * 24 * 60 * 60 * 1000,  # 30 days
    ),
    "raw.events.un_voting": TopicConfig(
        name="raw.events.un_voting",
        num_partitions=2,
        retention_ms=365 * 24 * 60 * 60 * 1000,  # 1 year
    ),
    "normalized.events": TopicConfig(
        name="normalized.events",
        num_partitions=10,
        retention_ms=90 * 24 * 60 * 60 * 1000,  # 90 days
    ),
    "enriched.events": TopicConfig(
        name="enriched.events",
        num_partitions=10,
        retention_ms=90 * 24 * 60 * 60 * 1000,  # 90 days
    ),
    "dlq.events": TopicConfig(
        name="dlq.events",
        num_partitions=1,
        retention_ms=7 * 24 * 60 * 60 * 1000,  # 7 days
    ),
}


def get_partition_key(event_source: str, country_iso: Optional[str], event_date: str) -> str:
    """
    Generate partition key for consistent ordering.
    
    Partition by composite key: source + country + day
    This ensures ordering within source-country-day while enabling parallelism.
    """
    country = country_iso or "XXX"
    return f"{event_source}:{country}:{event_date}"


def get_topic_names() -> list[str]:
    """Return all canonical topic names."""
    return ALL_TOPICS.copy()


def get_raw_topic(source: str) -> str:
    """Get the raw topic name for a specific source."""
    return RAW_TOPICS.get(source, f"raw.events.{source}")


def get_topic_config(topic_name: str) -> Optional[TopicConfig]:
    """Get configuration for a specific topic."""
    return TOPIC_CONFIGS.get(topic_name)


# Export functions
__all__ = [
    "RAW_TOPICS",
    "NORMALIZED_TOPIC",
    "ENRICHED_TOPIC",
    "DLQ_TOPIC",
    "ALL_TOPICS",
    "TopicConfig",
    "get_partition_key",
    "get_topic_names",
    "get_raw_topic",
    "get_topic_config",
]