"""
SIPRI (Stockholm International Peace Research Institute) source adapter.
"""

import asyncio
import csv
import io
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

from src.adapters.base import SourceAdapter, TransientError, PermanentError
from src.schemas.event import ConflictEvent, EventSource, DisorderType


class SIPRIAdapter(SourceAdapter):
    """
    Adapter for SIPRI (Stockholm International Peace Research Institute) data.
    
    Fetches arms trade register data via CSV download (no official API).
    Poll interval: 7 days (batch via Airflow).
    Normalizes to ConflictEvent with STRATEGIC_DEVELOPMENTS category.
    """
    
    # SIPRI Arms Transfers Database URL (CSV format)
    ARMS_TRANSFERS_URL = "https://www.sipri.org/databases/armstransfers/export"
    
    def __init__(self):
        super().__init__(
            source_name="sipri",
            poll_interval=timedelta(days=7)
        )
        self._base_url = "https://www.sipri.org"
    
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None
    ) -> list[dict]:
        """
        Fetch SIPRI arms trade data via CSV export.
        
        Note: SIPRI doesn't have a public API, so we fetch their CSV export.
        This is typically run as a batch job via Airflow.
        """
        # SIPRI export URL (may need to be updated based on current format)
        url = f"{self._base_url}/databases/armstransfers"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Try to fetch the exports page first to find the CSV link
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        raise TransientError(f"SIPRI page fetch failed: {response.status}")
                    
                    # Parse the page to find export links
                    html = await response.text()
                    # For now, return empty list as SIPRI doesn't have direct API
                    # In production, would need to scrape the export links
                    return []
                    
        except asyncio.TimeoutError:
            raise TransientError("SIPRI request timed out")
        except aiohttp.ClientError as e:
            raise TransientError(f"SIPRI connection error: {str(e)}")
    
    def _parse_csv_stream(self, text: str) -> list[dict]:
        """Parse CSV data from SIPRI export."""
        results = []
        
        try:
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                results.append(row)
        except Exception:
            pass
        
        return results
    
    def normalize(self, raw_event: dict) -> ConflictEvent:
        """
        Normalize SIPRI arms trade data to ConflictEvent schema.
        
        Maps:
        - Supplier -> actor1 (arms exporter)
        - Recipient -> actor2 (arms importer)
        - Year -> event_date
        - TIV -> fatalities proxy (value of transfers)
        - Weapon type -> event_type
        """
        # Extract year from delivery year or current year
        delivery_year = raw_event.get("Delivery year", raw_event.get("Year", ""))
        year = datetime.now().year
        try:
            year_val = int(delivery_year) if delivery_year else datetime.now().year
            event_date = datetime(year_val, 1, 1)
            year = year_val
        except (ValueError, TypeError):
            event_date = datetime.now()
        
        # Map country names to ISO codes (simplified)
        supplier = raw_event.get("Supplier", raw_event.get("Origin", ""))
        recipient = raw_event.get("Recipient", raw_event.get("Destination", ""))
        
        # TIV (Trend Indicator Value) as proxy for conflict magnitude
        try:
            tiv = raw_event.get("TIV", raw_event.get("TIV delivered", "0"))
            fatalities = int(float(str(tiv).replace(",", "")) // 1000000) if tiv else 0
        except (ValueError, TypeError):
            fatalities = 0
        
        return ConflictEvent(
            event_id=f"sipri_{hash(supplier + recipient + str(year)) % 1000000}",
            source=EventSource.SIPRI,
            event_date=event_date,
            country_name=recipient,
            disorder_type=DisorderType.STRATEGIC_DEVELOPMENTS,
            event_type="arms_import",
            sub_event_type=raw_event.get("Weapon designation", raw_event.get("Weapon type", "")),
            actor1=supplier,
            actor2=recipient,
            fatalities=fatalities,
            raw_data=raw_event
        )


# Alternative: SIPRI Military Expenditure Database
class SIPRIMilExpAdapter(SourceAdapter):
    """
    Adapter for SIPRI Military Expenditure Database.
    
    Alternative adapter for fetching military spending data.
    """
    
    MIL_EXP_URL = "https://www.sipri.org/databases/milex/export"
    
    def __init__(self):
        super().__init__(
            source_name="sipri_milex",
            poll_interval=timedelta(days=30)
        )
    
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None
    ) -> list[dict]:
        """Fetch military expenditure data."""
        # Similar to above - would scrape/export CSV
        return []
    
    def normalize(self, raw_event: dict) -> ConflictEvent:
        """Normalize to ConflictEvent."""
        return ConflictEvent(
            event_id=f"sipri_milex_{raw_event.get('country', 'unknown')}",
            source=EventSource.SIPRI,
            event_date=datetime.now(),
            country_name=raw_event.get("country"),
            disorder_type=DisorderType.STRATEGIC_DEVELOPMENTS,
            event_type="military_expenditure",
            raw_data=raw_event
        )