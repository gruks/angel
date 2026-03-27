# Research Summary: ConflictPulse

**Project:** ConflictPulse - Real-Time Conflict Prediction Platform  
**Domain:** Conflict Prediction / Early Warning Systems  
**Researched:** 2026-03-27  
**Overall confidence:** HIGH

## Executive Summary

ConflictPulse is a real-time conflict prediction platform that aggregates 12 independent data streams (social media, satellite imagery, economic indicators, arms trade data, diplomatic signals, refugee flows) to predict armed conflicts 1-6 months in advance with explainable AI outputs.

The conflict prediction domain has matured significantly, with established players (ACLED CAST, VIEWS, Warcast) but a critical gap: **no platform provides causal chain explanations** for predictions. All competitors produce black-box scores that lose analyst trust. ConflictPulse's key differentiator is explainable AI with ranked causal chains.

Research reveals a surprising finding: simple autoregressive models (past violence predicts future violence) match or outperform complex ML models with structural covariates (GDP, ethnic composition, regime type). This has major implications for the ML pipeline phase structure.

## Key Findings

**Stack:** FastAPI + TimescaleDB/PostGIS + Kafka/Airflow + XLM-RoBERTa/YOLOv8 + Deck.gl/Mapbox. Version recommendations verified March 2026.

**Table Stakes:** Conflict event data, prediction engine, geographic visualization, risk scoring, real-time updates, API access, data export.

**Differentiator:** Explainable AI with causal chains — the critical gap no competitor fills.

**Critical Pitfall:** The "Warning-Response Gap" — systems predict accurately but produce no preventive action due to structural/organizational barriers. Design action triggers from Day 1.

**Architecture:** Pipeline-and-hub with clear layer separation (ingestion → ML → signal fusion → prediction → delivery).

## Roadmap Implications

Based on research, recommended phase structure:

1. **Phase 1: Data Foundation** — Ingestion layer, Kafka event bus, TimescaleDB + PostGIS
   - Addresses: Data ingestion from 12 sources
   - Avoids: Building ML pipeline before having normalized data to train on

2. **Phase 2: ML Pipeline Core** — NLP pipeline, basic forecasting
   - Addresses: Multilingual NLP, time-series forecasting
   - Avoids: Structural Covariate Illusion — run AR baseline first

3. **Phase 3: Signal Fusion** — Multi-source correlation, basic risk scoring
   - Addresses: Signal fusion with confidence intervals
   - Avoids: Black-box predictions — design causal chain generation

4. **Phase 4: API + Visualization** — REST API, Globe visualization
   - Addresses: Role-based access, alert delivery
   - Avoids: Warning-Response Gap — include action triggers in output

5. **Phase 5: Reasoning Layer** — Claude integration for causal chains
   - Addresses: Explainable AI (KEY DIFFERENTIATOR)
   - Avoids: Explanation Without Action — prioritize actionable drivers

6. **Phase 6: Hardware Extension** — Field sensors (defer to v2+)
   - Addresses: Acoustic/seismic sensors, drones
   - Avoids: Premature hardware integration

**Phase ordering rationale:**
- Data foundation first — everything depends on normalized data
- ML pipeline before fusion — need features before correlation works
- API/viz before reasoning — deliver value to users with working pipeline
- Reasoning layer last — most complex, benefits from working foundation

**Research flags for phases:**
- Phase 2 (ML Pipeline): Likely needs deeper research on autoregressive baseline vs. structural covariates
- Phase 5 (Reasoning Layer): Needs proof-of-concept for Claude causal chain generation

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | FastAPI 0.135.x, TimescaleDB 2.26.0, PostGIS 3.6.2 — all verified March 2026 |
| Features | HIGH | Table stakes validated by ACLED/VIEWS/Warcast; differentiator (causal chains) confirmed as market gap |
| Architecture | MEDIUM | Pipeline-and-hub pattern confirmed by multiple systems; component boundaries standard |
| Pitfalls | HIGH | Warning-Response Gap, Structural Covariate Illusion, Cry Wolf — all domain-specific and well-documented |

## Gaps to Address

1. **Autoregressive baseline vs. structural covariates**: Research strongly suggests AR outperforms structural models, but this needs validation in ConflictPulse context
2. **User timeline requirements**: Weekly/daily vs. monthly predictions — needs user research to determine
3. **Causal chain UX**: How exactly to present causal chains to analysts — needs user research in implementation
4. **Subnational resolution**: What geographic granularity is actionable for different user personas
5. **False positive tolerance**: What tradeoff is acceptable for UN/NATO vs. NGO vs. journalist

## Sources

- ACLED CAST: 6-month conflict forecasts — HIGH confidence
- VIEWS: Open-source early warning system — HIGH confidence
- Warcast: Real-time conflict intelligence — HIGH confidence
- PRIO 2024: Peer-reviewed comparison of early warning systems — HIGH confidence
- EPJ Data Science 2025: AR model superiority — HIGH confidence
- NYU CIC 2025: Warning-Response Gap — MEDIUM-HIGH confidence
