# Table Notes

## key_metrics_summary

Source: `results/evidence_pack/metrics_manifest.json`. Supports the headline Phase 4 results summary. Values are read from the metrics manifest, which is derived from current output files where available.

## outcome_counts_by_mode

Source: `results/summaries/prototype4_execution_comparison.csv`. Supports comparison of baseline and zero-trust execution outcomes. Values are computed directly from the CSV.

## safety_latency_frontier

Source: `results/summaries/safety_latency_frontier.csv`. Supports the validation-stringency trade-off analysis. False-accept reduction is computed relative to the schema-only configuration.

## file_manifest_summary

Source: `results/evidence_pack/file_manifest.csv`. Supports reproducibility reporting by grouping evidence files into input, output, derived analysis, summary, evidence-pack, and documentation categories.
