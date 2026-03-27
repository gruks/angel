# ROADMAP: ConflictPulse

**Project:** ConflictPulse - Real-Time Conflict Prediction Platform  
**Core Value:** Predict armed conflicts 1-6 months in advance with ranked causal chain explanations, enabling diplomatic intervention before violence erupts.  
**Total v1 Requirements:** 52  
**Depth:** Standard (5-8 phases)

---

## Phase Structure

| Phase | Goal | Requirements | Success Criteria |
|-------|------|--------------|------------------|
| 1 - Data Foundation | User can ingest, normalize, and stream data from all 9 sources | DATA-01 to DATA-09 (9) | 5 criteria |
| 2 - ML Pipeline | System can process, analyze, and forecast conflict signals | PRED-01 to PRED-06, NLP-01 to NLP-04, SAT-01 to SAT-05 (15) | 5 criteria |
| 3 - Signal Fusion & Core Features | User can view fused signals, predictions, and interact with visualizations | SF-01 to SF-03, GEOV-01 to GEOV-05, API-01 to API-05 (13) | 5 criteria |
| 4 - Delivery & Access | User can receive alerts, export data, and access based on role | ALERT-01 to ALERT-05, RBAC-01 to RBAC-05, EXPT-01 to EXPT-04 (14) | 5 criteria |
| 5 - Explainable AI | User receives ranked causal chain explanations for every risk score | AI-01 to AI-04 (4) | 4 criteria |

---

## Phase Details

### Phase 1: Data Foundation

**Goal:** User can ingest, normalize, and stream data from all 9 sources.

**Dependencies:** None (foundation phase)

**Requirements (9):**
- DATA-01: GDELT real-time event stream API
- DATA-02: ACLED armed conflict database
- DATA-03: IMF economic indicators API
- DATA-04: World Bank economic indicators API
- DATA-05: SIPRI arms trade register
- DATA-06: UN voting records API
- DATA-07: UNHCR refugee flow tracker API
- DATA-08: Data pipeline normalizes all sources to common event schema
- DATA-09: Kafka event bus handles real-time stream from all sources

**Plans:** 3 plans

**Plan list:**
- [ ] 01-data-foundation-01-PLAN.md — Database schema, Pydantic event models, Kafka topics, config
- [ ] 01-data-foundation-02-PLAN.md — 7 data source adapters with normalization
- [ ] 01-data-foundation-03-PLAN.md — Ingestion orchestration, retry, health monitoring

**Success Criteria (5 observable behaviors):**
1. User can configure and activate each of the 7 data source connections
2. Data from all sources appears in the normalized event schema within 15 minutes of availability
3. Kafka event bus displays live stream of events from all connected sources
4. System logs and displays ingestion health status for each source
5. Failed ingestion attempts trigger automatic retry with notification

---

### Phase 2: ML Pipeline

**Goal:** System can process, analyze, and forecast conflict signals.

**Dependencies:** Phase 1 (requires normalized data)

**Requirements (15):**
- PRED-01: System generates 1-month conflict probability forecasts per region
- PRED-02: System generates 3-month conflict probability forecasts per region
- PRED-03: System generates 6-month conflict probability forecasts per region
- PRED-04: System provides confidence intervals for all predictions
- PRED-05: Autoregressive baseline model runs for comparison
- PRED-06: System captures temporal dependencies in conflict patterns
- NLP-01: System performs multilingual text classification across 100+ languages
- NLP-02: System detects hate speech and dehumanization language
- NLP-03: System detects threat language in social media and news
- NLP-04: System performs sentiment/tone analysis on media content
- SAT-01: System detects changes in satellite imagery over time
- SAT-02: System identifies new construction at military sites
- SAT-03: System detects nighttime light intensity changes
- SAT-04: System processes Sentinel-2 optical imagery (10m resolution)
- SAT-05: System processes SAR satellite imagery (cloud-penetrating)

**Success Criteria (5 observable behaviors):**
1. User can view 1-month, 3-month, and 6-month conflict probability forecasts for any region
2. Each forecast displays a confidence interval range (e.g., "72% ± 8%")
3. Multilingual text classification returns results in at least 100 languages
4. Hate speech, threat language, and sentiment analysis appear in the event pipeline
5. Satellite change detection alerts trigger when significant changes are detected

---

### Phase 3: Signal Fusion & Core Features

**Goal:** User can view fused signals, predictions, and interact with visualizations.

**Dependencies:** Phase 2 (requires processed signals)

**Requirements (13):**
- SF-01: System correlates signals across multiple data sources
- SF-02: System identifies escalation patterns from combined signals
- SF-03: System generates causal chain explanations for risk scores
- GEOV-01: User can view interactive globe with risk heatmaps
- GEOV-02: User can drill down from continent to region to city
- GEOV-03: User can view historical conflict event overlays
- GEOV-04: User can view prediction overlays on geographic map
- GEOV-05: System uses H3 hexagonal grid for spatial aggregation
- API-01: REST API exposes predictions, events, and risk scores
- API-02: WebSocket API provides real-time prediction updates
- API-03: API supports programmatic filtering by region and date range
- API-04: API returns machine-readable JSON format
- API-05: API includes OpenAPI documentation

