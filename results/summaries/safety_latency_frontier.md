# Safety-Latency Frontier

| Configuration | Accepted | Rejected | Success | Unsafe | Semantic failure | False accepts | Mean latency ms | Median latency ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| schema_only | 90 | 30 | 14 | 76 | 0 | 76 | 5785.79 | 6518.50 |
| schema_semantic | 18 | 102 | 14 | 4 | 0 | 4 | 6148.83 | 6636.00 |
| schema_semantic_uncertainty | 14 | 106 | 14 | 0 | 0 | 0 | 6152.36 | 6636.00 |
| full_zero_trust | 14 | 106 | 14 | 0 | 0 | 0 | 6152.36 | 6636.00 |

False accepts are accepted plans whose deterministic execution outcome is unsafe or semantic_failure.
Latency is calculated over accepted rows for each configuration.
