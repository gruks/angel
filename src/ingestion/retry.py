"""
Retry logic with exponential backoff and dead letter queue (DLQ) handling.

Implements retry mechanisms for transient failures and sends permanent failures
to the DLQ for later analysis or reprocessing.
"""
import asyncio
import random
import logging
from datetime import datetime
from typing import Optional, Any, Callable, TypeVar
from dataclasses import dataclass, field

from src.kafka.client import get_kafka_client

logger = logging.getLogger(__name__)

# Retry configuration constants
RETRY_BASE_DELAY = 1.0  # seconds
RETRY_MAX_DELAY = 60.0  # seconds
RETRY_EXPONENTIAL_BASE = 2.0
RETRY_MAX_RETRIES = 5
RETRY_JITTER_FACTOR = 0.1  # 10% jitter


@dataclass
class RetryContext:
    """Context information for a retry attempt."""
    attempt: int
    max_attempts: int
    last_error: str
    total_time_ms: int
    start_time: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DLQRecord:
    """Dead letter queue record for failed events."""
    original_event: dict
    error: str
    retry_count: int
    last_attempt: datetime
    source: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Kafka serialization."""
        return {
            "original_event": self.original_event,
            "error": self.error,
            "retry_count": self.retry_count,
            "last_attempt": self.last_attempt.isoformat(),
            "source": self.source,
        }


class TransientError(Exception):
    """Error that may succeed on retry (network timeout, rate limit, etc.)."""
    pass


class PermanentError(Exception):
    """Error that will not succeed on retry (invalid API key, malformed request, etc.)."""
    pass


def calculate_delay(attempt: int, base_delay: float = RETRY_BASE_DELAY) -> float:
    """
    Calculate exponential backoff delay with jitter.
    
    Args:
        attempt: Current retry attempt (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay cap in seconds
    
    Returns:
        Delay in seconds with jitter applied
    """
    # Exponential backoff: base * (exponential_base ^ attempt)
    delay = base_delay * (RETRY_EXPONENTIAL_BASE ** attempt)
    
    # Cap at max delay
    delay = min(delay, RETRY_MAX_DELAY)
    
    # Add jitter (10% random variation)
    jitter = delay * RETRY_JITTER_FACTOR * (random.random() * 2 - 1)
    delay = max(0.1, delay + jitter)  # Minimum 100ms
    
    return delay


async def fetch_with_retry(
    fetch_func: Callable[[], Any],
    source: str = "unknown",
    max_retries: int = RETRY_MAX_RETRIES,
) -> Any:
    """
    Execute a fetch function with exponential backoff retry.
    
    Args:
        fetch_func: Async function to execute (e.g., adapter.fetch_new_events)
        source: Source name for logging
        max_retries: Maximum number of retry attempts
    
    Returns:
        Result from successful fetch
    
    Raises:
        PermanentError: After max retries exceeded
        Exception: Any non-retryable exception from fetch_func
    
    Example:
        >>> events = await fetch_with_retry(
        ...     lambda: adapter.fetch_new_events(last_update),
        ...     source="gdelt"
        ... )
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            result = await fetch_func()
            if attempt > 0:
                logger.info(f"{source}: Succeeded after {attempt} attempts")
            return result
            
        except PermanentError:
            # Don't retry permanent errors
            raise
            
        except TransientError as e:
            last_error = e
            logger.warning(
                f"{source}: Transient error (attempt {attempt + 1}/{max_retries + 1}): {e}"
            )
            
            if attempt < max_retries:
                delay = calculate_delay(attempt)
                logger.debug(f"{source}: Waiting {delay:.2f}s before retry")
                await asyncio.sleep(delay)
            
        except Exception as e:
            # Treat unknown exceptions as potentially transient
            last_error = e
            logger.warning(
                f"{source}: Unknown error (attempt {attempt + 1}/{max_retries + 1}): {e}"
            )
            
            if attempt < max_retries:
                delay = calculate_delay(attempt)
                logger.debug(f"{source}: Waiting {delay:.2f}s before retry")
                await asyncio.sleep(delay)
    
    # All retries exhausted
    raise PermanentError(
        f"Max retries ({max_retries}) exceeded for {source}. Last error: {last_error}"
    )


async def send_to_dlq(
    event: dict,
    error: str,
    retry_count: int = 0,
    source: str = "unknown",
) -> bool:
    """
    Send a failed event to the dead letter queue.
    
    Args:
        event: The original event that failed
        error: Error message from the failure
        retry_count: Number of retry attempts made
        source: Source name for the event
    
    Returns:
        True if successfully sent to DLQ, False otherwise
    
    Example:
        >>> await send_to_dlq(
        ...     event={"id": "123", "data": "..."},
        ...     error="Connection timeout after 5 retries",
        ...     retry_count=5,
        ...     source="gdelt"
        ... )
    """
    kafka_client = get_kafka_client()
    
    dlq_record = DLQRecord(
        original_event=event,
        error=error,
        retry_count=retry_count,
        last_attempt=datetime.utcnow(),
        source=source,
    )
    
    logger.warning(
        f"DLQ: Sending event from {source} to dead letter queue "
        f"(retry_count={retry_count}, error={error[:100]})"
    )
    
    try:
        success = await kafka_client.publish_to_dlq(
            event=dlq_record.to_dict(),
            key=source,
        )
        
        if success:
            logger.info(f"DLQ: Successfully sent event to dlq.events topic")
        else:
            logger.error(f"DLQ: Failed to publish to dlq.events topic")
            
        return success
        
    except Exception as e:
        logger.error(f"DLQ: Exception while sending to DLQ: {e}")
        return False


async def fetch_with_dlq(
    fetch_func: Callable[[], Any],
    source: str = "unknown",
    max_retries: int = RETRY_MAX_RETRIES,
) -> tuple[Optional[Any], bool]:
    """
    Execute fetch with retry, sending to DLQ on permanent failure.
    
    Combines fetch_with_retry and send_to_dlq for convenience.
    
    Args:
        fetch_func: Async function to execute
        source: Source name for logging
        max_retries: Maximum retry attempts
    
    Returns:
        Tuple of (result, success). If success=False, event was sent to DLQ.
    
    Example:
        >>> events, success = await fetch_with_dlq(
        ...     lambda: adapter.fetch_new_events(),
        ...     source="gdelt"
        ... )
        >>> if not success:
        ...     logger.error("Event sent to DLQ")
    """
    try:
        result = await fetch_with_retry(fetch_func, source, max_retries)
        return result, True
        
    except PermanentError as e:
        # Send to DLQ on permanent failure
        # We don't have the original event here, so we log the error
        logger.error(f"DLQ: Permanent failure for {source}: {e}")
        
        # Try to get event from the error context if available
        event = getattr(e, 'event', {}) or {"source": source, "error": str(e)}
        await send_to_dlq(event, str(e), max_retries, source)
        
        return None, False
        
    except Exception as e:
        # Unknown error - send to DLQ
        event = {"source": source, "error": str(e)}
        await send_to_dlq(event, str(e), max_retries, source)
        
        return None, False


# Type variable for generic function return
T = TypeVar('T')


# Export
__all__ = [
    "RetryContext",
    "DLQRecord",
    "TransientError",
    "PermanentError",
    "calculate_delay",
    "fetch_with_retry",
    "send_to_dlq",
    "fetch_with_dlq",
    "RETRY_BASE_DELAY",
    "RETRY_MAX_DELAY",
    "RETRY_EXPONENTIAL_BASE",
    "RETRY_MAX_RETRIES",
    "RETRY_JITTER_FACTOR",
]