**Success Criteria (5 observable behaviors):**
1. User can view a risk heatmap on an interactive globe and drill down to city level
2. Historical conflict events overlay correctly on geographic visualizations
3. REST API returns predictions and events in JSON format for programmatic access
4. WebSocket connection delivers real-time prediction updates to connected clients
5. OpenAPI documentation page is accessible and shows all available endpoints

---

### Phase 4: Delivery & Access

**Goal:** User can receive alerts, export data, and access based on role.

**Dependencies:** Phase 3 (requires API and visualizations)

**Requirements (14):**
- ALERT-01: System sends webhook alerts when risk thresholds crossed
- ALERT-02: System sends email alerts for risk escalations
- ALERT-03: System sends SMS alerts for critical risk events
- ALERT-04: User can configure alert thresholds per region
- ALERT-05: User can filter alerts by threat level
- RBAC-01: UN/NATO tier sees full signal breakdown and causal chains
- RBAC-02: NGO tier sees regional risk and pre-positioning recommendations
- RBAC-03: Press tier receives embeddable widgets and weekly summaries
- RBAC-04: User authentication with JWT tokens
- RBAC-05: Rate limiting per access tier
- EXPT-01: User can export predictions as CSV
- EXPT-02: User can export predictions as JSON
- EXPT-03: User can export historical conflict data
- EXPT-04: Export includes causal chain metadata

**Success Criteria (5 observable behaviors):**
1. User receives webhook, email, or SMS alerts when configured thresholds are crossed
2. User can configure alert thresholds per region and filter by threat level
3. User can log in and receive access based on their tier (UN/NATO, NGO, Press)
4. Rate limiting is enforced per access tier (visible via API 429 responses)
5. User can export predictions and historical data as CSV or JSON with causal chain metadata

---

### Phase 5: Explainable AI (KEY DIFFERENTIATOR)

**Goal:** User receives ranked causal chain explanations for every risk score.

**Dependencies:** Phase 4 (requires data export and full pipeline)

**Requirements (4):**
- AI-01: Each risk score includes ranked list of contributing signals
- AI-02: System generates plain-English causal chain explanations
- AI-03: User can see which signals most influenced each prediction
- AI-04: System provides confidence intervals with causal context

**Success Criteria (4 observable behaviors):**
1. Each risk score displays a ranked list of the top 5-10 contributing signals
2. Causal chain explanations are readable in plain English (non-technical)
3. User can identify which specific signals most influenced a prediction
4. Confidence intervals include contextual explanation of uncertainty factors

---

## Coverage Map

| Requirement ID | Phase | Requirement ID | Phase |
|----------------|-------|----------------|-------|
| DATA-01 | Phase 1 | NLP-02 | Phase 2 |
| DATA-02 | Phase 1 | NLP-03 | Phase 2 |
| DATA-03 | Phase 1 | NLP-04 | Phase 2 |
| DATA-04 | Phase 1 | SAT-01 | Phase 2 |
| DATA-05 | Phase 1 | SAT-02 | Phase 2 |
| DATA-06 | Phase 1 | SAT-03 | Phase 2 |
| DATA-07 | Phase 1 | SAT-04 | Phase 2 |
| DATA-08 | Phase 1 | SAT-05 | Phase 2 |
| DATA-09 | Phase 1 | GEOV-01 | Phase 3 |
| PRED-01 | Phase 2 | GEOV-02 | Phase 3 |
| PRED-02 | Phase 2 | GEOV-03 | Phase 3 |
| PRED-03 | Phase 2 | GEOV-04 | Phase 3 |
| PRED-04 | Phase 2 | GEOV-05 | Phase 3 |
| PRED-05 | Phase 2 | SF-01 | Phase 3 |
| PRED-06 | Phase 2 | SF-02 | Phase 3 |
| NLP-01 | Phase 2 | SF-03 | Phase 3 |

| Requirement ID | Phase | Requirement ID | Phase |
|----------------|-------|----------------|-------|
| API-01 | Phase 3 | EXPT-01 | Phase 4 |
| API-02 | Phase 3 | EXPT-02 | Phase 4 |
| API-03 | Phase 3 | EXPT-03 | Phase 4 |
| API-04 | Phase 3 | EXPT-04 | Phase 4 |
| API-05 | Phase 3 | AI-01 | Phase 5 |
| ALERT-01 | Phase 4 | AI-02 | Phase 5 |
| ALERT-02 | Phase 4 | AI-03 | Phase 5 |
| ALERT-03 | Phase 4 | AI-04 | Phase 5 |
| ALERT-04 | Phase 4 | | |
| ALERT-05 | Phase 4 | | |
| RBAC-01 | Phase 4 | | |
| RBAC-02 | Phase 4 | | |
| RBAC-03 | Phase 4 | | |
| RBAC-04 | Phase 4 | | |
| RBAC-05 | Phase 4 | | |

---

## Progress

| Phase | Name | Status |
|-------|------|--------|
| 1 | Data Foundation | Planned |
| 2 | ML Pipeline | Not Started |
| 3 | Signal Fusion & Core Features | Not Started |
| 4 | Delivery & Access | Not Started |
| 5 | Explainable AI | Not Started |

---

*Roadmap generated: 2026-03-27*
*Next: `/gsd-plan-phase 1` to begin implementation*