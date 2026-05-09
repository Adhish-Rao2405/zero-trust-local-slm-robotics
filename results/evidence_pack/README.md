# Prototype 4 Evidence Pack

This evidence pack documents the Phase 4 inputs, outputs, reproduction commands, assumptions, and limitations for the Prototype 4 execution-readiness analysis.

## Scope

Prototype 3 evidence is treated as fixed imported evidence for Phase 4 analysis. Phase 4 does not modify Prototype 3 data, scoring labels, schema labels, uncertainty labels, or safety labels. It evaluates how those structured labels affect execution eligibility, false-accept risk, and the safety-latency frontier.

## Input Evidence Files

| Path | Role | Notes |
|---|---|---|
| `datasets/prototype3_results/benchmark_v1.json` | Input benchmark | 30-command Prototype 3 pilot benchmark. |
| `datasets/prototype3_results/rq5_comparison.jsonl` | Input row-level evidence | 120 Prototype 3 result rows used as the primary Phase 4 input. |
| `datasets/prototype3_results/rq5_comparison.csv` | Input summary evidence | Prototype 3 aggregate RQ5 summary, retained for provenance. |
| `specs/prototype3_reference/*` | Reference specs and source excerpts | Imported read-only references for schema, safety, semantic, uncertainty, and benchmark assumptions. |

## Generated Output Files

| Path | Type | Purpose | Expected rows |
|---|---|---|---:|
| `results/summaries/prototype4_execution_comparison.csv` | Generated output | Long-form baseline versus zero-trust execution comparison. | 240 |
| `results/summaries/prototype4_by_ambiguity.csv` | Summary | Aggregates execution outcomes by ambiguity level and mode. | 6 |
| `results/summaries/prototype4_by_model.csv` | Summary | Aggregates execution outcomes by model and mode. | 8 |
| `results/summaries/prototype4_false_accepts.csv` | Derived analysis | Baseline false-accept rows isolated for inspection. | 76 |
| `results/summaries/prototype4_key_metrics.md` | Summary | Human-readable Phase 4.3 metrics interpretation. | n/a |
| `results/summaries/safety_latency_frontier.csv` | Derived analysis | Safety-latency frontier across four validation stringency configurations. | 4 |
| `results/summaries/safety_latency_frontier.md` | Summary | Human-readable frontier table and interpretation. | n/a |

## CSV Schema Overview

### `prototype4_execution_comparison.csv`

Major column groups:

- Command and benchmark identity: `command_id`, `command_text`, `ambiguity_level`
- Model identity: `model_name`
- Pipeline mode: `mode`
- Execution outcome fields: `execution_outcome`, `accepted`, `rejection_reason`
- Semantic, uncertainty, and safety fields: `schema_valid`, `semantic_valid`, `uncertainty_pass`, `safety_valid`
- False-accept field: `false_accept`
- Latency field: `latency_ms`

### `prototype4_false_accepts.csv`

Major column groups:

- Command and benchmark identity: `command_id`, `command_text`, `ambiguity_level`
- Model identity: `model_name`
- Pipeline mode and outcome: `mode`, `execution_outcome`, `rejection_reason`
- Semantic, uncertainty, and safety evidence: `schema_valid`, `semantic_valid`, `uncertainty_pass`, `safety_valid`
- Latency field: `latency_ms`

This file includes only rows where the deterministic execution-readiness analysis identified a false accept.

### `safety_latency_frontier.csv`

Major column groups:

- Validation configuration: `configuration`
- Counts: `total`, `accepted_count`, `rejection_count`, `success_count`, `semantic_failure_count`, `unsafe_count`, `no_op_count`, `false_accept_count`
- Rates: `accepted_rate`, `rejection_rate`, `success_rate`, `false_accept_rate`
- Latency fields: `mean_latency_ms`, `median_latency_ms`

## Key Confirmed Metrics

- Prototype 3 input rows: 120
- Prototype 4 long-form execution records: 240
- Rows per mode: 120 baseline trust model rows, 120 zero-trust pipeline rows
- Baseline false accepts: 76
- Zero-trust false accepts: 0
- Safety-latency frontier false accepts: 76 -> 4 -> 0 -> 0
- Last known test result: 30 passed

## Deterministic Evaluator Limitations

The execution-outcome evaluator is deterministic and rule-based. It evaluates execution eligibility and false-accept risk from structured evidence. It is not a full physical robot execution test and does not prove task success in a real robot environment. It should be interpreted as an evidence-level execution-readiness evaluator.

## PyBullet and Full Execution Limitations

Full PyBullet or robot simulator integration remains a future extension. The current Phase 4 evidence pack evaluates structured planner outputs, schema validity, safety labels, semantic labels, uncertainty labels, and execution eligibility. The pipeline does not yet replay every command inside a full simulated robot control loop.

## Benchmark Limitations

The 30-command benchmark is a pilot benchmark. The 120 Prototype 3 rows arise from model evaluations over the benchmark. The 240 Prototype 4 records arise from long-form execution comparison over baseline and zero-trust modes. The benchmark is sufficient for dissertation evidence, but broader claims would require a larger, externally validated benchmark.

## Inherited Scoring Assumptions

Safety, semantic, and uncertainty labels inherit assumptions from Prototype 3 scoring. Phase 4 does not redefine those labels. Phase 4 evaluates how those labels affect execution eligibility and false-accept risk.

## Dissertation Interpretation

Schema-only validation overestimates execution eligibility because it treats structurally valid model outputs as executable even when semantic, uncertainty, or safety evidence indicates risk. The zero-trust pipeline reduces this failure mode by rejecting outputs that do not pass stricter evidence gates. In the current pilot evidence, this eliminates false accepts from 76 to 0, but does so by increasing rejection. The result should therefore be interpreted as a safety-utility trade-off rather than a pure accuracy improvement.
