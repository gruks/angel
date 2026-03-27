"""
UN Voting (UNGA Roll Call) source adapter.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

from src.adapters.base import SourceAdapter, TransientError, PermanentError
from src.schemas.event import ConflictEvent, EventSource, DisorderType


class UNVotingAdapter(SourceAdapter):
    """
    Adapter for UN General Assembly Voting Data.
    
    Fetches from Voeten, Strezhneva & Zhirnov datasets (unvoting.org).
    Tracks voting alignment between countries as diplomatic tension indicator.
    Poll interval: 30 days (per UNGA session).
    """
    
    # Voeten's UNGA voting data API
    API_BASE_URL = "https://ungapl.digitaldemon.co.uk/api"
    
    # Alternative: Direct download URL
    DATA_URL = "https://data.harvard.edu/UNGA-Voting-Data"
    
    def __init__(self):
        super().__init__(
            source_name="un_voting",
            poll_interval=timedelta(days=30)
        )
        self._base_url = self.API_BASE_URL
    
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None
    ) -> list[dict]:
        """
        Fetch UNGA voting records.
        
        Data includes: session, country, vote (yes/no/abstain), date, resolution.
        """
        url = f"{self._base_url}/votes"
        
        params = {}
        if last_update:
            # Filter by session/year
            params["session"] = last_update.year - 1945  # UNGA started in 1946
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 404:
                        # API not available, try alternative
                        return await self._fetch_alternative(last_update)
                    if response.status == 429:
                        raise TransientError("UN Voting rate limit exceeded")
                    if response.status != 200:
                        raise TransientError(f"UN Voting API error: {response.status}")
                    
                    data = await response.json()
                    return data if isinstance(data, list) else data.get("votes", [])
                    
        except asyncio.TimeoutError:
            return await self._fetch_alternative(last_update)
        except aiohttp.ClientError:
            return await self._fetch_alternative(last_update)
    
    async def _fetch_alternative(self, last_update: Optional[datetime]) -> list[dict]:
        """Try alternative data source or return empty."""
        # In production, would fetch from Harvard Dataverse or similar
        # For now, return sample structure
        return []
    
    def normalize(self, raw_event: dict) -> ConflictEvent:
        """
        Normalize UN voting data to ConflictEvent schema.
        
        Creates events representing diplomatic alignment/disagreement.
        - vote = 'no' or 'abstain' on resolutions related to conflict → tension event
        - High disagreement between countries → diplomatic tension
        """
        # Parse session and date
        session = raw_event.get("session", 0)
        year = 1945 + session
        
        try:
            date_str = raw_event.get("date", "")
            if date_str:
                event_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            else:
                event_date = datetime(year, 9, 1)  # UNGA typically meets in September
        except (ValueError, TypeError):
            event_date = datetime(year, 9, 1)
        
        # Vote mapping
        vote = raw_event.get("vote", "")
        country = raw_event.get("country", raw_event.get("Country", ""))
        
        # Map vote to event classification
        if vote in ["no", "abstain"]:
            event_type = "diplomatic_disagreement"
            confidence = 0.7
        else:
            event_type = "diplomatic_agreement"
            confidence = 0.9
        
        # Create event for each voting record
        return ConflictEvent(
            event_id=f"unv_{session}_{raw_event.get('cc', 'UNK')}_{raw_event.get('rcid', '0')}",
            source=EventSource.UN_VOTING,
            event_date=event_date,
            country_iso=raw_event.get("cc", "").upper() if raw_event.get("cc") else None,
            country_name=country,
            disorder_type=DisorderType.STRATEGIC_DEVELOPMENTS,
            event_type=event_type,
            sub_event_type=raw_event.get("desc", ""),
            confidence=confidence,
            raw_data=raw_event
        )


class UNVotingAlignmentAdapter(SourceAdapter):
    """
    Adapter for computing country-level voting alignment scores.
    
    Instead of individual votes, this adapter computes pairwise alignment
    scores between countries based on their voting history.
    """
    
    def __init__(self):
        super().__init__(
            source_name="un_voting_alignment",
            poll_interval=timedelta(days=90)  # Less frequent - alignment changes slowly
        )
    
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None
    ) -> list[dict]:
        """
        Compute pairwise voting alignment scores.
        
        Returns pairs of countries with alignment scores (0-1).
        """
        # Would need to fetch all votes and compute alignment
        # For now, return empty
        return []
    
    def normalize(self, raw_event: dict) -> ConflictEvent:
        """
        Normalize alignment data to ConflictEvent.
        
        Creates events representing diplomatic alignment between country pairs.
        """
        return ConflictEvent(
            event_id=f"unv_align_{raw_event.get('country1', '')}_{raw_event.get('country2', '')}",
            source=EventSource.UN_VOTING,
            event_date=datetime.now(),
            country_iso=raw_event.get("country1"),
            country_name=raw_event.get("country1_name"),
            disorder_type=DisorderType.STRATEGIC_DEVELOPMENTS,
            event_type="voting_alignment",
            actor1=raw_event.get("country1"),
            actor2=raw_event.get("country2"),
            confidence=float(raw_event.get("alignment", 0.5)),
            raw_data=raw_event
        )