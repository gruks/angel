# Architecture Patterns

**Domain:** Conflict Prediction / Early Warning Systems  
**Project:** ConflictPulse  
**Researched:** 2026-03-27

## Executive Summary

Conflict prediction systems require a layered architecture that handles heterogeneous data ingestion, multi-modal processing (NLP, computer vision, time-series), signal fusion with reasoning, and deliverable outputs for diverse stakeholders. Based on analysis of existing systems (VIEWS, Traversals, ACLED, GDELT), the recommended architecture follows a **pipeline-and-hub** pattern with clear component boundaries.

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Web App     │  │ API Gateway │  │ Globe View  │  │ Analyst Dashboard   │ │
│  │ (Next.js)   │  │             │  │ (WebGL)     │  │ (Drill-down)        │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SERVICE LAYER (API)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Alert        │  │ User         │  │ Prediction   │  │ Signal        │  │
│  │ Service      │  │ Service      │  │ Service      │  │ Service       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SIGNAL FUSION LAYER                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Reasoning Engine (Claude)                          │   │
│  │  - Multi-signal correlation                                         │   │
│  │  - Causal chain generation                                          │   │
│  │  - Confidence scoring                                               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ML PROCESSING LAYER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ NLP Pipeline│  │ CV Pipeline │  │ Forecasting │  │ Anomaly Detection│   │
│  │ - Hate speech│  │ - Satellite │  │ Engine      │  │                  │   │
│  │ - Threat det│  │ - Change det│  │ - 6-month   │  │                  │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ Stream      │  │ API         │  │ Bulk        │  │ Web             │   │
│  │ Sources     │  │ Adapters    │  │ Downloads   │  │ Scrapers        │   │
│  │ (Kafka)     │  │             │  │             │  │                 │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA STORAGE LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ TimescaleDB │  │ PostGIS     │  │ Redis       │  │ Object Storage   │   │
│  │ (time-series)│ │ (geo-spatial)│ │ (cache)    │  │ (satellite, etc)│   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **Data Ingestion Layer** | Pull/push from 12 sources, normalize to common schema | ML Processing, Kafka |
| **ML Processing Layer** | Transform raw signals into features (NLP, CV, forecasting) | Signal Fusion, Storage |
| **Signal Fusion Layer** | Correlate multi-source signals, generate explanations | ML Processing, Prediction Engine |
| **Prediction Engine** | Compute risk scores, confidence intervals, trend analysis | Signal Fusion, API Layer |
| **API Layer** | Serve data to clients, handle auth, rate limiting | Client Layer, Alert Service |
| **Alert Service** | Deliver notifications via webhook/SMS/email | Prediction Engine, External |
| **User Service** | Manage roles, permissions, organization hierarchy | API Layer, Storage |

### Data Flow

**Real-time Pipeline (sub-15 min latency):**
```
Source → Ingestion → Kafka Topic → ML Pipeline → Signal Fusion → Prediction → API → Client
         │
         └─→ TimeseriesDB (raw + processed)
```

**Batch Pipeline (hourly/daily):**
```
Bulk sources → ETL Job → Feature Store → Model Retraining → Updated predictions
                           │
                           └─→ PostGIS (geospatial features)
```

**Key Data Transformations:**
1. **Raw → Normalized**: Source-specific schema → Common event schema (similar to ACLED CAMEO codebook)
2. **Normalized → Features**: Text → embeddings, images → patches, metrics → aggregates
3. **Features → Signals**: Feature groups → risk indicators (e.g., "hate speech spike in region X")
4. **Signals → Predictions**: Signal weights + historical patterns → conflict probability + causal explanation

## Patterns to Follow

### Pattern 1: Event Codebook Normalization
**What:** Transform all incoming data into a unified event taxonomy
**When:** Handling heterogeneous sources (social media, satellite, economic)
**Example:**
```python
# Common schema after normalization
{
  "event_id": "uuid",
  "source": "gdelt|acled|social",
  "timestamp": "ISO8601",
  "location": {"lat": float, "lon": float, "region": str},
  "event_type": "protest|violence|diplomatic_tension|economic_stress",
  "confidence": float,  # 0-1
  "raw_data": {}  # preserved for audit
}
```

