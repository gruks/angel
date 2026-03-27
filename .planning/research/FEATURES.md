# Feature Landscape

**Domain:** Conflict Prediction / Early Warning Platforms  
**Researched:** 2026-03-27  
**Confidence:** HIGH

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Conflict Event Data** | Core dataset - ACLED, GDELT, or equivalent | Low | Without verified conflict event data (battles, explosions, civilian targeting), the platform has no foundation. Must include historical + current. |
| **Conflict Forecasting/Prediction** | Primary value proposition | High | Predict conflict events 1-6 months ahead. Industry standard: ACLED CAST does 6-month forecasts; VIEWS does 1-36 months. Must have at least country-level, ideally subnational. |
| **Geographic Visualization** | Analysts work spatially | Medium | Interactive maps with risk heatmaps, subnational boundaries. Standard: Mapbox/Deck.gl with hexagonal binning (H3). Must show past events + predictions. |
| **Risk Score/Alert System** | Actionable thresholds | Low | Numeric risk scores (0-100), threat level categories (Critical/High/Moderate/Low). Warcast: Critical ≥90, High ≥50, Moderate ≥30, Low <30. |
| **Real-time Data Updates** | Freshness matters | Medium | Continuous data pipeline. Warcast: updates every 2 minutes. ACLED: monthly forecasts. VIEWS: monthly updates. |
| **API Access** | Analyst integration needs | Medium | Programmatic access for partner systems. ACLED offers API endpoints. VIEWS provides data downloads. |
| **Data Export** | Cross-referencing required | Low | CSV/JSON download for further analysis. All major platforms offer this. |

## Differentiators

Features that set product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Explainable AI (Causal Chains)** | Black-box scores lose analyst trust | High | **KEY DIFFERENTIATOR**. Warcast's Brain Score uses RAG but still lacks causal chain explanation. VIEWS research focuses on interpretability but doesn't provide causal chains to users. ConflictPulse can own this space by showing *why* a prediction was made. |
| **Interactive AI Chat Analyst** | Natural language exploration of predictions | Medium | Warcast's War Agent lets users ask questions in natural language. Claude-powered with tool access. Could be ConflictPulse differentiator if tied to causal explanations. |
| **Multi-scenario Forecasts** | Decision support under uncertainty | High | Warcast offers 48-hour predictions with escalation probabilities, alternative outcomes. VIEWS provides confidence intervals but not explicit scenarios. |
| **Actor Behavior Modeling** | Understanding escalation dynamics | High | Warcast models USA, Russia, China, NATO, Iran behavior based on historical patterns. No competitor offers this with causal chains. |
| **12 Diverse Data Streams** | Signal diversity improves accuracy | High | Single-source (news-only or ACLED-only) is vulnerable to gaps. Warcast aggregates 40+ news sources + ACLED + GDELT + social media. |
| **Confidence Intervals** | Uncertainty communication | Medium | VIEWS provides uncertainty estimates. Warcast tracks prediction confidence based on error patterns. Analysts need this for resource allocation decisions. |
| **Early Warning Signal Types** | Specific trigger identification | Medium | Warcast identifies 5 signal types: escalation, pattern match, anomaly, threshold, correlation. Helps analysts prioritize. |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Black-box Prediction Only** | Analysts cannot trust or act on opaque scores | Provide causal chain explanations linking drivers to predictions |
| **Historical Data Only** | No value without forward-looking component | Must have prediction component (minimum 1-month horizon) |
| **Consumer-Focused UX** | Target is UN/NATO/NGO analysts, not general public | Professional dashboard with detail layers, not simplified consumer view |
| **Single Data Source** | Gaps in coverage, no redundancy | Aggregate multiple sources (news + ACLED + GDELT + satellite + social) |
| **No Subnational Resolution** | Country-level too coarse for action | Provide provincial/regional-level predictions |
| **No Alert Customization** | Users need filtered, non-spam alerts | Allow source/region/threat-level filtering, cooldowns, delivery channel selection |
| **No API Access** | Analysts integrate into workflows | Provide REST API with proper authentication |
| **Real-time News Without Prediction** | Just a news aggregator, not a prediction platform | Always pair current events with forward-looking forecasts |

## Feature Dependencies

```
Data Ingestion → Data Processing → Prediction Engine → Visualization + Alerts
     ↓                ↓                   ↓                   ↓
  12 Streams     Normalization      Causal Chains       Dashboard
                 Entity Extract     Confidence          API
                 Deduplication      Scenarios           Alerts
```

```
Explainable AI Module → Causal Chain Visualization
         ↓                      ↓
  Model Interpretability ← Interactive Explorer
                    ↓
            Natural Language Explanation
```

## MVP Recommendation

Prioritize in order:

1. **Conflict Event Data** (ACLED integration) — Table stakes, foundational
2. **Basic Prediction Engine** (1-6 month forecasts) — Table stakes, core value
3. **Geographic Visualization** — Table stakes, how analysts work
4. **Risk Scoring + Alerts** — Table stakes, actionable output
5. **Explainable AI with Causal Chains** — KEY DIFFERENTIATOR — This is what makes ConflictPulse different from ACLED CAST and VIEWS

Defer:
- **Interactive AI Chat**: Can come in Phase 2 (needs prediction foundation first)
- **Multi-scenario Forecasts**: Complex, defer until basic predictions validated
- **Actor Behavior Modeling**: Research-heavy, defer to Phase 3

## Sources

- **ACLED CAST**: Conflict Alert System methodology and 6-month forecasts — HIGH confidence
- **VIEWS**: Violence Early-Warning System, 1-36 month predictions, open-source — HIGH confidence
- **Warcast**: Real-time conflict intelligence with ML scoring, War Agent, 48-hour forecasts — HIGH confidence
- **PRIO (2024)**: "A review and comparison of conflict early warning systems" — peer-reviewed academic — HIGH confidence
- **Anticipation Hub Catalogue**: 15+ early warning tools catalogued (UNEP, ACLED, WRI, Hatebase, etc.) — HIGH confidence
- **WRI Water-Peace-Security**: Machine learning methodology captures 86% of future conflicts — MEDIUM confidence
- **ConflictForecast.org**: Two-step ML using aggregated news — MEDIUM confidence

## Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| Table Stakes | HIGH | Multiple verified sources (ACLED, VIEWS, Warcast) agree on core features |
| Differentiators | HIGH | Clear gap in market: no platform offers causal chain explainability |
| Anti-Features | HIGH | Based on competitor analysis showing what exists vs. what ConflictPulse offers |
| Dependencies | MEDIUM | Inferred from platform architectures; may need validation in implementation |
| MVP Order | HIGH | Derived from competitive landscape analysis |

## Research Notes

The conflict prediction/early warning space has matured significantly since 2023. Key observations:

1. **Transparency crisis**: PRIO 2024 review calls out that most systems lack transparency in data/code access
2. **Explainability gap**: No major platform provides causal chain explanations (only confidence intervals)
3. **Multi-source is standard**: Warcast aggregates 40+ sources; single-source approaches are insufficient
4. **User-centric design matters**: Warcast's approach with War Agent shows demand for conversational exploration
5. **Humanitarian sector adoption**: VIEWS specifically targets practitioners; ConflictPulse should follow this pattern
