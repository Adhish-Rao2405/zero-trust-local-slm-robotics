# Phase 4.8: Simulated Clarification Recovery

Phase 4.8 adds an isolated clarification-recovery extension on top of the Phase 4.7 ambiguity-adaptive gate. It does not modify the locked Prototype 4 evaluator, loaders, evidence pack, figures, tables, or Phase 4.7 gate implementation.

The extension evaluates whether an ambiguous natural-language robot command can be converted into a lower-ambiguity executable command after a simulated user clarification. Each case pairs an original ambiguous command with a clarified replacement and reuses the Phase 4.7 `evaluate_ambiguity` function for both commands.

## Recovery Definition

A clarification case is counted as recovered only when:

- the original command decision is `CLARIFY` or `REJECT`;
- the clarified command decision is `EXECUTE`;
- the clarified ambiguity score is lower than the original ambiguity score.

This makes the extension a deterministic evidence-level recovery model rather than a live dialogue system.

## Outputs

The runner writes isolated evidence only under:

```text
results/prototype4_extensions/phase_4_8/
```

Generated files:

- `clarification_recovery_results.csv`
- `clarification_recovery_summary.json`

The summary reports total cases, recovered cases, recovery rate, mean original and clarified ambiguity scores, mean score reduction, and decision-count distributions.

## Dissertation Interpretation

Phase 4.8 demonstrates that ambiguity need not be treated only as a terminal rejection condition. In a zero-trust robot planning pipeline, ambiguous commands can be paused and clarified before reaching execution. This supports a safe recovery pathway: the system first detects underspecified instructions, then admits only clarified commands that become sufficiently explicit for execution.

This remains an optional extension. It does not change the previously reported Prototype 4 execution-comparison results, safety-latency frontier, evidence pack, or dissertation figures and tables.
