# Domain Pitfalls: Conflict Prediction and Early Warning Systems

**Domain:** Conflict prediction / political violence early warning systems  
**Researched:** March 2026  
**Confidence:** MEDIUM-HIGH (multiple peer-reviewed sources + institutional reports)

---

## Executive Summary

Conflict prediction systems face a fundamental paradox: they excel at detecting patterns in historical data but struggle to translate predictions into actionable intelligence. Research reveals that the most sophisticated ML models often fail to outperform simple autoregressive baselines that predict future violence from recent past violence. The critical failure modes in this domain are not primarily technical but organizational and epistemological—systems fail when they cannot connect warning to response, when they generate false confidence through precision metrics that mask poor calibration, or when they assume that explanatory variables (GDP, regime type) can serve as predictive ones.

---

## Critical Pitfalls

Mistakes that cause rewrites or major issues in conflict prediction projects.

### Pitfall 1: The Warning-Response Gap

**What goes wrong:** The system produces accurate predictions that go unheeded or unactionable.

**Why it happens:** 
- Structural barriers: limited political will, ambiguous mandates, siloed institutions
- The "urgency trap": decision-makers respond only when crises become visible and costs become unavoidable
- Predictions lack clear action pathways or threshold triggers

**Consequences:**
- System becomes irrelevant; analysts ignore outputs
- Erosion of organizational trust in "crying wolf" predictions
- The prediction capability exists but produces no preventive action

**Prevention:** 
- Design predictions with explicit action triggers from the start
- Build decision-maker personas into system design (UN/NATO vs NGO vs journalist have different response capacities)
- Include "recommended actions" in output, not just probability scores
- Test system with actual decision-makers during development, not just validation

**Detection:** 
- Track time-to-action after warnings; if predictions accumulate without response, gap exists
- Survey analyst users: "What did you do with this prediction?" vs. "Did the prediction help?"

**Phase Mapping:** This pitfall primarily manifests in the **Output & Delivery phase** when building user-facing dashboards and briefings. However, the technical design choices (precision vs. recall tradeoffs, threshold calibration) are made earlier in the **ML Pipeline phase**.

---

### Pitfall 2: Structural Covariate Illusion

**What goes wrong:** Building complex ML models with dozens of structural features (GDP, ethnic composition, regime type) that add minimal or negative predictive value.

**Why it happens:** 
- Confusing explanatory power with predictive power
- Academic literature emphasizes "root causes" but these are slow-moving, poorly suited for short-term prediction
- The research shows autoregressive models (past violence predicts future violence) match or outperform structurally-enriched models

**Consequences:**
- Wasted development effort on data collection for features that don't improve predictions
- Models become more complex without accuracy gains
- Overfitting to historical patterns that don't generalize

**Prevention:**
- Establish autoregressive baseline FIRST before adding covariates
- Test whether any new feature actually improves out-of-sample MAE/RMSE
- Use the EPJ Data Science 2025 benchmark: if covariate-only model has 30% higher MAE than AR-only, reconsider the feature set

**Detection:**
- Feature importance scores show structural covariates have near-zero importance after autoregressive terms
- Out-of-sample validation shows no improvement over AR baseline
- Cross-validation performance degrades with more covariates (indicating overfitting)

**Phase Mapping:** This pitfall is core to the **ML Pipeline Design phase**. Teams should run AR-only baseline experiments before architectural decisions.

---

### Pitfall 3: The Cry Wolf / False Alarm Fatigue

**What goes wrong:** High-recall systems that flag every potential conflict generate so many false positives that analysts desensitize to warnings.

**Why it happens:** 
- Class imbalance: 85%+ of country-months have zero conflict fatalities
- Optimizing for "never miss a conflict" produces many false alarms
- No calibration of confidence scores to actual probabilities

**Consequences:**
- Trust collapse: "Your system always says high risk; nothing happens"
- Analyst override: users tune out predictions entirely
- Resource misallocation: response teams burn out on false alarms

**Prevention:**
- Calibrate probability outputs against historical base rates
- Accept that perfect recall is impossible; optimize for precision at reasonable recall
- Provide confidence intervals, not point estimates
- Implement explicit "uncertainty" flags for borderline cases

**Detection:**
- Track false positive rates over time
- Monitor "dismissal rates" if system provides override tracking
- Compare predicted probabilities to observed frequencies (Brier score)

**Phase Mapping:** Critical in the **Output Calibration phase** and requires iteration with user feedback. The technical ML work happens earlier, but the failure mode surfaces in **Deployment & User Testing**.

---

### Pitfall 4: Data Quality Mismatch

**What goes wrong:** Building system on aggregated global datasets (ACLED, UCDP) without understanding geographic/sectoral coverage gaps.

