"""
Ingestion orchestrator for coordinating all data source adapters.

This module provides the main loop that polls all registered data sources
at their configured intervals and publishes events to Kafka.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from src.adapters.registry import AdapterRegistry
from src.kafka.client import get_kafka_client
from src.config import get_poll_interval

logger = logging.getLogger(__name__)


class IngestionOrchestrator:
    """
    Main ingestion orchestrator that coordinates polling of all data sources.
    
    Manages the lifecycle of the ingestion pipeline, tracking last update times
    per source and publishing normalized events to Kafka topics.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self._registry = AdapterRegistry()
        self._kafka_client = get_kafka_client()
        self._running = False
        self._tasks: dict[str, asyncio.Task] = {}
        self._last_update: dict[str, Optional[datetime]] = {}
        self._poll_intervals: dict[str, int] = {}
    
    def _register_all_adapters(self):
        """Register all available adapters with their poll intervals."""
        adapter_map = {
            "gdelt": ("src.adapters.gdelt", "GDELTAdapter"),
            "acled": ("src.adapters.acled", "ACLEDAdapter"),
            "unhcr": ("src.adapters.unhcr", "UNHCRAdapter"),
            "imf": ("src.adapters.imf", "IMFAdapter"),
            "worldbank": ("src.adapters.worldbank", "WorldBankAdapter"),
            "sipri": ("src.adapters.sipri", "SIPRIAdapter"),
            "un_voting": ("src.adapters.un_voting", "UNVotingAdapter"),
        }
        
        for source, (module_path, class_name) in adapter_map.items():
            try:
                # Import the adapter class
                from importlib import import_module
                module = import_module(module_path)
                adapter_class = getattr(module, class_name)
                
                # Get poll interval from config
                interval_seconds = get_poll_interval(source)
                poll_interval = timedelta(seconds=interval_seconds)
                
                # Create and register adapter
                adapter = adapter_class()
                self._registry.register(adapter)
                self._poll_intervals[source] = interval_seconds
                self._last_update[source] = None
                
                logger.info(f"Registered adapter: {source} (poll_interval={interval_seconds}s)")
                
            except Exception as e:
                logger.warning(f"Failed to register {source} adapter: {e}")
    
    async def _poll_source(self, source: str):
        """
        Poll a single source and publish events.
        
        Args:
            source: Source name to poll
        """
        try:
            adapter = self._registry.get_adapter(source)
            last_update = self._last_update.get(source)
            
            logger.debug(f"Polling {source} (last_update={last_update})")
            
            # Fetch new events
            raw_events = await adapter.fetch_new_events(last_update)
            
            if not raw_events:
                logger.debug(f"No new events from {source}")
                return
            
            # Publish raw events first
            for event in raw_events:
                event["ingestion_timestamp"] = datetime.utcnow().isoformat()
                event["source"] = source
                
                # Publish to raw topic
                await self._kafka_client.publish_to_raw_topic(
                    source=source,
                    event=event,
                    country_iso=event.get("country_iso"),
                    event_date=event.get("event_date"),
                )
                
                # Normalize and publish to normalized topic
                try:
                    normalized = adapter.normalize(event)
                    await self._kafka_client.publish_to_normalized(
                        event=normalized.model_dump(),
                        key=f"{source}:{normalized.country_iso}" if hasattr(normalized, 'country_iso') else None,
                    )
                except Exception as e:
                    logger.error(f"Failed to normalize event from {source}: {e}")
            
            # Update last update time
            self._last_update[source] = datetime.utcnow()
            logger.info(f"Polled {source}: {len(raw_events)} events")
            
        except Exception as e:
            logger.error(f"Error polling {source}: {e}")
    
    async def _poll_loop(self, source: str):
        """
        Continuous polling loop for a single source.
        
        Args:
            source: Source name to continuously poll
        """
        interval = self._poll_intervals.get(source, 3600)
        
        while self._running:
            await self._poll_source(source)
            await asyncio.sleep(interval)
    
    async def start_ingestion(self):
        """Start the ingestion pipeline."""
        if self._running:
            logger.warning("Ingestion already running")
            return
        
        # Register all adapters
        self._register_all_adapters()
        
        self._running = True
        
        # Start Kafka producer
        await self._kafka_client.start_producer()
        
        # Start polling tasks for each adapter
        sources = self._registry.list_adapters()
        for source in sources:
            task = asyncio.create_task(self._poll_loop(source))
            self._tasks[source] = task
            logger.info(f"Started polling task for {source}")
        
        logger.info(f"Ingestion started with {len(sources)} sources")
    
    async def stop_ingestion(self):
        """Stop the ingestion pipeline."""
        if not self._running:
            logger.warning("Ingestion not running")
            return
        
        self._running = False
        
        # Cancel all polling tasks
        for source, task in self._tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"Stopped polling task for {source}")
        
        self._tasks.clear()
        
        # Stop Kafka producer
        await self._kafka_client.stop_producer()
        
        logger.info("Ingestion stopped")
    
    async def poll_sources(self, sources: Optional[list[str]] = None):
        """
        Manually trigger a poll of specified sources (or all if None).
        
        Args:
            sources: List of source names to poll, or None for all
        """
        if sources is None:
            sources = self._registry.list_adapters()
        
        # Poll all sources in parallel
        await asyncio.gather(
            *[self._poll_source(source) for source in sources],
            return_exceptions=True,
        )
    
    @property
    def is_running(self) -> bool:
        """Check if ingestion is currently running."""
        return self._running
    
    @property
    def sources(self) -> list[str]:
        """Get list of registered source names."""
        return self._registry.list_adapters()
    
    def get_last_update(self, source: str) -> Optional[datetime]:
        """Get the last update time for a source."""
        return self._last_update.get(source)


# Global orchestrator instance
_orchestrator: Optional[IngestionOrchestrator] = None


def get_orchestrator() -> IngestionOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = IngestionOrchestrator()
    return _orchestrator


# Export
__all__ = ["IngestionOrchestrator", "get_orchestrator"]