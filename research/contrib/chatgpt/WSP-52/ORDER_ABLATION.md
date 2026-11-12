# WSP52 — order-invariant readout diagnostic (SELFTEST only)

**Not preregistered as a WSP52 comparison arm.** No registered DEV / protected PRIMARY was touched. All measurements below use only SELFTEST seeds 9001 and 9002, three acoustic encodings, and the original 36 phase-A + 6 phase-B observed-action budgets. The underlying source and direct-writer numerical weight construction are unchanged.

## Controlled mechanism test

The source simulator sets an object's location to `(destination+verb) mod 4`: destination and action effects are commutative, while the acoustic grammar order changes between phase A and phase B. This provides a strong **human-supplied symmetry** we can inject into a diagnostic readout, without claiming that it was learned.

`OrderInvariantReadout` reuses the exact same `DirectWeightWriter.observe`, numerical entity/effect weights, action count, evidence conflicts, snapshot, and serialized capacity. It alters only the inference prior: match entity acoustic candidates independently of sentence slot, and aggregate the other two acoustic segments as an unordered pair. This could be invalid for noncommutative real language and physical actions; it is a test of the bottleneck, not an acceptable shortcut to general intelligence.

## Fixture results (total six conditions)

| Metric | Original position-sensitive writer | Order-invariant readout |
|---|---:|---:|
| Phase A correct /360 | **221** | **167** |
| Phase A wrong confident | 5 | 5 |
| Phase B correct /540 | **16** | **240** |
| Phase B wrong confident | 0 | **9** |
| Phase A retained correct /360 after B | **221** | **162** |
| Phase A retained wrong confident | 6 | 6 |
| Gradient optimizer steps | 0 | 0 |
| Evidence/actions | 42 per condition | 42 per condition |
| Serialized model state | Identical by construction | Identical by construction |

Per condition, A/B correct and B wrong confident:

| Seed/encoding | Direct A | Invariant A | Direct B | Invariant B | Invariant B wrong |
|---|---:|---:|---:|---:|---:|
| 9001 identity | 40 | 28 | 2 | 42 | 0 |
| 9001 permuted | 16 | 16 | 0 | 31 | 2 |
| 9001 rotated | 39 | 31 | 3 | 49 | 0 |
| 9002 identity | 45 | 45 | 5 | 40 | 0 |
| 9002 permuted | 41 | 24 | 0 | 50 | 0 |
| 9002 rotated | 40 | 23 | 6 | 28 | 7 |

## Interpretation and falsification

**Directly constructing numerical association weights provides partial compositional transfer**, but the original inference tied associations to fixed sentence positions. Deleting that assumption increases transfer substantially on this **commutative toy world**, while damaging original-grammar competence, retention, and safe abstention. The proposed near-term scientific target of >=75% B and zero wrong confident was **not** met. The model still does not discover independent destination/verb meaning (not identifiable from the observations); it is not a learned grammar, natural language understanding, or a new SCIENTIFIC_PASS. No equivalence to conventional fully trained baselines has been demonstrated.

What the diagnostic suggests testing next: **learning** which transformations are behavior-preserving from interventions, then applying only validated invariances with calibrated abstention, contrasted with explicit invariance and random invariance controls. Natural language requires order-sensitive counterexamples, not simply commutative aggregation. Freeze these ablations and measure the full process rather than retrofitting metrics after PRIMARY.

## Reproduction

From the WSP-52 directory, Python 3.12+ stdlib:
`python -m unittest -v test_source.py test_direct_writer.py test_order_ablation.py`

16/16 local tests PASS on 2026-11-12, Python 3.13.5. Same snapshot and weight equality are asserted, and independent final SHA CI must pass on Linux and Windows before engineering qualification. This is a **development fixture**, no special science-run authorization or accepted-ref mutation.

Deployment: none. Merge: none. Schedule/runner dispatch: none. Cost: no paid services.