**Why it happens:** 
- Event data reflects journalistic coverage and coding decisions, not ground truth
- Coverage is highly uneven: well-covered regions (Middle East, Ukraine) vs. blind spots (rural regions, certain conflict types)
- Lag between events and data availability undermines "real-time" claims

**Consequences:**
- Predictions for poorly-covered regions may be based on data artifacts
- System inherits coder bias in event classification
- "Real-time" claims don't hold for data latency (often weeks-months)

**Prevention:**
- Audit coverage metrics by region before using any dataset
- Document data latency expectations explicitly
- Combine multiple sources (ACLED + ICEWS + VIEWS) for triangulation
- Build uncertainty estimates that reflect data quality

**Detection:**
- Compare event density maps to known coverage gaps
- Analyze cross-source agreement on key events
- Flag predictions for regions with <X events/year

**Phase Mapping:** This is a **Data Pipeline phase** consideration. Data quality auditing should be completed before feature engineering begins.

---

### Pitfall 5: Predictive Optimism / Overclaiming

**What goes wrong:** Stating system capabilities that exceed what models can deliver; confusing in-sample fit with out-of-sample prediction.

**Why it happens:** 
- Academic papers often report AUC/accuracy without calibration metrics
- Leaders expect "AI can predict conflicts" (as if deterministic)
- Temporal validation may use data leakage (future information in training)

**Consequences:**
- When predictions fail, loss of credibility is disproportionate to technical shortfall
- Stakeholders make commitments based on inflated expectations
- System gets abandoned after first high-profile miss

**Prevention:**
- Report calibration metrics (Brier score, reliability diagrams) alongside AUC
- Use walk-forward validation with strict temporal separation
- Under-promise: say "historically, X% of similar situations escalated" rather than "AI predicts conflict"
- Explicitly communicate uncertainty ranges, not point predictions

**Detection:**
- Compare predicted probabilities to observed frequencies
- Track calibration drift over time
- Run backtests on events system wasn't designed for

**Phase Mapping:** This pitfall cuts across **ML Pipeline Design** (validation methodology) and **Stakeholder Communication** (output framing). It is primarily an organizational/institutional pitfall.

---

### Pitfall 6: Ignoring Endogenous Conflict Dynamics

**What goes wrong:** Building models that assume conflict is exogenously triggered (by structural factors) rather than self-reinforcing.

**Why it happens:** 
- Theories emphasize "root causes" (poverty, ethnic division) that are slow-moving
- ML frameworks default to supervised learning on static features
- Feedback loops (retaliation, repression spiral) aren't modeled

**Consequences:**
- Models can't capture escalation dynamics; they only capture background risk
- The most dangerous dynamics (rapid escalation from baseline) are systematically underpredicted
- Predictions are too slow to react to emerging situations

**Prevention:**
- Include lagged outcome variables (recent violence as predictor)
- Model explicitly for regime shifts, not just continuous risk
- Incorporate temporal patterns (conflict clustering, burstiness)
- Consider agent-based modeling for escalation dynamics

**Detection:**
- Autocorrelation analysis shows strong temporal dependencies
- Model residuals show systematic underprediction during escalation phases
- Accuracy drops during periods of rapid change

**Phase Mapping:** This is core to the **ML Pipeline Design phase**—feature engineering should include temporal dependence. Also relevant to **Architecture** (considering feedback loops in system design).

---

## Moderate Pitfalls

### Pitfall 7: Precision Metric Myopia

**What goes wrong:** Optimizing for AUC or F1-score without asking whether these metrics matter for the use case.

**Why it happens:** 
- Academic literature uses AUC as primary metric
- Real decisions are threshold-based ("should we deploy resources?")
- Class imbalance makes AUC misleading (can be high with poor calibration)

**Consequences:**
- System recommends action at wrong threshold
- High AUC doesn't translate to trustworthy probabilities
- Decision-makers receive "0.73 probability" with no calibration to what that means

**Prevention:**
- Report calibration curves, not just AUC
- Choose metrics aligned with operational decisions (e.g., "At 80% recall threshold, precision is X%")
- Test with actual decision thresholds, not abstract metrics

**Detection:**
- Compare probability outputs to observed frequencies by bin
- Track operational outcomes: "When system said >50%, did conflict occur?"

### Pitfall 8: Subnational Resolution Mismatch

**What goes wrong:** Predicting at national level when analysts need subnational precision.

**Why it happens:** 
- Most datasets (UCDP, PRIO) are country-level
- National-level predictions obscure regional variation
- Users need actionable geographic specificity

**Consequences:**
- "High risk for Myanmar" is not actionable
- Analysts must translate national prediction to local decision
- Miss the most important variations within countries

**Prevention:**
- Build at subnational resolution from start (ADM1/ADM2 level)
- Aggregate to national only for summary dashboards
- Include geographic uncertainty in outputs

