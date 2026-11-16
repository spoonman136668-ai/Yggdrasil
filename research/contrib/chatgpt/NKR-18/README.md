# NKR-18 — What is learned, rather than merely stored?

This is an isolated, preregistered development study, not scientific acceptance
or accepted-model integration. It starts at NKR-17 draft #1154, exact SHA
23e95651f408ca05a8307e172575afe0d581925f, tree
ce2a75d579c7d11c94e6607cf7ee1921d0a317a7. Accepted main remains
5e74f8db85b2f5839c42148c0dfba69a88b1a2c9. No AGENTS.md exists in that
source tree. CONTRIBUTING_RESEARCH.md governs this external evidence lane.

The FIRST preregistration commit is
4287499900d9911038d3113eb201e16adc37d3b9, before implementation and outcomes.

## Mechanism and source

The existing NativeRelationMemory learns ten GF(2) affine action/context
coefficients per native address without tokens, transformers or gradients.
The new optional NativeRelationReadout serializes those SAME coefficients and
outcome-free input-support row spaces. It excludes all observation records,
right-hand-side outcome tables, exception records and source text. A fresh
Python process receives only compact bytes and query inputs. The trainer's
checkpoint digest links provenance but does not authenticate source truth.
Export rejects verified exceptions, so it cannot silently lose stored facts.
The incumbent choose_contextual and safer choose_verified_contextual interfaces
and 164-byte YPC1 snapshot remain unchanged. There is no owner-model activation.

The source is the unchanged already-consumed NKR-11 synthetic action fixture,
not the historical 21.3-million-record image or fresh external scientific data.
Its 12 deterministic worlds have four context bits, one action, and an affine
parity action-effect rule. New combinations are unseen inputs within a known
family, not unfamiliar real-world mechanisms or newly invented relationship
types. Native learning is falsifiable and bounded by that family.

## Frozen comparison

Two, four, eight or sixteen distinct public outcomes per world are presented
cyclically to the same total of 16 presentations/world at each scale. Duplicates
are counted as presentations, never new knowledge. All five methods receive
identical rows. Retrieval abstains on absent pairs. One-nearest-neighbor uses
raw-input Hamming distance. Conventional CART is fully grown to fit every
training label, including XOR's initially zero-information splits. The strong
independent control enumerates all 1,024 affine signatures with consensus-only
predictions. Algorithms differ in compute cost; no matched-compute speedup is
claimed. No neural baseline is included.

Score 192 previously unseen context/action combinations per scale. Then add
128 distinct observations into the remaining four slots of the SAME bank,
cold-restore, and compare all 384 earlier predictions. Identical abstentions
and correctly retained answers are reported separately. Attempted contradictory
same-slot observations must reject atomically: this shows protection but NOT
successful learning of a changed rule. Unknown-address probes and zero-weight
ablation diagnose missing cross-address transfer and dependence on weights.

## Reproduction and qualification

Primary: one source-committed local Linux run. Replication: one Windows CI
sweep, comparing every stable metric, prediction-trace SHA and checkpoint hash
with result.json. Mechanical tests do not run the primary sweep. Final source
requires the mandatory whole inherited root regression, six NKR05 tests and
independent G29 on Ubuntu and Windows. Source identity, environment, timings,
ancestry and limitations are recorded in provenance.json and the session report.

```sh
python -B -m unittest discover -s tests -p test_native_compact_knowledge.py -v
python -B research/contrib/chatgpt/NKR-18/experiment.py --verify research/contrib/chatgpt/NKR-18/result.json
```

Do not rerun original MiniGrid, rescan the historical image, retune the frozen
worlds or thresholds, merge, mutate main, start a runner/controller/scheduler,
or claim scientific superiority from a symbolic tie. Original MG19 negative
and NKR-17's bounded active-intervention result remain preserved.
