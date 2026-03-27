"""
IMF (International Monetary Fund) source adapter.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

from src.adapters.base import SourceAdapter, TransientError, PermanentError
from src.schemas.economic import EconomicIndicator, EconomicSource, IndicatorType


class IMFAdapter(SourceAdapter):
    """
    Adapter for IMF (International Monetary Fund) economic data.
    
    Fetches data from IMF SDMX-JSON API.
    Poll interval: 1 day.
    Indicators: NGDPD (GDP), FPICPI (inflation), LUR (unemployment)
    """
    
    # IMF API endpoints
    API_BASE_URL = "https://dataservices.imf.org/REST/SDMX_JSON.svc"
    
    # Indicator codes to fetch
    INDICATORS = {
        "NGDPD": IndicatorType.GDP,          # GDP at purchaser's prices (current US$)
        "FPICPI": IndicatorType.INFLATION,   # Consumer price index (2010 = 100)
        "LUR": IndicatorType.UNEMPLOYMENT,   # Unemployment rate (% of labor force)
    }
    
    def __init__(self):
        super().__init__(
            source_name="imf",
            poll_interval=timedelta(days=1)
        )
        self._base_url = self.API_BASE_URL
    
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None
    ) -> list[dict]:
        """
        Fetch economic indicators from IMF API.
        
        Uses IMF's SDMX-JSON API to fetch multiple indicators for all countries.
        """
        all_data = []
        
        # Fetch each indicator
        for indicator_code, indicator_type in self.INDICATORS.items():
            try:
                data = await self._fetch_indicator(indicator_code, indicator_type)
                all_data.extend(data)
            except TransientError:
                # Continue with other indicators
                continue
        
        return all_data
    
    async def _fetch_indicator(
        self, 
        indicator_code: str, 
        indicator_type: IndicatorType
    ) -> list[dict]:
        """Fetch a specific indicator from IMF API."""
        # IMF SDMX-JSON endpoint structure
        url = f"{self._base_url}/CompactData/IFS/{indicator_code}.M....SP.PPP"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 429:
                        raise TransientError("IMF rate limit exceeded")
                    if response.status == 404:
                        # Indicator not found - skip
                        return []
                    if response.status != 200:
                        raise TransientError(f"IMF API error: {response.status}")
                    
                    data = await response.json()
                    return self._parse_imf_response(data, indicator_code, indicator_type)
                    
        except asyncio.TimeoutError:
            raise TransientError("IMF request timed out")
        except aiohttp.ClientError as e:
            raise TransientError(f"IMF connection error: {str(e)}")
    
    def _parse_imf_response(
        self, 
        data: dict, 
        indicator_code: str,
        indicator_type: IndicatorType
    ) -> list[dict]:
        """Parse IMF SDMX-JSON response into normalized format."""
        results = []
        
        try:
            # Navigate the IMF response structure
            # Structure: { data: { datasets: [ { series: [...] } ] } }
            datasets = data.get("data", {}).get("dataSets", [])
            
            for dataset in datasets:
                series_list = dataset.get("series", [])
                
                for series in series_list:
                    # Extract dimension values (country, year, etc.)
                    dims = series.get("attributes", {})
                    observations = series.get("observations", {})
                    
                    # Parse each observation (year/quarter)
                    for obs_key, obs_value in observations.items():
                        if not obs_value or len(obs_value) < 2:
                            continue
                        
                        # Time dimension
                        time_str = obs_key  # Format varies by dataset
                        year, month = self._parse_time_period(time_str)
                        
                        # Value
                        value = obs_value[0]
                        if value is None:
                            continue
                        
                        # Country from dimensions
                        country_iso = dims.get("0", "") or "UNKNOWN"
                        
                        results.append({
                            "indicator_code": indicator_code,
                            "indicator_type": indicator_type,
                            "country_iso": country_iso,
                            "year": year,
                            "month": month,
                            "value": value,
                            "unit": self._get_unit(indicator_type)
                        })
                        
        except (KeyError, TypeError, ValueError) as e:
            # Parsing error - return empty
            pass
        
        return results
    
    def _parse_time_period(self, time_str: str) -> tuple[int, Optional[int]]:
        """Parse IMF time period string to year and month."""
        # IMF uses formats like "2023Q1", "2023M01", or just "2023"
        try:
            if "Q" in time_str:
                quarter = int(time_str.split("Q")[1])
                year = int(time_str.split("Q")[0])
                month = (quarter - 1) * 3 + 1  # Q1 -> month 1, etc.
                return year, month
            elif "M" in time_str:
                parts = time_str.split("M")
                year = int(parts[0])
                month = int(parts[1])
                return year, month
            else:
                return int(time_str), None
        except (ValueError, IndexError):
            return datetime.now().year, None
    
    def _get_unit(self, indicator_type: IndicatorType) -> str:
        """Get the unit for an indicator type."""
        units = {
            IndicatorType.GDP: "usd",
            IndicatorType.GDP_PER_CAPITA: "usd",
            IndicatorType.INFLATION: "index",
            IndicatorType.UNEMPLOYMENT: "percent",
            IndicatorType.POPULATION: "persons",
            IndicatorType.MILITARY_EXPENDITURE: "usd",
        }
        return units.get(indicator_type, "unknown")
    
    def normalize(self, raw_event: dict) -> EconomicIndicator:
        """
        Normalize IMF data to EconomicIndicator schema.
        """
        return EconomicIndicator(
            source=EconomicSource.IMF,
            country_iso=raw_event.get("country_iso", "UNK"),
            year=raw_event.get("year", datetime.now().year),
            month=raw_event.get("month"),
            value=float(raw_event.get("value", 0)),
            unit=raw_event.get("unit", "unknown"),
            indicator_type=raw_event.get("indicator_type", IndicatorType.GDP),
            raw_data=raw_event
        )