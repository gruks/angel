"""
GDELT source adapter for fetching conflict events from GDELT API.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

from src.adapters.base import SourceAdapter, TransientError, PermanentError
from src.schemas.event import ConflictEvent, EventSource, DisorderType


class GDELTAdapter(SourceAdapter):
    """
    Adapter for GDELT (Global Database of Events, Language, and Tone).
    
    Fetches events from GDELT Cloud API with Bearer token authentication.
    Poll interval: 15 minutes.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            source_name="gdelt",
            poll_interval=timedelta(minutes=15)
        )
        self._api_key = api_key or ""
        self._base_url = "https://api.gdeltproject.org/v2"
    
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None
    ) -> list[dict]:
        """
        Fetch new events from GDELT API.
        
        Uses GDELT's Search API with mode=artlist&format=json to get events.
        """
        if not self._api_key:
            raise PermanentError("GDELT API key not configured")
        
        # Calculate date filter - GDELT uses YYYYMMDD format
        if last_update:
            # Fetch from last_update to now
            start_date = last_update.strftime("%Y%m%d")
            end_date = datetime.now().strftime("%Y%m%d")
        else:
            # Default to last 24 hours
            start_date = (datetime.now() - timedelta(hours=24)).strftime("%Y%m%d")
            end_date = datetime.now().strftime("%Y%m%d")
        
        url = f"{self._base_url}/search"
        params = {
            "query": f"arematch(start={start_date},end={end_date})",
            "mode": "artlist",
            "format": "json",
            "maxrec": "250",  # Limit results
            "sort": "DateDesc"
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    params=params, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 429:
                        raise TransientError("GDELT rate limit exceeded")
                    if response.status == 401:
                        raise PermanentError("Invalid GDELT API key")
                    if response.status != 200:
                        raise TransientError(f"GDELT API error: {response.status}")
                    
                    data = await response.json()
                    return data.get("articles", [])[:100]  # Limit events
                    
        except asyncio.TimeoutError:
            raise TransientError("GDELT request timed out")
        except aiohttp.ClientError as e:
            raise TransientError(f"GDELT connection error: {str(e)}")
    
    def normalize(self, raw_event: dict) -> ConflictEvent:
        """
        Normalize a GDELT event to ConflictEvent schema.
        
        Maps:
        - seendate -> event_date
        - url -> actor1 (as source reference)
        - domain -> actor2 (source domain)
        - title -> event_type
        - seentitle -> sub_event_type
        - language, translated title -> for tone analysis
        """
        # Extract date from seendate (YYYYMMDD format)
        seendate = raw_event.get("seendate", "")
        try:
            event_date = datetime.strptime(seendate[:8], "%Y%m%d")
        except (ValueError, TypeError):
            event_date = datetime.now()
        
        # Map domain to country (simplified - would need GeoIP for accuracy)
        domain = raw_event.get("domain", "")
        country_iso = self._extract_country_from_domain(domain)
        
        # Compute goldstein scale from sentiment if available
        tone = raw_event.get("tone", 0)
        goldstein = self._tone_to_goldstein(tone)
        
        return ConflictEvent(
            event_id=f"gdelt_{raw_event.get('url', '').hash()}",
            source=EventSource.GDELT,
            event_date=event_date,
            country_iso=country_iso,
            country_name=raw_event.get("country", ""),
            event_type=raw_event.get("type", ""),
            sub_event_type=raw_event.get("subtype", ""),
            actor1=raw_event.get("domain", ""),
            actor2=raw_event.get("socialimage", "")[:100] if raw_event.get("socialimage") else None,
            tone=tone,
            goldstein_scale=goldstein,
            raw_data=raw_event
        )
    
    def _extract_country_from_domain(self, domain: str) -> Optional[str]:
        """Extract country code from domain (simplified)."""
        # This would need actual country mapping logic
        # For now, return None and let downstream handle
        return None
    
    def _tone_to_goldstein(self, tone: float) -> Optional[float]:
        """Convert GDELT tone (-100 to 100) to Goldstein scale (-10 to 10)."""
        return max(-10, min(10, tone / 10)) if tone is not None else None