### Pattern 2: Federated Search with MLOps
**What:** Multi-source querying with continuous model training
**When:** Real-time monitoring across sources with evolving event types
**Why:** Traversals architecture demonstrates daily model retraining for new event categories
**Implementation:** Scheduled batch jobs pull data → label → train → deploy

### Pattern 3: Confidence-Aware Prediction Output
**What:** Every prediction includes confidence interval + causal chain
**When:** Delivering to decision-makers who need actionable intelligence
**Why:** VIEWS research emphasizes interpretability for humanitarian users

### Pattern 4: Two-Stage Alert Routing
**What:** Prediction triggers → Alert Service → Role-based delivery rules
**When:** Different stakeholders need different alert thresholds
**Example:**
```python
# UN/NATO: All alerts above 0.6 confidence
# NGO: Only alerts above 0.8 confidence in their regions
# Press: Aggregated weekly summaries only
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Monolithic ML Pipeline
**What:** Single model attempting to process all source types
**Why bad:** Different modalities (text, image, time-series) require specialized preprocessing; monolithic approach causes feature leakage and training instability
**Instead:** Modular pipeline with source-specific processors feeding into fusion layer

### Anti-Pattern 2: Point-to-Point Source Integration
**What:** Direct coupling between each source and prediction engine
**Why bad:** Adding new sources requires modifying prediction code; hard to test, debug, and scale
**Instead:** Source-agnostic event bus (Kafka) with standardized contracts

### Anti-Pattern 3: Black-Box Predictions
**What:** Model outputs probability without explanation
**Why bad:** Analysts cannot act on predictions they don't understand; lacks audit trail for humanitarian decisions
**Instead:** Generate causal chain alongside prediction (which signals triggered the alert)

### Anti-Pattern 4: Real-Time Only Architecture
**What:** Optimizing exclusively for sub-minute latency
**Why bad:** Conflict prediction requires historical context and batch features (e.g., 6-month trends); ignoring batch processing reduces accuracy
**Instead:** Lambda architecture with real-time + batch paths

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 1M users |
|---------|--------------|--------------|-------------|
| **Data Ingestion** | Single Kafka partition sufficient | 10+ partitions, source-specific consumers | Partition by source + region |
| **ML Processing** | Single worker per pipeline type | GPU cluster for CV, CPU for NLP | Distributed Ray/Dask cluster |
| **Storage** | Single TimescaleDB instance | Read replicas + write leader | TimescaleDB distributed + PostGIS cluster |
| **API** | Single API server | Load balancer + multiple instances | Global CDN + edge caching |
| **Alert Delivery** | Direct SMTP/push | Queue-based (Redis + workers) | Multi-region pub/sub |

## Build Order Implications

Based on component dependencies, suggest this phase ordering:

### Phase 1: Data Foundation
- Ingestion layer (sources → normalized events)
- Kafka event bus
- TimescaleDB + PostGIS storage
- *Rationale:* Everything depends on having normalized data available

### Phase 2: ML Pipeline Core
- NLP pipeline (one source first: GDELT or social media)
- Basic forecasting (simplified model)
- *Rationale:* Need features before fusion can work

### Phase 3: Signal Fusion
- Multi-source correlation
- Basic risk scoring
- *Rationale:* Requires both ingestion and ML outputs

### Phase 4: API + Visualization
- REST API layer
- Globe visualization (WebGL)
- *Rationale:* Delivers value to users; can mock ML outputs initially

### Phase 5: Reasoning Layer
- Claude integration for causal chains
- Confidence scoring refinement
- *Rationale:* Most complex, benefits from having working pipeline first

### Phase 6: Alert System + RBAC
- Alert delivery (webhooks, SMS)
- Role-based access control
- *Rationale:* Operational features for production use

## Sources

- VIEWS (Violence & Impacts Early-Warning System): https://viewsforecasting.org/ — Open-source conflict forecasting with ML pipeline
- Traversals Multi-Source Data Fusion Platform: https://traversals.com/products/multi-source-data-fusion-platform/ — Commercial real-time conflict monitoring
- ACLED (Armed Conflict Location & Event Data Project): https://www.acleddata.com/ — Industry-standard conflict event data
- GDELT (Global Database of Events, Language and Tone): https://www.gdeltproject.org/ — Real-time global event stream
- Research: "Next-Generation Conflict Forecasting: Spatiotemporal Learning" (arXiv, 2025)
- Research: "The role of AI for early warning systems" (ScienceDirect, 2025)