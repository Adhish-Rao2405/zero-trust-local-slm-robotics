# Prototype 4: Execution-Level Zero-Trust Evaluation and the Safety-Latency Frontier

Prototype 4 evaluates what would happen if schema-valid model plans were trusted directly, compared with a zero-trust policy that grants execution eligibility only after deterministic validation.

This repository contains the execution-readiness evidence pipeline for the Microsoft IXN dissertation. It imports fixed Prototype 3 results, compares trust-the-model execution against a deterministic zero-trust pipeline, and produces the safety-latency frontier used to discuss the trade-off between unsafe acceptance, rejection, and latency.

## 1. Purpose

Prototype 4 moves the dissertation evidence from plan validity toward execution-level readiness. It asks whether a model output that is structurally valid should be allowed to execute, or whether execution should require additional deterministic checks.

The core analysis measures:

- accepted and rejected plans
- successful execution-ready plans
- unsafe plans that would be falsely accepted by a baseline
- semantic, uncertainty, and safety gate effects
- latency over accepted rows
- safety-latency trade-offs across stricter validation configurations

## 2. Relationship to Prototype 3

Prototype 4 treats Prototype 3 as fixed imported evidence. It does not relabel, rescore, or modify Prototype 3 data.

Imported Prototype 3 evidence includes:

- `datasets/prototype3_results/benchmark_v1.json`
- `datasets/prototype3_results/rq5_comparison.jsonl`
- `datasets/prototype3_results/rq5_comparison.csv`
- `specs/prototype3_reference/`

Prototype 3 provides the benchmark commands, model outputs, schema validity, semantic labels, uncertainty labels, safety labels, and latency fields. Prototype 4 evaluates how those labels affect execution eligibility and false-accept risk.

## 3. Trust-the-Model vs Zero-Trust Comparison

Prototype 4 compares two execution policies over the same 120 imported Prototype 3 rows.

`baseline_trust_model` represents a trust-the-model policy. It treats schema-valid non-empty model plans as execution-eligible, then classifies whether the accepted plan would be successful, unsafe, semantically invalid, or a no-op.

`zero_trust_pipeline` represents deterministic zero-trust execution gating. It accepts a plan only when the plan passes schema, semantic, uncertainty, safety, and non-empty action-plan checks.

Recorded core results:

- 120 Prototype 3 input rows
- 240 Prototype 4 execution records
- 120 baseline rows and 120 zero-trust rows
- 76 baseline false accepts
- 0 zero-trust false accepts
- 14 successful executions preserved by zero trust

## 4. Execution Outcome Taxonomy

Prototype 4 uses deterministic execution-readiness outcomes rather than physical robot execution.

The main outcome categories are:

- `success`: the plan is accepted and satisfies the available semantic and safety evidence.
- `unsafe`: the plan is accepted by a policy but violates safety evidence.
- `semantic_failure`: the plan is accepted by a policy but violates semantic evidence.
- `no_op`: the model produced no executable action plan.
- `rejected`: the zero-trust policy blocked execution before the plan became execution-eligible.

A false accept is an accepted plan whose deterministic execution outcome is unsafe or semantically invalid.

## 5. Safety-Latency Frontier

The safety-latency frontier evaluates progressively stricter validation configurations:

| Configuration | Accepted | Rejected | Success | Unsafe | False accepts | Mean latency ms |
|---|---:|---:|---:|---:|---:|---:|
| `schema_only` | 90 | 30 | 14 | 76 | 76 | 5785.79 |
| `schema_semantic` | 18 | 102 | 14 | 4 | 4 | 6148.83 |
| `schema_semantic_uncertainty` | 14 | 106 | 14 | 0 | 0 | 6152.36 |
| `full_zero_trust` | 14 | 106 | 14 | 0 | 0 | 6152.36 |

The frontier shows that schema-only validation maximizes acceptance but admits many unsafe plans. Adding semantic and uncertainty checks sharply reduces false accepts, while full zero trust maintains zero false accepts at the cost of higher rejection.

## 6. Evidence Artefacts

Primary evidence is stored under `results/summaries/` and `results/evidence_pack/`.

Core summary outputs:

- `results/summaries/prototype4_execution_comparison.csv`
- `results/summaries/prototype4_by_ambiguity.csv`
- `results/summaries/prototype4_by_model.csv`
- `results/summaries/prototype4_false_accepts.csv`
- `results/summaries/prototype4_key_metrics.md`
- `results/summaries/safety_latency_frontier.csv`
- `results/summaries/safety_latency_frontier.md`

Evidence pack files:

- `results/evidence_pack/README.md`
- `results/evidence_pack/reproduction_commands.md`
- `results/evidence_pack/metrics_manifest.json`
- `results/evidence_pack/file_manifest.csv`

Dissertation-ready figures and tables are stored in:

- `figures/`
- `tables/`
- `results/writing_pack/`

## 7. How to Reproduce / Run Tests

Run commands from the repository root.

```bash
python scripts/run_prototype4.py
python scripts/run_safety_latency_frontier.py
python -m pytest tests -v --basetemp=tmp/pytest
```

Recommended reproduction order:

1. Confirm that the imported Prototype 3 files exist.
2. Run `python scripts/run_prototype4.py`.
3. Run `python scripts/run_safety_latency_frontier.py`.
4. Run `python -m pytest tests -v --basetemp=tmp/pytest`.
5. Inspect `results/summaries/` and `results/evidence_pack/`.

The evidence pack records a historical core test result of `30 passed`. Later optional extension phases add further tests under `tests/extensions/`.

## 8. Limitations

Prototype 4 is an evidence-level execution-readiness evaluator. It is deterministic and rule-based, and it evaluates structured planner outputs rather than running every command inside a physical robot or full PyBullet control loop.

Important limitations:

- The benchmark is a 30-command pilot benchmark.
- The 120 Prototype 3 rows come from model evaluations over that benchmark.
- Safety, semantic, and uncertainty labels are inherited from Prototype 3.
- Prototype 4 does not prove real-world robot task success.
- Broader safety claims would require a larger externally validated benchmark and simulator or physical execution replay.

## 9. Link to Prototype 5

Prototype 4 establishes the execution-level safety evidence and safety-latency frontier. Prototype 5 should build on this by moving beyond deterministic evidence evaluation toward a richer execution setting, such as simulator replay, online clarification, policy refinement, or deployment-oriented validation.

No Prototype 5 source directory is present in this repository at the time of this README update.

