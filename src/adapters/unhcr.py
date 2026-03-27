"""
UNHCR (UN Refugee Agency) source adapter.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

from src.adapters.base import SourceAdapter, TransientError, PermanentError
from src.schemas.event import ConflictEvent, EventSource, DisorderType


class UNHCRAdapter(SourceAdapter):
    """
    Adapter for UNHCR refugee and displacement data.
    
    Fetches refugee population statistics from UNHCR Population Statistics Reference Database.
    Poll interval: 12 hours.
    Tracks displacement flows as leading conflict indicators.
    Normalizes to ConflictEvent with DEMOGRAPHICS category.
    """
    
    # UNHCR Population Statistics API
    API_BASE_URL = "https://api.unhcr.org"
    
    # UNHCR provides CSV/Excel exports
    POPULATION_URL = "https://www.unhcr.org/refugee-statistics/download/"
    
    # Known asylum countries for mapping
    ASYLUM_COUNTRIES = {
        "afg": "AFG", "dza": "DZA", "egy": "EGY", "irn": "IRN", "irq": "IRQ",
        "jor": "JOR", "lbn": "LBN", "pak": "PAK", "syr": "SYR", "tur": "TUR",
        "deu": "DEU", "grc": "GRC", "ita": "ITA", "fra": "FRA", "gbr": "GBR",
    }
    
    def __init__(self):
        super().__init__(
            source_name="unhcr",
            poll_interval=timedelta(hours=12)
        )
        self._base_url = self.API_BASE_URL
    
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None
    ) -> list[dict]:
        """
        Fetch UNHCR refugee population data.
        
        Data includes: origin country, asylum country, refugee population, 
        asylum applications, returns, etc.
        """
        # UNHCR provides downloadable datasets
        # For now, we'll try their public API endpoint
        url = f"{self._base_url}/v1/population"
        
        params = {
            "year": datetime.now().year,
            "format": "json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 404:
                        # API not available, try alternative data source
                        return await self._fetch_from_dataset()
                    if response.status == 429:
                        raise TransientError("UNHCR rate limit exceeded")
                    if response.status != 200:
                        raise TransientError(f"UNHCR API error: {response.status}")
                    
                    data = await response.json()
                    return data if isinstance(data, list) else data.get("data", [])
                    
        except asyncio.TimeoutError:
            return await self._fetch_from_dataset()
        except aiohttp.ClientError:
            return await self._fetch_from_dataset()
    
    async def _fetch_from_dataset(self) -> list[dict]:
        """
        Try to fetch from UNHCR's publicly available datasets.
        
        UNHCR provides CSV/Excel downloads at their statistics portal.
        In production, this would be a scheduled download job.
        """
        # Return empty for now - would need to implement CSV parsing
        # from UNHCR's downloadable datasets
        return []
    
    def normalize(self, raw_event: dict) -> ConflictEvent:
        """
        Normalize UNHCR data to ConflictEvent schema.
        
        UNHCR data represents population movements (refugees, asylum seekers).
        These are mapped to:
        - Origin country -> event source (conflict in origin causes displacement)
        - Refugee count -> fatalities proxy (displacement magnitude)
        - Asylum country -> country (where they're counted)
        """
        # Extract data fields
        origin = raw_event.get("origin", raw_event.get("country_of_origin", ""))
        asylum = raw_event.get("asylum", raw_event.get("country_of_asylum", ""))
        
        # Get refugee count
        try:
            refugees = int(raw_event.get("refugees", raw_event.get("population", 0) or 0))
        except (ValueError, TypeError):
            refugees = 0
        
        # Year
        year = raw_event.get("year", datetime.now().year)
        try:
            event_date = datetime(int(year), 1, 1)
        except (ValueError, TypeError):
            event_date = datetime.now()
        
        # Displacement type
        pop_type = raw_event.get("type", raw_event.get("population_type", "REF"))
        
        # Map population type to event classification
        if pop_type == "REF":
            event_type = "refugee_arrival"
        elif pop_type == "ASY":
            event_type = "asylum_seeker"
        elif pop_type == "IDP":
            event_type = "internal_displacement"
        else:
            event_type = "displacement"
        
        # Use refugee count as severity proxy (scaled down)
        # 1,000,000 refugees = scale 10
        fatalities = min(10, refugees // 100000)
        
        return ConflictEvent(
            event_id=f"unhcr_{origin}_{asylum}_{year}",
            source=EventSource.UNHCR,
            event_date=event_date,
            country_name=asylum,
            disorder_type=DisorderType.DEMOGRAPHICS,
            event_type=event_type,
            sub_event_type=pop_type,
            actor1=origin,
            actor2=asylum,
            fatalities=fatalities,
            confidence=0.9,
            raw_data=raw_event
        )


class UNHCRDisplacementFlowsAdapter(SourceAdapter):
    """
    Adapter for UNHCR displacement flow data.
    
    Tracks new displacement events (rather than stock population).
    Useful for detecting acute crisis onset.
    """
    
    def __init__(self):
        super().__init__(
            source_name="unhcr_flows",
            poll_interval=timedelta(hours=6)  # More frequent for flow data
        )
    
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None
    ) -> list[dict]:
        """
        Fetch displacement flow data (new arrivals, returns, etc.).
        """
        # Would fetch from UNHCR's internal systems or IXN dataset
        return []
    
    def normalize(self, raw_event: dict) -> ConflictEvent:
        """Normalize to ConflictEvent with higher urgency."""
        return ConflictEvent(
            event_id=f"unhcr_flow_{raw_event.get('origin', '')}_{raw_event.get('date', '')}",
            source=EventSource.UNHCR,
            event_date=datetime.now(),
            country_name=raw_event.get("asylum"),
            disorder_type=DisorderType.DEMOGRAPHICS,
            event_type="displacement_flow",
            actor1=raw_event.get("origin"),
            fatalities=raw_event.get("new_arrivals", 0) // 100000,
            raw_data=raw_event
        )