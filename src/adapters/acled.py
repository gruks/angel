"""
ACLED (Armed Conflict Location and Event Data) source adapter.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

from src.adapters.base import SourceAdapter, TransientError, PermanentError
from src.schemas.event import ConflictEvent, EventSource, DisorderType


class ACLEDAdapter(SourceAdapter):
    """
    Adapter for ACLED (Armed Conflict Location and Event Data).
    
    Fetches events using OAuth2 password flow authentication.
    Poll interval: 6 hours.
    Uses ACLED Dyadic export format by default.
    """
    
    def __init__(
        self, 
        username: Optional[str] = None, 
        password: Optional[str] = None,
        access_token: Optional[str] = None
    ):
        super().__init__(
            source_name="acled",
            poll_interval=timedelta(hours=6)
        )
        self._username = username
        self._password = password
        self._access_token = access_token
        self._base_url = "https://api.acleddata.com"
    
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None,
        country: Optional[str] = None,
        year: Optional[int] = None
    ) -> list[dict]:
        """
        Fetch events from ACLED API.
        
        Args:
            last_update: Datetime of last successful fetch
            country: Optional country filter (ISO 3 code or name)
            year: Optional year filter
        """
        # Get access token if not available
        if not self._access_token:
            await self._authenticate()
        
        # Build query parameters
        params = {
            "format": "json",
            "limit": 1000  # Max per request
        }
        
        if country:
            params["country"] = country
        if year:
            params["year"] = year
        elif last_update:
            # Default to current year if last_update provided
            params["year"] = datetime.now().year
        
        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._base_url}/export",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 429:
                        raise TransientError("ACLED rate limit exceeded")
                    if response.status == 401:
                        raise PermanentError("Invalid ACLED credentials")
                    if response.status == 403:
                        raise PermanentError("ACLED account not authorized for API access")
                    if response.status != 200:
                        raise TransientError(f"ACLED API error: {response.status}")
                    
                    data = await response.json()
                    return data if isinstance(data, list) else data.get("data", [])
                    
        except asyncio.TimeoutError:
            raise TransientError("ACLED request timed out")
        except aiohttp.ClientError as e:
            raise TransientError(f"ACLED connection error: {str(e)}")
    
    async def _authenticate(self) -> None:
        """Authenticate with ACLED using OAuth2 password flow."""
        if not self._username or not self._password:
            raise PermanentError("ACLED credentials not configured")
        
        auth_url = f"{self._base_url}/login"
        data = {
            "email": self._username,
            "password": self._password
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    auth_url, 
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        raise PermanentError(f"ACLED authentication failed: {response.status}")
                    
                    result = await response.json()
                    self._access_token = result.get("access_token")
                    if not self._access_token:
                        raise PermanentError("ACLED authentication did not return access token")
                        
        except asyncio.TimeoutError:
            raise TransientError("ACLED authentication timed out")
        except aiohttp.ClientError as e:
            raise TransientError(f"ACLED authentication error: {str(e)}")
    
    def normalize(self, raw_event: dict) -> ConflictEvent:
        """
        Normalize an ACLED event to ConflictEvent schema.
        
        Maps ACLED fields:
        - event_id_cnty -> event_id
        - event_date -> event_date
        - country -> country_name
        - admin1, admin2, admin3 -> admin_region
        - latitude, longitude -> lat/lon
        - event_type -> disorder_type
        - sub_event_type -> event_type
        - actor1, actor2 -> actors
        - fatalities -> fatalities
        - source -> raw_data
        """
        # Parse date - ACLED uses DD/MM/YYYY format
        event_date_str = raw_event.get("event_date", "")
        try:
            event_date = datetime.strptime(event_date_str, "%d/%m/%Y")
        except ValueError:
            try:
                event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
            except ValueError:
                event_date = datetime.now()
        
        # Map event_type to DisorderType
        event_type = raw_event.get("event_type", "")
        disorder_type = self._map_event_type(event_type)
        
        # Extract country ISO (would need mapping table in production)
        country_name = raw_event.get("country", "")
        
        # Build admin region string
        admin_parts = [
            raw_event.get("admin1", ""),
            raw_event.get("admin2", ""),
            raw_event.get("admin3", "")
        ]
        admin_region = ", ".join(p for p in admin_parts if p) or None
        
        # Parse fatalities
        try:
            fatalities = int(raw_event.get("fatalities", 0) or 0)
        except (ValueError, TypeError):
            fatalities = 0
        
        return ConflictEvent(
            event_id=raw_event.get("event_id_cnty", f"acled_{raw_event.get('data_id', '')}"),
            source=EventSource.ACLED,
            event_date=event_date,
            latitude=raw_event.get("latitude"),
            longitude=raw_event.get("longitude"),
            country_name=country_name,
            admin_region=admin_region,
            disorder_type=disorder_type,
            event_type=event_type,
            sub_event_type=raw_event.get("sub_event_type"),
            actor1=raw_event.get("actor1"),
            actor2=raw_event.get("actor2"),
            fatalities=fatalities,
            raw_data=raw_event
        )
    
    def _map_event_type(self, event_type: str) -> Optional[DisorderType]:
        """Map ACLED event types to DisorderType enum."""
        mapping = {
            "Battle": DisorderType.POLITICAL_VIOLENCE,
            "Explosion": DisorderType.POLITICAL_VIOLENCE,
            "Violence against civilians": DisorderType.POLITICAL_VIOLENCE,
            "Riots": DisorderType.PROTEST,
            "Protests": DisorderType.PROTEST,
            "Strategic developments": DisorderType.STRATEGIC_DEVELOPMENTS,
        }
        return mapping.get(event_type)