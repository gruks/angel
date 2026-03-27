from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EventSource(str, Enum):
    """Enumeration of supported event data sources."""
    GDELT = "gdelt"
    ACLED = "acled"
    UNHCR = "unhcr"
    UN_VOTING = "un_voting"
    ECONOMIC = "economic"
    SIPRI = "sipri"


class DisorderType(str, Enum):
    """Classification types for conflict events based on CAMEO taxonomy."""
    POLITICAL_VIOLENCE = "political_violence"
    PROTEST = "protest"
    STRATEGIC_DEVELOPMENTS = "strategic_developments"
    DEMOGRAPHICS = "demographics"


class ConflictEvent(BaseModel):
    """
    Normalized conflict event model representing a single event from any source.
    
    Transforms heterogeneous source data into a unified schema compatible with
    ACLED's CAMEO-derived taxonomy.
    """
    # Primary identifiers
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now().timestamp()}")
    source: EventSource
    event_date: datetime = Field(alias="event_date")
    
    # Ingestion metadata
    ingestion_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Location fields
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_iso: Optional[str] = Field(default=None, max_length=3)
    country_name: Optional[str] = None
    admin_region: Optional[str] = None
    
    # Event classification
    disorder_type: Optional[DisorderType] = None
    event_type: Optional[str] = None
    sub_event_type: Optional[str] = None
    
    # Actors (if applicable)
    actor1: Optional[str] = None
    actor2: Optional[str] = None
    
    # Severity metrics
    fatalities: int = 0
    confidence: float = 1.0
    
    # Computed fields
    goldstein_scale: Optional[float] = Field(default=None, ge=-10, le=10)
    tone: Optional[float] = Field(default=None, ge=-100, le=100)
    
    # Raw source data preserved for audit trail
    raw_data: Optional[dict] = None
    
    class Config:
        populate_by_name = True


class EventSourceHealth(BaseModel):
    """Model for tracking external data source health status."""
    source: str
    status: str = "unknown"  # healthy, degraded, down
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    avg_latency_ms: float = 0.0


# Export all models for easy import
__all__ = [
    "ConflictEvent",
    "EventSource",
    "DisorderType",
    "EventSourceHealth",
]