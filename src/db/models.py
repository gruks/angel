"""
Database models using SQLAlchemy for ConflictPulse.

This provides SQLAlchemy models as an alternative to Prisma for Python-based
database operations. For TypeScript/Node.js operations, use the Prisma client.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, Index, UniqueConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ConflictEventModel(Base):
    """SQLAlchemy model for conflict events."""
    __tablename__ = "conflict_events"
    
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())
    source = Column(String(50), nullable=False, index=True)
    event_date = Column(DateTime(timezone=True), nullable=False)
    
    # Location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    country_iso = Column(String(3), nullable=True)
    country_name = Column(String(255), nullable=True)
    admin_region = Column(String(255), nullable=True)
    
    # Classification
    disorder_type = Column(String(50), nullable=True)
    event_type = Column(String(100), nullable=True)
    sub_event_type = Column(String(100), nullable=True)
    
    # Actors
    actor1 = Column(String(255), nullable=True)
    actor2 = Column(String(255), nullable=True)
    
    # Severity
    fatalities = Column(Integer, default=0)
    confidence = Column(Float, default=1.0)
    
    # Computed
    goldstein_scale = Column(Float, nullable=True)
    tone = Column(Float, nullable=True)
    
    # Raw data
    raw_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_conflict_events_source_date", "source", "event_date"),
        Index("ix_conflict_events_country_date", "country_iso", "event_date"),
    )


class EconomicIndicatorModel(Base):
    """SQLAlchemy model for economic indicators."""
    __tablename__ = "economic_indicators"
    
    indicator_id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())
    source = Column(String(50), nullable=False)  # imf, worldbank
    country_iso = Column(String(3), nullable=False)
    country_name = Column(String(255), nullable=True)
    year = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    indicator_type = Column(String(50), nullable=True)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint("source", "country_iso", "year", "indicator_type", name="uq_economic_indicator"),
        Index("ix_economic_indicators_country_year", "country_iso", "year"),
    )


class SourceHealthModel(Base):
    """SQLAlchemy model for tracking external data source health."""
    __tablename__ = "source_health"
    
    source = Column(String(50), primary_key=True)
    status = Column(String(20), default="unknown")  # healthy, degraded, down
    last_success = Column(DateTime(timezone=True), nullable=True)
    last_failure = Column(DateTime(timezone=True), nullable=True)
    consecutive_failures = Column(Integer, default=0)
    avg_latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# Export models
__all__ = [
    "Base",
    "ConflictEventModel",
    "EconomicIndicatorModel",
    "SourceHealthModel",
]