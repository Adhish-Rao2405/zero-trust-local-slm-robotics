# Figure Notes

## safety_latency_frontier.png

Source: `results/summaries/safety_latency_frontier.csv`. Columns used: `configuration`, `false_accept_count`, `mean_latency_ms`. Values are directly read from the frontier CSV. Latency is available as accepted-row mean latency.

## rejection_by_ambiguity.png

Source: `results/summaries/prototype4_execution_comparison.csv`. Columns used: `ambiguity_level`, `mode`, `execution_outcome`. Rejected counts are computed by counting `execution_outcome == rejected` for each ambiguity level and mode.

## model_comparison_heatmap.png

Source: `results/summaries/prototype4_execution_comparison.csv`. Columns used: `model_name`, `mode`, `schema_valid`, `semantic_valid`, `execution_outcome`, `false_accept`, `latency_ms`. Metrics are computed from available fields. No separate model-level uncertainty-valid rate is plotted because the selected heatmap prioritises schema rate, semantic rate, success count, false accepts, zero-trust rejected count, and mean latency.

## outcome_comparison_by_mode.png

Source: `results/summaries/prototype4_execution_comparison.csv`. Columns used: `mode`, `execution_outcome`. Outcome counts are computed directly from the CSV.

## false_accept_reduction.png

Source: `results/evidence_pack/metrics_manifest.json`. Values used: `baseline_false_accepts`, `zero_trust_false_accepts`. Values are confirmed by `prototype4_execution_comparison.csv`.

## pipeline_summary_metrics.png

Source: `results/evidence_pack/metrics_manifest.json`. This optional summary figure presents headline row counts, false-accept counts, and test result.
