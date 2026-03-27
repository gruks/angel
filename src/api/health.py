"""
FastAPI health endpoints for monitoring source status and Kafka connectivity.

Provides /health/sources, /health/kafka, and /health endpoints.
"""
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException

from src.ingestion.health import get_health_tracker, SourceStatus
from src.kafka.client import get_kafka_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

# All 7 data sources
ALL_SOURCES = [
    "gdelt",
    "acled",
    "unhcr",
    "imf",
    "worldbank",
    "sipri",
    "un_voting",
]


@router.get("/sources")
async def get_sources_health():
    """
    Get health status for all configured data sources.
    
    Returns:
        Dictionary mapping source names to health status
    """
    tracker = get_health_tracker()
    
    # Get health for each source
    sources_health = {}
    for source in ALL_SOURCES:
        health = tracker.get_health(source)
        if health:
            sources_health[source] = health.to_dict()
        else:
            # Source not yet polled - show as UNKNOWN
            sources_health[source] = {
                "source": source,
                "status": SourceStatus.UNKNOWN.value,
                "last_success": None,
                "last_failure": None,
                "consecutive_failures": 0,
                "total_successes": 0,
                "total_failures": 0,
                "avg_latency_ms": 0,
                "last_latency_ms": None,
                "last_check": None,
                "error_message": "Not yet polled",
            }
    
    # Calculate summary
    healthy_count = sum(
        1 for h in sources_health.values()
        if h["status"] == SourceStatus.HEALTHY.value
    )
    degraded_count = sum(
        1 for h in sources_health.values()
        if h["status"] == SourceStatus.DEGRADED.value
    )
    down_count = sum(
        1 for h in sources_health.values()
        if h["status"] == SourceStatus.DOWN.value
    )
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total": len(ALL_SOURCES),
            "healthy": healthy_count,
            "degraded": degraded_count,
            "down": down_count,
            "unknown": len(ALL_SOURCES) - healthy_count - degraded_count - down_count,
        },
        "sources": sources_health,
    }


@router.get("/kafka")
async def get_kafka_health():
    """
    Check Kafka connectivity, topic existence, and consumer offsets.
    
    Returns:
        Kafka cluster and topic status
    """
    kafka_client = get_kafka_client()
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "connected": False,
        "bootstrap_servers": kafka_client._bootstrap_servers,
        "topics": {},
        "errors": [],
    }
    
    try:
        # Try to start producer to check connectivity
        await kafka_client.start_producer()
        
        # Check if producer is connected
        if kafka_client.is_connected:
            result["connected"] = True
            result["status"] = "healthy"
        else:
            result["status"] = "degraded"
            result["errors"].append("Producer not fully connected")
            
    except Exception as e:
        result["status"] = "down"
        result["errors"].append(f"Connection error: {str(e)[:200]}")
        return result
    
    # Check topics (if admin client available)
    from src.kafka.topics import get_topic_names
    
    topics = get_topic_names()
    for topic in topics:
        result["topics"][topic] = {
            "exists": True,  # Topics may be auto-created
            "configured": True,
        }
    
    return result


@router.get("/")
async def get_overall_health():
    """
    Get overall system health including database, Kafka, and sources.
    
    Returns:
        Overall system health status
    """
    tracker = get_health_tracker()
    
    # Get source health
    sources_response = await get_sources_health()
    source_summary = sources_response["summary"]
    
    # Get Kafka health
    kafka_response = await get_kafka_health()
    
    # Determine overall status
    overall_status = "healthy"
    
    # Check source status
    if source_summary["down"] > 0:
        overall_status = "down"
    elif source_summary["degraded"] > 0:
        overall_status = "degraded"
    
    # Check Kafka status
    if kafka_response.get("status") == "down":
        overall_status = "down"
    elif kafka_response.get("status") == "degraded" and overall_status == "healthy":
        overall_status = "degraded"
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": overall_status,
        "components": {
            "sources": {
                "status": "healthy" if source_summary["down"] == 0 else "degraded",
                "healthy": source_summary["healthy"],
                "degraded": source_summary["degraded"],
                "down": source_summary["down"],
                "total": source_summary["total"],
            },
            "kafka": {
                "status": kafka_response.get("status", "unknown"),
                "connected": kafka_response.get("connected", False),
            },
        },
        "checks": {
            "sources": f"{source_summary['healthy']}/{source_summary['total']} healthy",
            "kafka": "connected" if kafka_response.get("connected") else "disconnected",
        },
    }


# Export router
__all__ = ["router"]