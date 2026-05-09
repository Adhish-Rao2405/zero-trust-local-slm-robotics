# Phase 4 Results Summary

Phase 4 evaluated execution-readiness for Prototype 3 planner outputs using a deterministic evidence-level evaluator. The input evidence contains 120 Prototype 3 result rows from a 30-command pilot benchmark. Prototype 4 expands these into 240 long-form execution records: 120 baseline rows and 120 zero-trust rows.

The baseline trust model produced 76 false accepts, while the zero-trust pipeline produced 0. Baseline outcomes were unsafe=76, success=14, and no_op=30. Zero-trust outcomes were rejected=106 and success=14.

The Safety-Latency frontier shows false accepts decreasing as gates are added: 76 -> 4 -> 0 -> 0. This supports a safety-utility interpretation: stricter evidence gates reduce unsafe acceptance, but increase rejection.

Limitations remain important. The evaluator is deterministic and evidence-level. It does not replay commands in PyBullet, does not prove physical robot task success, and relies on Prototype 3 semantic, uncertainty, and safety labels.
