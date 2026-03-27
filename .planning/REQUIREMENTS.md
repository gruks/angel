# Requirements: ConflictPulse

**Defined:** 2026-03-27
**Core Value:** Predict armed conflicts 1-6 months in advance with ranked causal chain explanations, enabling diplomatic intervention before violence erupts.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Data Ingestion

- [ ] **DATA-01**: User can ingest data from GDELT real-time event stream API
- [ ] **DATA-02**: User can ingest data from ACLED armed conflict database
- [ ] **DATA-03**: User can ingest data from IMF economic indicators API
- [ ] **DATA-04**: User can ingest data from World Bank economic indicators API
- [ ] **DATA-05**: User can ingest data from SIPRI arms trade register
- [ ] **DATA-06**: User can ingest data from UN voting records API
- [ ] **DATA-07**: User can ingest data from UNHCR refugee flow tracker API
- [ ] **DATA-08**: Data pipeline normalizes all sources to common event schema
- [ ] **DATA-09**: Kafka event bus handles real-time stream from all sources

### Prediction Engine

- [ ] **PRED-01**: System generates 1-month conflict probability forecasts per region
- [ ] **PRED-02**: System generates 3-month conflict probability forecasts per region
- [ ] **PRED-03**: System generates 6-month conflict probability forecasts per region
- [ ] **PRED-04**: System provides confidence intervals for all predictions
- [ ] **PRED-05**: Autoregressive baseline model runs for comparison
- [ ] **PRED-06**: System captures temporal dependencies in conflict patterns

### NLP Processing

- [ ] **NLP-01**: System performs multilingual text classification across 100+ languages
- [ ] **NLP-02**: System detects hate speech and dehumanization language
- [ ] **NLP-03**: System detects threat language in social media and news
- [ ] **NLP-04**: System performs sentiment/tone analysis on media content

### Satellite Processing

- [ ] **SAT-01**: System detects changes in satellite imagery over time
- [ ] **SAT-02**: System identifies new construction at military sites
- [ ] **SAT-03**: System detects nighttime light intensity changes
- [ ] **SAT-04**: System processes Sentinel-2 optical imagery (10m resolution)
- [ ] **SAT-05**: System processes SAR satellite imagery (cloud-penetrating)

### Geospatial Visualization

- [ ] **GEOV-01**: User can view interactive globe with risk heatmaps
- [ ] **GEOV-02**: User can drill down from continent to region to city
- [ ] **GEOV-03**: User can view historical conflict event overlays
- [ ] **GEOV-04**: User can view prediction overlays on geographic map
- [ ] **GEOV-05**: System uses H3 hexagonal grid for spatial aggregation

### Signal Fusion

- [ ] **SF-01**: System correlates signals across multiple data sources
- [ ] **SF-02**: System identifies escalation patterns from combined signals
- [ ] **SF-03**: System generates causal chain explanations for risk scores

### Explainable AI (KEY DIFFERENTIATOR)

- [ ] **AI-01**: Each risk score includes ranked list of contributing signals
- [ ] **AI-02**: System generates plain-English causal chain explanations
- [ ] **AI-03**: User can see which signals most influenced each prediction
- [ ] **AI-04**: System provides confidence intervals with causal context

### API Access

- [ ] **API-01**: REST API exposes predictions, events, and risk scores
- [ ] **API-02**: WebSocket API provides real-time prediction updates
- [ ] **API-03**: API supports programmatic filtering by region and date range
- [ ] **API-04**: API returns machine-readable JSON format
- [ ] **API-05**: API includes OpenAPI documentation

### Alert System

- [ ] **ALERT-01**: System sends webhook alerts when risk thresholds crossed
- [ ] **ALERT-02**: System sends email alerts for risk escalations
- [ ] **ALERT-03**: System sends SMS alerts for critical risk events
- [ ] **ALERT-04**: User can configure alert thresholds per region
- [ ] **ALERT-05**: User can filter alerts by threat level

### Role-Based Access Control

- [ ] **RBAC-01**: UN/NATO tier sees full signal breakdown and causal chains
- [ ] **RBAC-02**: NGO tier sees regional risk and pre-positioning recommendations
- [ ] **RBAC-03**: Press tier receives embeddable widgets and weekly summaries
- [ ] **RBAC-04**: User authentication with JWT tokens
- [ ] **RBAC-05**: Rate limiting per access tier

### Data Export

- [ ] **EXPT-01**: User can export predictions as CSV
- [ ] **EXPT-02**: User can export predictions as JSON
- [ ] **EXPT-03**: User can export historical conflict data
- [ ] **EXPT-04**: Export includes causal chain metadata

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Additional Data Sources

- **DATA-10**: Social media NLP (Reddit, Telegram, Twitter, YouTube)
- **DATA-11**: ADS-B flight tracking for military movements
- **DATA-12**: AIS maritime tracking for naval activity
- **DATA-13**: Political leader speech corpus analysis
- **DATA-14**: Radio Free Europe / VOA media monitoring

### Advanced Features

- **AI-05**: Interactive AI chat analyst for natural language exploration
- **AI-06**: Multi-scenario forecasts with alternative outcomes
- **AI-07**: Actor behavior modeling (government, armed groups)
- **GEOV-06**: 3D terrain visualization
- **GEOV-07**: Drone imagery gap-filling between satellite passes

### Hardware Integration (Field Sensors)

- **HW-01**: Acoustic sensor nodes (gunshot/explosion detection)
- **HW-02**: Seismic sensors (artillery/explosion ground signature)
- **HW-03**: Crowd-sourced field reporter app
- **HW-04**: Border crossing population flow sensors
- **HW-05**: RF monitoring stations (signal volume analysis)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Decryption capabilities | RF monitoring analyzes volume only, not content — ethical and legal constraints |
| Real-time military command integration | Alert delivery only, no bidirectional comms — security concerns |
| Facial recognition on sensors | Privacy-preserving design; border sensors count anonymously |
| Mobile app | Web-first, responsive design sufficient for v1 |
| Paid data sources | All v1 sources must have free APIs |
| Sub-minute latency | 15-minute target sufficient for conflict prediction |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 to DATA-09 | Phase 1 | Pending |
| PRED-01 to PRED-06 | Phase 2 | Pending |
| NLP-01 to NLP-04 | Phase 2 | Pending |
| SAT-01 to SAT-05 | Phase 2 | Pending |
| GEOV-01 to GEOV-05 | Phase 3 | Pending |
| SF-01 to SF-03 | Phase 3 | Pending |
| AI-01 to AI-04 | Phase 4 | Pending |
| API-01 to API-05 | Phase 3 | Pending |
| ALERT-01 to ALERT-05 | Phase 3 | Pending |
| RBAC-01 to RBAC-05 | Phase 3 | Pending |
| EXPT-01 to EXPT-04 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 52 total
- Mapped to phases: 52
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-27*
*Last updated: 2026-03-27 after auto-mode research synthesis*
