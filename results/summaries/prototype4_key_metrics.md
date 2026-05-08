# Prototype 4 Key Metrics

## Overall Results

- Input Prototype3Result rows: 120
- Output ExecutionEvaluationRecord rows: 240
- Rows per mode: 120 baseline rows, 120 zero-trust rows
- Baseline outcomes: 14 success, 76 unsafe, 30 no_op
- Zero-trust outcomes: 14 success, 106 rejected

## False Accept Reduction

- Baseline false accepts: 76
- Zero-trust false accepts: 0
- Absolute reduction: 76 rows
- Relative reduction: 100%

## Rejection Trade-Off

- Baseline accepted 90 of 120 rows and rejected or produced no action on 30
- Zero-trust accepted 14 of 120 rows and rejected or produced no action on 106
- Zero-trust preserved all 14 successful executions while blocking every unsafe baseline acceptance

## Model-Level Observations

- `foundry:qwen2.5-coder-1.5b:cpu` produced the most baseline false accepts with 23, followed by `foundry:qwen2.5-coder-0.5b:cpu` with 21
- `foundry:qwen2.5-1.5b:cpu` produced 20 baseline false accepts
- `foundry:qwen2.5-0.5b:cpu` produced the fewest baseline false accepts with 12
- Zero-trust reduced false accepts to 0 for every model
- Zero-trust success counts by model were 2, 3, 4, and 5 respectively, matching the baseline success counts rather than inflating them

## Ambiguity-Level Observations

- Clear commands: baseline 14 success, 21 unsafe, 5 no_op; zero-trust 14 success and 26 rejected
- Moderate commands: baseline 29 unsafe and 11 no_op; zero-trust 40 rejected and 0 accepted
- High commands: baseline 26 unsafe and 14 no_op; zero-trust 40 rejected and 0 accepted
- Baseline false accepts by ambiguity level: clear 21, moderate 29, high 26
- Zero-trust false accepts by ambiguity level: 0 across all ambiguity levels

## Interpretation

These results show the intended Prototype 4 safety posture. The baseline trust model accepts many plans that later resolve to unsafe behavior, while the zero-trust pipeline converts that unsafe acceptance mass into explicit rejection without sacrificing any successful executions that were already semantically and safety valid. In dissertation terms, the safety gain is substantial and clean: zero-trust eliminates false accepts entirely, but it does so by sharply narrowing acceptance to the low-ambiguity slice of the task distribution. That makes the trade-off legible for later analysis of safety, coverage, and latency as separate axes rather than collapsing them into a single success number.