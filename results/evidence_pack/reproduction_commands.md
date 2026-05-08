# Reproduction Commands

Run these commands from the repository root:

```bash
python scripts/run_prototype4.py
python scripts/run_safety_latency_frontier.py
python -m pytest tests -v --basetemp=tmp/pytest
```

## Recommended Reproduction Order

1. Confirm imported Prototype 3 files exist:

   ```bash
   python -c "from pathlib import Path; paths=['datasets/prototype3_results/benchmark_v1.json','datasets/prototype3_results/rq5_comparison.jsonl','datasets/prototype3_results/rq5_comparison.csv']; print({p: Path(p).exists() for p in paths})"
   ```

2. Run Prototype 4 execution comparison:

   ```bash
   python scripts/run_prototype4.py
   ```

3. Run Safety-Latency frontier analysis:

   ```bash
   python scripts/run_safety_latency_frontier.py
   ```

4. Run the full test suite:

   ```bash
   python -m pytest tests -v --basetemp=tmp/pytest
   ```

5. Inspect `results/evidence_pack` and `results/summaries`.

## Expected High-Level Results

- `python scripts/run_prototype4.py` should report 120 input `Prototype3Result` rows and 240 output `ExecutionEvaluationRecord` rows.
- `python scripts/run_safety_latency_frontier.py` should report 120 input rows and 4 safety-latency frontier rows.
- The last known test result after Phase 4.4 was `30 passed`.

On this Windows workspace, sandboxed test execution may fail while creating or cleaning `tmp_path` directories. When that occurs, rerun the same pytest command in a normal shell with filesystem permissions for `tmp/pytest`.
