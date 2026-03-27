from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EconomicSource(str, Enum):
    """Enumeration of economic data sources."""
    IMF = "imf"
    WORLD_BANK = "worldbank"
    SIPRI = "sipri"


class IndicatorType(str, Enum):
    """Standard economic indicator types."""
    GDP = "gdp"
    GDP_PER_CAPITA = "gdp_per_capita"
    INFLATION = "inflation"
    UNEMPLOYMENT = "unemployment"
    CURRENT_ACCOUNT = "current_account"
    RESERVES = "reserves"
    POPULATION = "population"
    MILITARY_EXPENDITURE = "military_expenditure"
    EXPORTS = "exports"
    IMPORTS = "imports"


class EconomicIndicator(BaseModel):
    """
    Normalized economic indicator model for storing data from IMF, World Bank, etc.
    
    Standardizes economic metrics across different sources into a common schema.
    """
    # Primary identifiers
    indicator_id: str = Field(default_factory=lambda: f"eco_{datetime.now().timestamp()}")
    source: EconomicSource
    country_iso: str = Field(max_length=3)
    country_name: Optional[str] = None
    
    # Time
    year: int = Field(ge=1900, le=2100)
    month: Optional[int] = Field(default=None, ge=1, le=12)
    
    # Value
    value: float
    unit: str  # percent, usd, etc.
    
    # Classification
    indicator_type: IndicatorType
    
    # Additional metadata
    raw_data: Optional[dict] = None
    
    # Ingestion metadata
    ingestion_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class EconomicIndicatorResponse(BaseModel):
    """Response model for economic indicator queries."""
    indicators: list[EconomicIndicator]
    total_count: int
    last_updated: datetime


# Export all models
__all__ = [
    "EconomicIndicator",
    "EconomicIndicatorResponse",
    "EconomicSource",
    "IndicatorType",
]