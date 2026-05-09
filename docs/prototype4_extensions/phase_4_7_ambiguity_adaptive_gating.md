# Phase 4.7 Ambiguity-Adaptive Gating

Phase 4.7 adds an optional ambiguity-adaptive pre-execution gate outside the locked Prototype 4 core. It does not modify the deterministic execution evaluator, Prototype 3 loaders, Safety-Latency frontier, figures, tables, or evidence pack.

## Purpose

The gate evaluates whether a natural-language robot command is sufficiently specified to justify execution, should trigger clarification, or should be rejected. This sits before action execution and complements the existing zero-trust evidence gates.

## Deterministic Features

The feature extractor detects:

- unresolved pronouns such as `it`, `this`, and `that`
- vague object references such as `thing`, `object`, `item`, `stuff`, `something`, and `everything`
- ambiguous locations such as `there`, `over there`, `somewhere`, and `next to it`
- weak action verbs such as `sort`, `fix`, `arrange`, `handle`, `do`, and `manage`
- missing target locations for move/place/put/transfer commands
- multiple possible object references such as `the other one` or `the correct one`
- underspecified tasks such as `sort everything properly`

## Policy

Feature flags are converted into a bounded ambiguity score in `[0.0, 1.0]`.

| Score range | Decision |
|---:|---|
| `0.00` to `0.30` | `EXECUTE` |
| `> 0.30` to `0.65` | `CLARIFY` |
| `> 0.65` to `1.00` | `REJECT` |

Each gate result includes the command, score, decision, and reason codes.

## Outputs

The runner writes only to the extension output folder:

- `results/prototype4_extensions/phase_4_7/ambiguity_gate_results.csv`
- `results/prototype4_extensions/phase_4_7/ambiguity_gate_summary.json`

## Dissertation Framing

Phase 4.7 extends the Prototype 4 evaluation stack with an ambiguity-adaptive gating layer. Unlike the deterministic execution evaluator, which assesses whether a generated action can be executed safely and consistently, the ambiguity gate operates one step earlier: it evaluates whether the natural-language command itself is sufficiently specified to justify execution. This distinction is important because a command may pass syntactic and physical safety checks while still being semantically underdetermined.

The extension is isolated from the locked Prototype 4 core. It therefore does not alter the previously reported safety-latency frontier, execution metrics, or evidence pack. Instead, it provides an optional safety layer that can be evaluated independently and used to motivate future clarification-aware robot planning.
