# Phase 4.9: Formal Safety Specification Layer

Phase 4.9 adds an optional formal safety specification layer outside the locked Prototype 4 core. It does not modify the Prototype 4 execution evaluator, Phase 4.7 ambiguity gate, Phase 4.8 clarification recovery layer, evidence pack, figures, or existing extension results.

## Purpose

The extension defines the robot planner safety contract as explicit, structured, machine-readable rules. It is an audit layer rather than a replacement for the locked Prototype 4 deterministic validator. Its role is to make the safety assumptions of the zero-trust planning pipeline directly inspectable and citeable.

## Rule Set

| Rule ID | Requirement |
|---|---|
| FS-001 | Action must be present. |
| FS-002 | Action must be in the supported action set. |
| FS-003 | Action parameters must match the required schema for that action. |
| FS-004 | `target_xyz` must be inside permitted workspace bounds. |
| FS-005 | Zone target must be inside the allowed zone set. |
| FS-006 | Gripper width must be within permitted bounds if supplied. |
| FS-007 | Force must be within permitted bounds if supplied. |
| FS-008 | Referenced object must be known if object references are supplied. |
| FS-009 | Action must not contain unknown or extra fields. |
| FS-010 | Commands classified as `CLARIFY` or `REJECT` by an ambiguity gate must not be authorised for execution. |

## Contract Constants

The contract is defined in `src/extensions/phase_4_9/formal_safety_spec.py` using conservative defaults:

- supported actions: `describe_scene`, `move_ee`, `open_gripper`, `close_gripper`, `pick`, `place`, and `reset`
- allowed zones: `bin_A`, `bin_B`, `bin_C`, `left_tray`, `right_tray`, `staging_area`, and `home`
- workspace bounds: x and y in `[-1.0, 1.0]`, z in `[0.0, 1.0]`
- bounded gripper width and force fields when they are supplied
- a small deterministic known-object set for audit cases

## Audit Output

Each audit returns a structured result containing:

```json
{
  "passed": false,
  "violations": [
    {
      "rule_id": "FS-004",
      "severity": "critical",
      "message": "target_xyz is outside permitted workspace bounds"
    }
  ],
  "rule_ids_checked": ["FS-001", "FS-002", "FS-003", "FS-004"]
}
```

The runner evaluates deterministic formal safety cases and writes isolated evidence only under:

```text
results/prototype4_extensions/phase_4_9/
```

Generated files:

- `formal_safety_audit_results.csv`
- `formal_safety_audit_summary.json`

## Dissertation Interpretation

Phase 4.9 introduces a formal safety specification layer as an optional extension to the Prototype 4 evaluation stack. Whereas the locked Prototype 4 core evaluates execution reliability empirically, the Phase 4.9 layer defines the safety contract explicitly through structured, machine-readable rules.

This extension does not replace the existing deterministic validator. Instead, it makes the implicit safety assumptions of the system auditable. Each action plan can be checked against rule identifiers FS-001 to FS-010, producing a transparent list of violations and severity levels. This creates a clearer connection between the zero-trust argument and the implemented system: model outputs are never trusted directly, and execution is only permitted when the action satisfies an explicit safety contract.

