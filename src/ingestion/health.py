"""
Health tracking system for monitoring data source status.

Provides SourceHealth dataclass for tracking individual source status,
HealthTracker for managing health state, and Prometheus metrics for monitoring.
"""
import logging
from datetime import datetime
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class SourceStatus(str, Enum):
    """Health status for a data source."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"
    UNKNOWN = "UNKNOWN"


@dataclass
class SourceHealth:
    """
    Health information for a single data source.
    
    Tracks current status, timing information, and failure counts
    to enable accurate health monitoring.
    """
    source: str
    status: SourceStatus = SourceStatus.UNKNOWN
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    total_successes: int = 0
    total_failures: int = 0
    avg_latency_ms: float = 0.0
    last_latency_ms: Optional[float] = None
    last_check: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "source": self.source,
            "status": self.status.value,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "consecutive_failures": self.consecutive_failures,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "last_latency_ms": round(self.last_latency_ms, 2) if self.last_latency_ms else None,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "error_message": self.error_message,
        }


class HealthTracker:
    """
    Manages health tracking for all data sources.
    
    Provides methods to update health based on fetch results,
    retrieve current status, and calculate overall system health.
    """
    
    # Threshold for marking a source as degraded
    CONSECUTIVE_FAILURE_THRESHOLD = 3
    
    # Threshold for marking a source as down
    MAX_CONSECUTIVE_FAILURES = 10
    
    # Latency thresholds (ms)
    LATENCY_DEGRADED_THRESHOLD = 5000  # 5 seconds
    LATENCY_DOWN_THRESHOLD = 30000     # 30 seconds
    
    def __init__(self):
        """Initialize the health tracker."""
        self._health: dict[str, SourceHealth] = {}
    
    def get_or_create(self, source: str) -> SourceHealth:
        """
        Get existing health or create new entry for a source.
        
        Args:
            source: Source name
        
        Returns:
            SourceHealth instance for the source
        """
        if source not in self._health:
            self._health[source] = SourceHealth(source=source)
            logger.debug(f"Created new health entry for {source}")
        return self._health[source]
    
    def record_success(
        self,
        source: str,
        latency_ms: float,
    ) -> SourceHealth:
        """
        Record a successful fetch for a source.
        
        Args:
            source: Source name
            latency_ms: Fetch latency in milliseconds
        
        Returns:
            Updated SourceHealth instance
        """
        health = self.get_or_create(source)
        
        now = datetime.utcnow()
        health.last_success = now
        health.last_check = now
        health.consecutive_failures = 0
        health.total_successes += 1
        health.last_latency_ms = latency_ms
        
        # Update running average latency
        if health.avg_latency_ms == 0:
            health.avg_latency_ms = latency_ms
        else:
            health.avg_latency_ms = (
                (health.avg_latency_ms * (health.total_successes - 1) + latency_ms)
                / health.total_successes
            )
        
        # Determine status based on latency
        if latency_ms > self.LATENCY_DOWN_THRESHOLD:
            health.status = SourceStatus.DOWN
        elif latency_ms > self.LATENCY_DEGRADED_THRESHOLD:
            health.status = SourceStatus.DEGRADED
        else:
            health.status = SourceStatus.HEALTHY
        
        health.error_message = None
        
        logger.debug(
            f"Health: {source} -> {health.status.value} "
            f"(latency={latency_ms:.2f}ms, successes={health.total_successes})"
        )
        
        return health
    
    def record_failure(
        self,
        source: str,
        error: str,
        latency_ms: Optional[float] = None,
    ) -> SourceHealth:
        """
        Record a failed fetch for a source.
        
        Args:
            source: Source name
            error: Error message
            latency_ms: Optional latency if available
        
        Returns:
            Updated SourceHealth instance
        """
        health = self.get_or_create(source)
        
        now = datetime.utcnow()
        health.last_failure = now
        health.last_check = now
        health.consecutive_failures += 1
        health.total_failures += 1
        health.last_latency_ms = latency_ms
        health.error_message = error[:500] if error else "Unknown error"
        
        # Determine status based on consecutive failures
        if health.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            health.status = SourceStatus.DOWN
        elif health.consecutive_failures >= self.CONSECUTIVE_FAILURE_THRESHOLD:
            health.status = SourceStatus.DEGRADED
        else:
            health.status = SourceStatus.UNKNOWN
        
        logger.warning(
            f"Health: {source} -> {health.status.value} "
            f"(consecutive_failures={health.consecutive_failures}, error={error[:100]})"
        )
        
        return health
    
    def update_health(
        self,
        source: str,
        success: bool,
        latency_ms: Optional[float] = None,
        error: Optional[str] = None,
    ) -> SourceHealth:
        """
        Update health based on fetch attempt result.
        
        Args:
            source: Source name
            success: Whether the fetch succeeded
            latency_ms: Optional latency in milliseconds
            error: Optional error message
        
        Returns:
            Updated SourceHealth instance
        """
        if success:
            return self.record_success(source, latency_ms or 0.0)
        else:
            return self.record_failure(source, error or "Unknown error", latency_ms)
    
    def get_health(self, source: str) -> Optional[SourceHealth]:
        """
        Get health for a specific source.
        
        Args:
            source: Source name
        
        Returns:
            SourceHealth or None if not tracked
        """
        return self._health.get(source)
    
    def get_all_health(self) -> list[SourceHealth]:
        """
        Get health for all tracked sources.
        
        Returns:
            List of SourceHealth instances
        """
        return list(self._health.values())
    
    def get_unhealthy_sources(self) -> list[SourceHealth]:
        """
        Get all sources that are not healthy.
        
        Returns:
            List of unhealthy SourceHealth instances
        """
        return [
            h for h in self._health.values()
            if h.status in (SourceStatus.DEGRADED, SourceStatus.DOWN)
        ]
    
    def get_system_health(self) -> dict:
        """
        Get overall system health summary.
        
        Returns:
            Dictionary with system health metrics
        """
        all_health = self.get_all_health()
        
        if not all_health:
            return {
                "status": "UNKNOWN",
                "total_sources": 0,
                "healthy": 0,
                "degraded": 0,
                "down": 0,
            }
        
        healthy = sum(1 for h in all_health if h.status == SourceStatus.HEALTHY)
        degraded = sum(1 for h in all_health if h.status == SourceStatus.DEGRADED)
        down = sum(1 for h in all_health if h.status == SourceStatus.DOWN)
        
        # Overall status is the worst of any source
        if down > 0:
            overall_status = "DOWN"
        elif degraded > 0:
            overall_status = "DEGRADED"
        elif healthy == len(all_health):
            overall_status = "HEALTHY"
        else:
            overall_status = "UNKNOWN"
        
        return {
            "status": overall_status,
            "total_sources": len(all_health),
            "healthy": healthy,
            "degraded": degraded,
            "down": down,
            "sources": [h.to_dict() for h in all_health],
        }
    
    def reset_source(self, source: str) -> None:
        """
        Reset health for a specific source.
        
        Args:
            source: Source name to reset
        """
        if source in self._health:
            self._health[source] = SourceHealth(source=source)
            logger.info(f"Reset health for {source}")
    
    def clear_all(self) -> None:
        """Clear all health tracking (primarily for testing)."""
        self._health.clear()
        logger.info("Cleared all health tracking")


# Global health tracker instance
_health_tracker: Optional[HealthTracker] = None


def get_health_tracker() -> HealthTracker:
    """Get or create the global health tracker instance."""
    global _health_tracker
    if _health_tracker is None:
        _health_tracker = HealthTracker()
    return _health_tracker


# Export
__all__ = [
    "SourceStatus",
    "SourceHealth",
    "HealthTracker",
    "get_health_tracker",
]