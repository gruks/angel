"""
Base adapter interface and common utilities for data source adapters.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from src.schemas.event import ConflictEvent
from src.schemas.economic import EconomicIndicator


class AdapterError(Exception):
    """Base exception for adapter errors."""
    pass


class TransientError(AdapterError):
    """Error that may succeed on retry (network timeout, rate limit, etc.)."""
    pass


class PermanentError(AdapterError):
    """Error that will not succeed on retry (invalid API key, malformed request, etc.)."""
    pass


class SourceAdapter(ABC):
    """
    Abstract base class for all data source adapters.
    
    Each adapter implements fetch and normalize methods to bridge external APIs
    with the normalized event schema. This enables adding/removing sources without
    changing the pipeline.
    """
    
    def __init__(self, source_name: str, poll_interval: timedelta):
        """
        Initialize the adapter.
        
        Args:
            source_name: Unique identifier for this data source
            poll_interval: How often to poll for new data
        """
        self._source_name = source_name
        self._poll_interval = poll_interval
    
    @property
    def source_name(self) -> str:
        """Return the source name."""
        return self._source_name
    
    @property
    def poll_interval(self) -> timedelta:
        """Return the poll interval."""
        return self._poll_interval
    
    @abstractmethod
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None
    ) -> list[dict]:
        """
        Fetch new events from the external data source.
        
        Args:
            last_update: Datetime of the last successful fetch. If None, fetch recent data.
            
        Returns:
            List of raw event dictionaries from the external source.
            
        Raises:
            TransientError: For retryable errors (timeout, rate limit, etc.)
            PermanentError: For non-retryable errors (invalid credentials, etc.)
        """
        pass
    
    @abstractmethod
    def normalize(self, raw_event: dict) -> ConflictEvent | EconomicIndicator:
        """
        Normalize a raw event from this source to the unified schema.
        
        Args:
            raw_event: Raw event dictionary from fetch_new_events
            
        Returns:
            Normalized ConflictEvent or EconomicIndicator depending on source type.
        """
        pass
    
    async def health_check(self) -> bool:
        """
        Check if the data source is accessible.
        
        Returns:
            True if the source is healthy, False otherwise.
        """
        try:
            await self.fetch_new_events()
            return True
        except Exception:
            return False