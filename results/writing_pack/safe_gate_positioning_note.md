# SafeGate Positioning Note

SafeGate is the closest related recent work because it also uses pre-execution safety gating for LLM-controlled robots. It introduces a neurosymbolic architecture with hazard analysis, deterministic decision gating, safety contract compilation, SMT verification, and runtime monitoring.

This dissertation differs by targeting sub-2B CPU-class local SLMs through Microsoft Foundry Local, constrained and offline industrial or clinical-style deployment assumptions, ambiguity-stratified command evaluation, and explicit measurement of the model-level versus pipeline-level false-accept gap.

The contribution should therefore be positioned as a local-first constrained-deployment complement to SafeGate. It should not be framed as outperforming SafeGate, replacing SafeGate, or proving broader robot safety. Instead, it studies how evidence gates affect execution-readiness and false-accept risk for local SLM planning under pilot benchmark conditions.
