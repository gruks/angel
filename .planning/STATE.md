# STATE: ConflictPulse

**Last Updated:** 2026-03-27

---

## Project Reference

**Core Value:** Predict armed conflicts 1-6 months in advance with ranked causal chain explanations, enabling diplomatic intervention before violence erupts.

**Current Focus:** Roadmap created - 5 phases defined covering 52 v1 requirements

---

## Current Position

| Attribute | Value |
|-----------|-------|
| **Phase** | Planning - Roadmap Complete |
| **Plan** | 5 phases defined |
| **Status** | Awaiting Phase 1 Planning |
| **Progress** | 0% |

---

## Roadmap Overview

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 1 | Data Foundation | 9 | Not Started |
| 2 | ML Pipeline | 15 | Not Started |
| 3 | Signal Fusion & Core Features | 13 | Not Started |
| 4 | Delivery & Access | 14 | Not Started |
| 5 | Explainable AI | 4 | Not Started |

---

## Accumulated Context

### Key Decisions

| Decision | Status |
|----------|--------|
| FastAPI backend | Selected (from research) |
| TimescaleDB + PostGIS | Selected (from research) |
| Kafka for event streaming | Selected (from research) |
| 5-phase structure | Approved |
| Depth: Standard | Applied |

### Research Flags

- **Phase 2 (ML Pipeline):** Needs deeper research on autoregressive baseline vs. structural covariates
- **Phase 5 (Reasoning Layer):** Needs proof-of-concept for Claude causal chain generation

### Dependencies Between Phases

- Phase 1 (Data Foundation) → Phase 2 (ML Pipeline)
- Phase 2 (ML Pipeline) → Phase 3 (Signal Fusion)
- Phase 3 (Signal Fusion) → Phase 4 (Delivery & Access)
- Phase 4 (Delivery & Access) → Phase 5 (Explainable AI)

---

## Session Continuity

**Next Step:** `/gsd-plan-phase 1` to begin implementation of Data Foundation phase

**Pending Items:**
- None

**Blockers:**
- None

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| v1 Requirements Total | 52 |
| v1 Requirements Mapped | 52 (100%) |
| Phases Defined | 5 |
| Depth Setting | Standard |

---

*State updated: 2026-03-27 after roadmap creation*