# Dissertation Results Paragraphs

## Execution Comparison

The execution comparison evaluated Prototype 3 planner outputs under two deterministic Phase 4 policies: a baseline trust model and a zero-trust pipeline. The baseline mode accepted structurally valid non-empty plans, while the zero-trust mode required schema, semantic, uncertainty, safety, and action-plan evidence before acceptance. Across 120 Prototype 3 rows, the comparison produced 240 long-form Prototype 4 execution records.

## False Accept Reduction

The primary safety result is the reduction in false accepts. The baseline trust model produced 76 false accepts, whereas the zero-trust pipeline produced 0. This indicates that structurally valid planner outputs can substantially overstate execution readiness when semantic, uncertainty, and safety evidence are not used as gates. The result should be interpreted as evidence of reduced false-accept risk, not as proof of physical task completion.

## Safety-Latency Frontier

The Safety-Latency frontier isolates the effect of progressively stricter validation. False accepts decreased from 76 under schema-only validation to 4 after adding semantic validation, and to 0 after adding uncertainty gating. Full zero-trust preserved the 0 false-accept result. This pattern demonstrates a safety-utility trade-off: stricter validation reduces unsafe acceptance, but narrows the set of accepted outputs.

## Ambiguity-Level Behaviour

Ambiguity strongly influenced acceptance behaviour. The zero-trust pipeline preserved successful low-risk executions while rejecting outputs in higher-ambiguity settings where the available evidence did not justify execution. This supports the use of ambiguity-stratified analysis for evaluating local SLM planning pipelines.

## Model-Level Behaviour

Model-level results show that false-accept risk is not only a model property. Different local models produced different rates of structurally valid but unsafe or semantically unsuitable outputs, yet the zero-trust pipeline reduced false accepts to zero across all models in the pilot evidence. This suggests that pipeline-level validation can mitigate model-level variation in safety-relevant behaviour.

## Reproducibility and Evidence Pack

The evidence pack records the imported Prototype 3 inputs, generated Prototype 4 outputs, reproduction commands, row counts, metrics, and file manifest. This makes the Phase 4 analysis auditable from the checked-in CSV, JSONL, Markdown, and manifest files.

## Limitations of Deterministic Execution Evaluation

The Phase 4 evaluator is deterministic and evidence-level. It uses structured planner outputs and inherited Prototype 3 labels for schema validity, semantic validity, uncertainty, and safety. It does not constitute physical robot validation, formal verification, or full simulator replay. The benchmark is pilot-scale, and broader claims would require a larger externally validated benchmark and physical or simulated execution studies.
