# ConflictPulse

## What This Is

A real-time conflict prediction and early warning platform that aggregates 12 independent data streams (social media, satellite imagery, economic indicators, arms trade data, diplomatic signals, refugee flows) to predict armed conflicts 1-6 months in advance with explainable AI outputs. Targets UN/NATO analysts, NGOs, journalists, and field workers who need actionable conflict risk intelligence.

## Core Value

Predict armed conflicts 1-6 months in advance with ranked causal chain explanations, enabling diplomatic intervention before violence erupts.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Real-time data ingestion from 12 sources
- [ ] Multilingual NLP pipeline for hate speech/threat detection
- [ ] Satellite change detection for military activity
- [ ] Time-series forecasting engine (6-month horizon)
- [ ] Signal fusion with Claude reasoning layer
- [ ] Risk scoring with confidence intervals
- [ ] Role-based access control (UN/NATO, NGO, Press)
- [ ] Alert delivery system (webhooks, SMS, email)

### Out of Scope

- [Hardware sensor network] — Field sensors (acoustic, seismic, drone) deferred to v2+ for operational complexity
- [Decryption capabilities] — RF monitoring analyzes volume only, not content
- [Real-time military command integration] — Alert delivery only, no bidirectional comms

## Context

**Domain:** Conflict prediction / early warning / geospatial intelligence

**Technical Environment:**
- Next.js 16.2.1 app (existing scaffold)
- Need backend for API aggregation (FastAPI recommended)
- TimescaleDB for time-series, PostGIS for geospatial
- Kafka for real-time event streaming

**Data Sources to Integrate:**
1. GDELT (real-time event stream)
2. ACLED (armed conflict data)
3. Sentinel-2 + SAR (satellite imagery)
4. SIPRI (arms trade)
5. UN voting records
6. Social media NLP (Reddit, Telegram, Twitter, YouTube)
7. IMF + World Bank economic indicators
8. UNHCR refugee flows
9. Radio Free Europe / VOA media monitoring
10. ADS-B + AIS (flight/maritime tracking)
11. VIIRS nighttime lights
12. Political leader speech corpus

**Implementation Priority:** Signal ingestion → AI processing → Prediction engine → Dashboards → Hardware extension (v2)

## Constraints

- **[Data Access]**: All sources must have free APIs — no paid data feeds for v1
- **[Latency]**: Target <15 min from signal to alert for real-time sources
- **[Accuracy]**: Backtesting required — system must validate against historical conflicts
- **[Privacy]**: Border sensors count individuals anonymously (no facial recognition)
- **[Explainability]**: Every risk score needs causal chain explanation (not black box)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude as reasoning layer | Cross-signal synthesis requires LLM reasoning | — Pending |
| 12-source minimum | Single-source systems have high false positive rates | — Pending |
| 6-month prediction horizon | Based on academic research on conflict precursors | — Pending |
| Role-based access tiers | Different stakeholders need different granularity | — Pending |

---
*Last updated: 2026-03-27 after project initialization*