### Pitfall 9: One-Size-Fits-All Model

**What goes wrong:** Training single global model when conflict dynamics vary by region/type.

**Why it happens:** 
- Simpler to build one model; limited labeled data for regional models
- Assumes conflict is universal phenomenon with consistent drivers

**Consequences:**
- Model averages across heterogeneous dynamics
- Some regions systematically underperform
- Context-specific patterns (e.g., election violence, communal violence) not captured

**Prevention:**
- Train region-specific models where data permits
- Include regime/type indicators as features
- Validate separately by region and conflict type

---

## Minor Pitfalls

### Pitfall 10: Explanation Without Action

**What goes wrong:** Building sophisticated explainability (SHAP, LIME) that doesn't help decision-makers act.

**Why it happens:** 
- Technical teams focus on model interpretability
- "Why" matters less than "what should we do"
- Explanations may show drivers that are unchangeable

**Prevention:**
- Prioritize "recommended actions" over feature attributions
- If explaining, explain in terms of actionable drivers (recent events, escalation signals) not structural factors (ethnicity, GDP)

### Pitfall 11: Timeline Mismatch

**What goes wrong:** Building monthly predictions when users need weekly or daily for operational response.

**Why it happens:** 
- Data availability constrains temporal resolution
- Monthly aggregation is standard in academic datasets
- Real conflict dynamics unfold faster than monthly models capture

**Prevention:**
- Understand user timeline requirements early
- Use daily event data if available, even if predicting at monthly granularity
- Provide nowcasting alongside forecasting

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Data Pipeline | Data Quality Mismatch | Audit coverage, document latency, build uncertainty estimates |
| ML Pipeline Design | Structural Covariate Illusion | Run AR baseline first; test feature additions |
| ML Pipeline Design | Ignoring Endogenous Dynamics | Include lagged outcomes; model temporal dependence |
| Output Calibration | Cry Wolf / False Alarm Fatigue | Calibrate probabilities; balance precision/recall |
| Output & Delivery | Warning-Response Gap | Build action triggers; test with decision-makers |
| Stakeholder Communication | Predictive Optimism | Under-promise; report calibration metrics |
| Deployment & User Testing | False Alarm Fatigue | Track dismissal rates; iterate on thresholds |

---

## Key Sources

### Primary Academic Sources
- Chadefaux & Schincariol (2025) "Endogenous conflict and the limits of predictive optimization" EPJ Data Science — **HIGH confidence** — Peer-reviewed, demonstrates AR superiority
- Hegre et al. (2019) "ViEWS: A political violence early-warning system" Journal of Peace Research — **HIGH confidence** — Major system paper
- Ward et al. (2010) "The perils of policy by p-value" Journal of Peace Research — **HIGH confidence** — Critical of predictive overclaiming
- Bazzi et al. (2022) "The Promise and Pitfalls of Conflict Prediction" Review of Economics and Statistics — **HIGH confidence** — Empirical evidence from Colombia/Indonesia

### Institutional Reports
- NYU CIC (2025) "Warning Without Response: Why Early Warning Fails" — **MEDIUM-HIGH confidence** — Policy-focused synthesis
- HCSS (2022) "Practices, Principles and Promises of Conflict Early Warning Systems" — **MEDIUM confidence** — European security policy analysis

### Prediction Challenges
- VIEWS Prediction Challenge 2023/24 — **MEDIUM-HIGH confidence** — State of the art in conflict fatality prediction

---

## Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| Warning-Response Gap | HIGH | Documented across multiple institutional sources, not just technical |
| Structural Covariate Limitations | HIGH | Strong peer-reviewed evidence (EPJ Data Science 2025) |
| False Alarm/Cry Wolf | MEDIUM | Documented in related EWS domains (famine, flood), less specific to conflict |
| Data Quality Issues | HIGH | Well-documented for ACLED/UCDP |
| Predictive Optimism | MEDIUM | Academic consensus exists but requires more specific citation |
| Endogenous Dynamics | HIGH | Strong theoretical + empirical support |

---

## Open Questions for ConflictPulse

1. **What is the target temporal resolution?** If monthly, are predictions actionable for operational response? If weekly, is data available at that resolution?

2. **Who is the primary user and what are their response options?** The warning-response gap is different for UN analysts (diplomatic options), NATO (strategic), NGOs (humanitarian positioning), journalists (awareness).

3. **What constitutes "success"?** This domain has fundamental uncertainty; what is the acceptable false positive / false negative tradeoff for each user persona?

4. **Is the team planning for autoregressive baselines?** The research strongly suggests this should be the starting point, not a baseline to beat.

5. **What happens when predictions are wrong?** The first high-profile miss will test credibility. How will the team communicate uncertainty from the start?
