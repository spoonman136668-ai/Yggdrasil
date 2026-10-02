{
  "schema": "yggdrasil.research-invalid-attempt.v1",
  "experiment": "EXP-BRIDGE-WINGLESS-YGGDRASIL-HIERARCHY-MAINTENANCE-001",
  "disposition": "invalid-preregistration-before-execution",
  "scientific_claim": false,
  "primary_probe_executed": false,
  "reason": "Pre-execution consistency review found two frozen-design defects. First, prediction semantics defaulted missing higher-level structures to reference byte 224; for lesion sets containing the two even-parity compounds, 4 of 12 affected ordered compound pairs legitimately target 224, forcing affected post-lesion accuracy to 1/3 and making the <=0.25 damage gate internally inconsistent. Second, the shuffled repair control said to cyclically rotate payloads among four retained records even though compound records are 10 bytes and reference-profile records are 4 bytes, leaving type/length-preserving control construction ambiguous.",
  "preservation": "No implementation or probe executed. Reissue the exact integration question from this clean invalid-attempt parent. Keep all source identities, structure definitions, seeds, lesion selection, evaluation grammar, repair budgets, and scientific intent unchanged. Clarify only missing-structure output as an out-of-vocabulary abstention byte that can never equal a valid reference target, and define shuffled controls separately within compound-record and profile-record types.",
  "authority": "research-only"
}
