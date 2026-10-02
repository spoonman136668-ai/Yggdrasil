{
  "schema": "yggdrasil.research-invalid-attempt.v1",
  "experiment": "EXP-BRIDGE-WINGLESS-YGGDRASIL-HIERARCHY-MAINTENANCE-002",
  "disposition": "invalid-preregistration-before-execution",
  "scientific_claim": false,
  "primary_probe_executed": false,
  "reason": "Pre-execution control-identity review found the lesion selector p and (p+2) mod 4 always chooses two compounds with the same parity. The type-preserving shuffled control swaps their compound payloads while the paired reference profiles encode identical parity bits, so the shuffled state can remain functionally equivalent on the frozen reference task. That makes the <=0.25 shuffled-control gate non-discriminative.",
  "preservation": "No implementation or probe executed. Reissue from this clean parent with the same source identities, canonical 16-structure state, seeds, grammar, abstention behavior, retained encodings, repair budgets, and thresholds. Change only lesion selection from same-parity p/p+2 to adjacent opposite-parity p/p+1 so the frozen type-preserving shuffle is a genuine wrong-payload control.",
  "authority": "research-only"
}
