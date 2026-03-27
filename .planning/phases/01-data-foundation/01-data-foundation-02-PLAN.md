---
phase: 01-data-foundation
plan: "02"
type: execute
wave: 2
depends_on: ["01-data-foundation-01-PLAN"]
files_modified:
  - src/adapters/base.py
  - src/adapters/gdelt.py
  - src/adapters/acled.py
  - src/adapters/imf.py
  - src/adapters/worldbank.py
  - src/adapters/sipri.py
  - src/adapters/un_voting.py
  - src/adapters/unhcr.py
  - src/adapters/registry.py
autonomous: true
user_setup:
  - service: external_apis
    why: "7 external data sources need API keys/config"
    env_vars:
      - name: GDELT_API_KEY
        source: "GDELT Cloud API registration"
      - name: ACLED_USERNAME
        source: "ACLED account registration"
      - name: ACLED_PASSWORD
        source: "ACLED account password"

must_haves:
  truths:
    - "Each of 7 data sources has a working adapter that can fetch data"
    - "All adapters normalize to ConflictEvent schema"
    - "Adapters can run independently with their own poll intervals"
  artifacts:
    - path: "src/adapters/base.py"
      provides: "Base SourceAdapter abstract class"
      exports: ["SourceAdapter"]
    - path: "src/adapters/gdelt.py"
      provides: "GDELT source adapter"
      methods: ["fetch_new_events", "normalize"]
    - path: "src/adapters/acled.py"
      provides: "ACLED source adapter"
      methods: ["fetch_new_events", "normalize"]
    - path: "src/adapters/registry.py"
      provides: "Adapter registry for orchestration"
      methods: ["get_adapter", "list_adapters"]
  key_links:
    - from: "src/adapters/gdelt.py"
      to: "src/schemas/event.py"
      via: "normalize() returns ConflictEvent"
      pattern: "def normalize.*ConflictEvent"
    - from: "src/adapters/registry.py"
      to: "src/kafka/client.py"
      via: "producer.send() to publish normalized events"
      pattern: "await producer.send"
---

<objective>
Create modular data source adapters for all 7 external data sources. Each adapter implements the SourceAdapter interface with fetch and normalize methods.

Purpose: Adapters are the bridge between external APIs and the normalized event schema. This enables adding/removing sources without changing the pipeline.
Output: 7 source adapters + adapter registry
</objective>

<execution_context>
@C:/Users/HP/.config/opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/HP/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/research/STACK.md
@.planning/phases/01-data-foundation/01-data-foundation-RESEARCH.md
@.planning/phases/01-data-foundation/01-data-foundation-01-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create base adapter interface and registry</name>
  <files>src/adapters/base.py, src/adapters/registry.py</files>
  <action>
Create abstract SourceAdapter base class:
- Properties: source_name (str), poll_interval (timedelta)
- Methods: fetch_new_events(last_update: datetime) -> list[dict], normalize(raw_event: dict) -> ConflictEvent
- Error handling: raise specific exceptions for transient vs permanent failures

Create AdapterRegistry:
- Singleton pattern to manage all adapters
- get_adapter(source: str) -> SourceAdapter
- list_adapters() -> list[str]
- get_poll_interval(source: str) -> timedelta
  </action>
  <verify>
Run `python -c "from src.adapters.base import SourceAdapter; from src.adapters.registry import AdapterRegistry; print('OK')"` to verify imports.
  </verify>
  <done>
Base adapter interface defined. Registry can instantiate adapters by name.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create GDELT and ACLED adapters</name>
  <files>src/adapters/gdelt.py, src/adapters/acled.py</files>
  <action>
Create GDELTAdapter:
- Poll interval: 15 minutes
- Fetch from GDELT Cloud API with Bearer token auth
- Normalize to ConflictEvent: map cluster_id→event_id, resolve location, goldstein scale, tone
- Handle rate limits gracefully

Create ACLEDAdapter:
- Poll interval: 6 hours
- OAuth2 password flow authentication
- Fetch events filtered by country/year
- Normalize: map event_id_cnty→event_id, event_type, actor1/actor2, fatalities, lat/lon
- Use Dyadic export format by default
  </action>
  <verify>
Run `python -c "from src.adapters.gdelt import GDELTAdapter; from src.adapters.acled import ACLEDAdapter; print('OK')"` to verify imports.
  </verify>
  <done>
GDELT and ACLED adapters implement SourceAdapter interface. Can fetch and normalize data.
  </done>
</task>

<task type="auto">
  <name>Task 3: Create economic data adapters (IMF, World Bank)</name>
  <files>src/adapters/imf.py, src/adapters/worldbank.py</files>
  <action>
Create IMFAdapter:
- Poll interval: 1 day
- Fetch from IMF SDMX-JSON API
- Indicators: NGDPD (GDP), FPICPI (inflation), LUR (unemployment)
- Normalize to EconomicIndicator schema (not ConflictEvent - different schema)

Create WorldBankAdapter:
- Poll interval: 1 day
- Fetch from World Bank v2 API (no auth)
- Indicators: SP.POP.TOTL (population), NY.GDP.PCAP.CD (GDP per capita), MS.MIL.XPND.GD.ZS (military expenditure)
- Normalize to EconomicIndicator schema
  </action>
  <verify>
Run `python -c "from src.adapters.imf import IMFAdapter; from src.adapters.worldbank import WorldBankAdapter; print('OK')"` to verify imports.
  </verify>
  <done>
IMF and World Bank adapters fetch economic indicators and normalize to schema.
  </done>
</task>

<task type="auto">
  <name>Task 4: Create remaining adapters (SIPRI, UN Voting, UNHCR)</name>
  <files>src/adapters/sipri.py, src/adapters/un_voting.py, src/adapters/unhcr.py</files>
  <action>
Create SIPRIAdapter:
- Poll interval: 7 days (batch via Airflow)
- No official API - implement CSV download + parse
- Fetch arms trade register data
- Normalize to ConflictEvent (strategic developments category)

Create UNVotingAdapter:
- Poll interval: 30 days (per UNGA session)
- Fetch from unvoting.org API
- Track voting alignment between countries
- Normalize to ConflictEvent (diplomatic tension events)

Create UNHCRAdapter:
- Poll interval: 12 hours
- Fetch refugee population statistics
- Track displacement flows as leading conflict indicators
- Normalize to ConflictEvent (demographics category) with refugee counts as fatalities proxy
  </action>
  <verify>
Run `python -c "from src.adapters.sipri import SIPRIAdapter; from src.adapters.un_voting import UNVotingAdapter; from src.adapters.unhcr import UNHCRAdapter; print('OK')"` to verify imports.
  </verify>
  <done>
All 7 source adapters implemented. Can fetch and normalize data to unified schema.
  </done>
</task>

</tasks>

<verification>
- All 7 adapters import without errors
- Base adapter interface is consistent across all implementations
- Adapter registry can list and retrieve all adapters
</verification>

<success_criteria>
7 modular source adapters implemented with consistent interface. All normalize to unified schema.
</success_criteria>

<output>
After completion, create `.planning/phases/01-data-foundation/01-data-foundation-02-SUMMARY.md`
</output>
