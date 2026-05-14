# Paper Figure and Table List

## Tables

### Table I: Main Method Comparison (aggregate)
- **Location**: Section IV-A
- **Metrics**: Avg Rate, Outage Prob, Beam Success, Return, Latency (ms)
- **Methods**: ProposedV2, Reactive, Belief-Aware Rollout, One-Step Predictive, Oracle
- **Status**: Data present in markdown; needs formatted IEEE table environment

### Table II: Scene Sweep Summary
- **Location**: Section IV-B
- **Metrics**: ProposedV2 Return, Reactive Return, Deficit, ProposedV2 Outage, Reactive Outage
- **Sweep points**: 16 configurations (4 blocker_density + 4 obs_noise + 4 blocker_speed + 4 reflection_strength)
- **Status**: Data present in markdown; needs formatted IEEE table environment

### Table III: Ablation Study
- **Location**: Section IV-C
- **Metrics**: Rate, Outage, Bsucc, Return, Delta Return
- **Variants**: ProposedV2 (Full), No LoS Guard, No Predictive Fallback, Reactive
- **Status**: Data present in markdown; needs formatted IEEE table environment

### Table IV: Blockage Event Recovery
- **Location**: Section IV-D
- **Metrics**: Avg Recovery (slots), Preemptive Switch Rate, Fallback Trigger Rate
- **Methods**: ProposedV2, Reactive, Belief-Aware Rollout, Oracle
- **Status**: Data present in markdown; needs formatted IEEE table environment

### Table V: Regime Boundaries Summary
- **Location**: Section V-F
- **Content**: Condition, Preferred Method, Reason
- **7 regime conditions**
- **Status**: Data present in markdown; needs formatted IEEE table environment

## Figures

### Figure 1: Return Difference vs Reactive Across Sweep Dimensions
- **Location**: Referenced in Section IV-B
- **Type**: Multi-panel bar or dot plot
- **Data source**: Table II return deficit column
- **Key annotation**: Mark failure regimes (negative deficits) in distinct color
- **Status**: Not rendered

### Figure 2: Outage Probability vs Observation Noise
- **Location**: Referenced in Section V-C
- **Type**: Line plot with two series (ProposedV2, Reactive)
- **Data source**: Section V-C noise spectrum table
- **Key annotation**: Cross-over region (obs_noise approx 0.03--0.04)
- **Status**: Not rendered

### Figure 3: Blocker Density Impact on Rate-Outage Tradeoff
- **Location**: Referenced in Section V-D
- **Type**: Scatter or dual-axis plot
- **Data source**: Section V-D blocker density table
- **Key annotation**: Return flip at density=3
- **Status**: Not rendered

## Figure/Table Generation Source Files

- Plot scripts: `claude/isac_uploaded_repo/repo/plot_results.py`
- Result CSVs: `claude/isac_uploaded_repo/repo/results/`
- Caption specs: `claude/isac_prediction_regime_project/06_writing/figure_table_captions_v0.md`
- Storyboard: `claude/isac_prediction_regime_project/06_writing/figure_table_storyboard.md`

## Cross-Reference Map

| Reference in Text | Actual Table/Figure | Status |
|---|---|---|
| "Table I" | Main method comparison | Data ready |
| "Table II" | Scene sweep summary | Data ready |
| "Table III" | Ablation study | Data ready |
| "Table IV" | Blockage recovery | Data ready |
| "Table V" | Regime boundaries | Data ready |
| "Figure 1" | Return difference vs Reactive | Not rendered |
| "Figure 2" | Outage vs observation noise | Not rendered |
| "Figure 3" | Blocker density impact | Not rendered |
