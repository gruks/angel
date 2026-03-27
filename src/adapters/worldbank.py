"""
World Bank source adapter for economic and development data.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

from src.adapters.base import SourceAdapter, TransientError, PermanentError
from src.schemas.economic import EconomicIndicator, EconomicSource, IndicatorType


class WorldBankAdapter(SourceAdapter):
    """
    Adapter for World Bank economic and development data.
    
    Fetches data from World Bank v2 API (no authentication required).
    Poll interval: 1 day.
    Indicators: SP.POP.TOTL (population), NY.GDP.PCAP.CD (GDP per capita), 
                MS.MIL.XPND.GD.ZS (military expenditure)
    """
    
    # World Bank API endpoint
    API_BASE_URL = "https://api.worldbank.org/v2"
    
    # Indicator codes to fetch
    INDICATORS = {
        "SP.POP.TOTL": IndicatorType.POPULATION,           # Total population
        "NY.GDP.PCAP.CD": IndicatorType.GDP_PER_CAPITA,    # GDP per capita (current US$)
        "MS.MIL.XPND.GD.ZS": IndicatorType.MILITARY_EXPENDITURE,  # Military expenditure (% of GDP)
    }
    
    # Country mapping for ISO codes
    ISO_MAP = {
        "afg": "AFG", "ago": "AGO", "alb": "ALB", "are": "ARE", "arg": "ARG",
        "arm": "ARM", "aus": "AUS", "aut": "AUT", "aze": "AZE", "bdi": "BDI",
        "bel": "BEL", "ben": "BEN", "bfa": "BFA", "bgd": "BGD", "bgr": "BGR",
        "bhr": "BHR", "bih": "BIH", "blr": "BLR", "blz": "BLZ", "bol": "BOL",
        "bra": "BRA", "btn": "BTN", "bwa": "BWA", "caf": "CAF", "can": "CAN",
        "che": "CHE", "chl": "CHL", "chn": "CHN", "civ": "CIV", "cmr": "CMR",
        "cod": "COD", "cog": "COG", "col": "COL", "com": "COM", "cri": "CRI",
        "cub": "CUB", "cyp": "CYP", "cze": "CZE", "deu": "DEU", "dji": "DJI",
        "dma": "DMA", "dnk": "DNK", "dom": "DOM", "dza": "DZA", "egy": "EGY",
        "eri": "ERI", "esp": "ESP", "est": "EST", "eth": "ETH", "fin": "FIN",
        "fji": "FJI", "fra": "FRA", "gab": "GAB", "gbr": "GBR", "geo": "GEO",
        "gha": "GHA", "gin": "GIN", "gmb": "GMB", "gnb": "GNB", "gnq": "GNQ",
        "grc": "GRC", "grd": "GRD", "gtm": "GTM", "guy": "GUY", "hnd": "HND",
        "hrv": "HRV", "hti": "HTI", "hun": "HUN", "idn": "IDN", "ind": "IND",
        "irl": "IRL", "irn": "IRN", "irq": "IRQ", "isl": "ISL", "isr": "ISR",
        "ita": "ITA", "jam": "JAM", "jor": "JOR", "jpn": "JPN", "kaz": "KAZ",
        "ken": "KEN", "kgz": "KGZ", "khm": "KHM", "kir": "KIR", "kna": "KNA",
        "kor": "KOR", "kwt": "KWT", "lao": "LAO", "lbn": "LBN", "lbr": "LBR",
        "lby": "LBY", "lca": "LCA", "lka": "LKA", "lso": "LSO", "ltu": "LTU",
        "lux": "LUX", "lva": "LVA", "mar": "MAR", "mda": "MDA", "mdg": "MDG",
        "mex": "MEX", "mkd": "MKD", "mli": "MLI", "mlt": "MLT", "mmr": "MMR",
        "mne": "MNE", "mng": "MNG", "moz": "MOZ", "mrt": "MRT", "mus": "MUS",
        "mwi": "MWI", "mys": "MYS", "nam": "NAM", "ner": "NER", "nga": "NGA",
        "nic": "NIC", "nld": "NLD", "nor": "NOR", "npl": "NPL", "nzl": "NZL",
        "omn": "OMN", "pak": "PAK", "pan": "PAN", "per": "PER", "phl": "PHL",
        "png": "PNG", "pol": "POL", "prk": "PRK", "prt": "PRT", "pry": "PRY",
        "pse": "PSE", "pyf": "PYF", "qat": "QAT", "rou": "ROU", "rus": "RUS",
        "rwa": "RWA", "sau": "SAU", "sdn": "SDN", "sen": "SEN", "sgp": "SGP",
        "sle": "SLE", "slv": "SLV", "som": "SOM", "srb": "SRB", "ssp": "SSD",
        "sur": "SUR", "svk": "SVK", "svn": "SVN", "swe": "SWE", "swz": "SWZ",
        "syr": "SYR", "tcd": "TCD", "tgo": "TGO", "tha": "THA", "tjk": "TJK",
        "tkm": "TKM", "tls": "TLS", "ton": "TON", "tun": "TUN", "tur": "TUR",
        "tza": "TZA", "uga": "UGA", "ukr": "UKR", "ury": "URY", "usa": "USA",
        "uzb": "UZB", "ven": "VEN", "vnm": "VNM", "vut": "VUT", "yem": "YEM",
        "zaf": "ZAF", "zmb": "ZMB", "zwe": "ZWE",
    }
    
    def __init__(self):
        super().__init__(
            source_name="worldbank",
            poll_interval=timedelta(days=1)
        )
        self._base_url = self.API_BASE_URL
    
    async def fetch_new_events(
        self, 
        last_update: Optional[datetime] = None
    ) -> list[dict]:
        """
        Fetch economic indicators from World Bank API.
        
        Fetches multiple indicators for all countries using the v2 API.
        No authentication required.
        """
        all_data = []
        
        # Determine year range
        end_year = datetime.now().year
        start_year = end_year - 5  # Last 5 years of data
        
        # Fetch each indicator
        for indicator_code, indicator_type in self.INDICATORS.items():
            try:
                data = await self._fetch_indicator(indicator_code, indicator_type, start_year, end_year)
                all_data.extend(data)
            except TransientError:
                # Continue with other indicators
                continue
        
        return all_data
    
    async def _fetch_indicator(
        self, 
        indicator_code: str, 
        indicator_type: IndicatorType,
        start_year: int,
        end_year: int
    ) -> list[dict]:
        """Fetch a specific indicator from World Bank API."""
        # World Bank API v2 format
        url = f"{self._base_url}/country/all/indicator/{indicator_code}"
        params = {
            "format": "json",
            "date": f"{start_year}:{end_year}",
            "per_page": 500  # Max results per page
        }
        
        try:
            all_results = []
            page = 1
            
            async with aiohttp.ClientSession() as session:
                while True:
                    params["page"] = page
                    async with session.get(
                        url,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        if response.status == 429:
                            raise TransientError("World Bank rate limit exceeded")
                        if response.status != 200:
                            raise TransientError(f"World Bank API error: {response.status}")
                        
                        data = await response.json()
                        
                        # World Bank returns [metadata, data] array
                        if len(data) < 2:
                            break
                        
                        records = data[1]
                        if not records:
                            break
                        
                        for record in records:
                            if record.get("value") is None:
                                continue
                            
                            country_code = record.get("countryiso3code", "")
                            country_id = record.get("country", {}).get("id", "").lower()
                            
                            all_results.append({
                                "indicator_code": indicator_code,
                                "indicator_type": indicator_type,
                                "country_iso": self.ISO_MAP.get(country_id, country_code or "UNK"),
                                "country_name": record.get("country", {}).get("value"),
                                "year": int(record.get("date", 0)),
                                "value": float(record["value"]),
                                "unit": self._get_unit(indicator_type)
                            })
                        
                        # Check for more pages
                        total_pages = data[0].get("pages", 1)
                        if page >= total_pages:
                            break
                        page += 1
            
            return all_results
            
        except asyncio.TimeoutError:
            raise TransientError("World Bank request timed out")
        except aiohttp.ClientError as e:
            raise TransientError(f"World Bank connection error: {str(e)}")
    
    def _get_unit(self, indicator_type: IndicatorType) -> str:
        """Get the unit for an indicator type."""
        units = {
            IndicatorType.GDP: "usd",
            IndicatorType.GDP_PER_CAPITA: "usd",
            IndicatorType.INFLATION: "percent",
            IndicatorType.UNEMPLOYMENT: "percent",
            IndicatorType.POPULATION: "persons",
            IndicatorType.MILITARY_EXPENDITURE: "percent_gdp",
        }
        return units.get(indicator_type, "unknown")
    
    def normalize(self, raw_event: dict) -> EconomicIndicator:
        """
        Normalize World Bank data to EconomicIndicator schema.
        """
        return EconomicIndicator(
            source=EconomicSource.WORLD_BANK,
            country_iso=raw_event.get("country_iso", "UNK"),
            country_name=raw_event.get("country_name"),
            year=raw_event.get("year", datetime.now().year),
            value=float(raw_event.get("value", 0)),
            unit=raw_event.get("unit", "unknown"),
            indicator_type=raw_event.get("indicator_type", IndicatorType.POPULATION),
            raw_data=raw_event
        )