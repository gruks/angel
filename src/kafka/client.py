"""
Kafka client wrapper for ConflictPulse event streaming.

Provides async producer and consumer utilities using aiokafka.
"""
import os
import json
import logging
from typing import Optional, Callable, Any
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError

from src.kafka.topics import (
    get_topic_names,
    get_raw_topic,
    NORMALIZED_TOPIC,
    ENRICHED_TOPIC,
    DLQ_TOPIC,
)

logger = logging.getLogger(__name__)


class KafkaClient:
    """
    Async Kafka client wrapper for ConflictPulse.
    
    Handles connection lifecycle and provides convenience methods for
    publishing and consuming events.
    """
    
    def __init__(self, bootstrap_servers: Optional[str] = None):
        """
        Initialize Kafka client.
        
        Args:
            bootstrap_servers: Comma-separated list of broker addresses.
                              Defaults to KAFKA_BOOTSTRAP_SERVERS env var.
        """
        self._bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", 
            "localhost:9092"
        )
        self._producer: Optional[AIOKafkaProducer] = None
        self._consumers: dict[str, AIOKafkaConsumer] = {}
    
    async def start_producer(self) -> AIOKafkaProducer:
        """Start the Kafka producer."""
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            await self._producer.start()
            logger.info(f"Kafka producer started: {self._bootstrap_servers}")
        return self._producer
    
    async def stop_producer(self):
        """Stop the Kafka producer."""
        if self._producer:
            await self._producer.stop()
            self._producer = None
            logger.info("Kafka producer stopped")
    
    async def publish_event(
        self,
        topic: str,
        event: dict,
        key: Optional[str] = None,
    ) -> bool:
        """
        Publish an event to a Kafka topic.
        
        Args:
            topic: Target topic name
            event: Event data as dictionary
            key: Optional partition key
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            producer = await self.start_producer()
            await producer.send_and_wait(topic, value=event, key=key)
            logger.debug(f"Published event to {topic}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            return False
    
    async def publish_to_raw_topic(
        self,
        source: str,
        event: dict,
        country_iso: Optional[str] = None,
        event_date: Optional[str] = None,
    ) -> bool:
        """
        Publish an event to the appropriate raw topic for a source.
        
        Args:
            source: Data source (gdelt, acled, unhcr, etc.)
            event: Event data
            country_iso: Optional country code for partitioning
            event_date: Optional date string for partitioning
            
        Returns:
            True if published successfully
        """
        topic = get_raw_topic(source)
        key = None
        if country_iso and event_date:
            key = f"{source}:{country_iso}:{event_date}"
        
        return await self.publish_event(topic, event, key)
    
    async def publish_to_normalized(self, event: dict, key: Optional[str] = None) -> bool:
        """Publish to the normalized events topic."""
        return await self.publish_event(NORMALIZED_TOPIC, event, key)
    
    async def publish_to_enriched(self, event: dict, key: Optional[str] = None) -> bool:
        """Publish to the enriched events topic."""
        return await self.publish_event(ENRICHED_TOPIC, event, key)
    
    async def publish_to_dlq(self, event: dict, error: str) -> bool:
        """Publish a failed event to the dead letter queue."""
        dlq_event = {
            "original_event": event,
            "error": error,
            "timestamp": event.get("ingestion_timestamp"),
        }
        return await self.publish_event(DLQ_TOPIC, dlq_event)
    
    async def create_consumer(
        self,
        topic: str,
        group_id: str = "conflictpulse-consumer",
        auto_offset_reset: str = "earliest",
    ) -> AIOKafkaConsumer:
        """
        Create a Kafka consumer for a topic.
        
        Args:
            topic: Topic to consume from
            group_id: Consumer group ID
            auto_offset_reset: Where to start reading ('earliest' or 'latest')
            
        Returns:
            Configured Kafka consumer (not started)
        """
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            key_deserializer=lambda m: m.decode("utf-8") if m else None,
        )
        self._consumers[topic] = consumer
        return consumer
    
    async def start_consumer(self, topic: str, handler: Callable[[dict], Any]):
        """
        Start consuming from a topic and process messages with a handler.
        
        Args:
            topic: Topic to consume from
            handler: Async function to process each message
            
        Returns:
            Consumer task
        """
        if topic not in self._consumers:
            await self.create_consumer(topic)
        
        consumer = self._consumers[topic]
        await consumer.start()
        
        try:
            async for msg in consumer:
                try:
                    await handler(msg.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Could publish to DLQ here
        finally:
            await consumer.stop()
    
    async def stop_all(self):
        """Stop all producers and consumers."""
        await self.stop_producer()
        for topic, consumer in self._consumers.items():
            await consumer.stop()
        self._consumers.clear()
        logger.info("All Kafka clients stopped")
    
    @property
    def is_connected(self) -> bool:
        """Check if producer is connected."""
        return self._producer is not None and self._producer._transport is not None


# Global client instance
_kafka_client: Optional[KafkaClient] = None


def get_kafka_client(bootstrap_servers: Optional[str] = None) -> KafkaClient:
    """Get or create the global Kafka client instance."""
    global _kafka_client
    if _kafka_client is None:
        _kafka_client = KafkaClient(bootstrap_servers)
    return _kafka_client


async def ensure_topics_exist(admin_client, topics: list[str]) -> list[str]:
    """
    Create topics that don't exist yet.
    
    Args:
        admin_client: Kafka admin client
        topics: List of topic names to ensure exist
        
    Returns:
        List of topics that were created
    """
    # This would require kafka-python-admin or similar
    # For now, just return the topics - they can be auto-created
    return topics


# Export
__all__ = [
    "KafkaClient",
    "get_kafka_client",
    "get_topic_names",
    "get_raw_topic",
    "NORMALIZED_TOPIC",
    "ENRICHED_TOPIC",
    "DLQ_TOPIC",
]