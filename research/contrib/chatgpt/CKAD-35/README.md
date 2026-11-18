# CKAD35 — Cold native memory and few-shot causal transfer

**Research-only.** This experiment does not edit Yggdrasil's accepted native components, controller, or owner loop. It is an isolated external research contribution.

CKAD34 ([PR #1250](https://github.com/spoonman136668-ai/Yggdrasil/pull/1250)) established that the existing numeric checkpoint can select degree 1/2/3 polynomial classes from observed interventions. Fully fitted conventional GF(2) matched its predictions. CKAD35 tests the next practical gap: **can previously learned native causal representations help a new world when context features are renamed and the donor/world correspondence is unknown?**

Three source functions are learned from 42 source-witnessed interventions each, written into the existing `NativeContextAccumulator`, and restored from a cold checkpoint. Each new target is generated using a hidden source identity, a random reordering and complementing of context bits, and an optional output flip. The binary action is kept causal and is not relabeled. Three negative targets additionally contain an unfamiliar quartic term. The candidate is not told donor identity, mapping, output flip, or negative-family labels.

### Exact research intervention budget

For each seed, 126 donor source observations (3×42), 96 target source observations (6×16: 10 fit and 6 independent calibration), and 168 fresh pressure observations (4×42) = **390 publicly witnessed binary outcomes**. Sixteen entirely disjoint held action inputs per target are evaluator-only, giving 48 held composite cases for each target family and **96 held composites per pilot**. No synthetic, inferred or hypothesized outcome may be written into the native memory as genuine source evidence.

### Candidate and strongest controls

The candidate reads actual checkpointed native donor functions and conducts a conventional bounded analogy search: 3 donors × 5! permutations × 2⁵ input complements × 2 output complements = **23,040** source-consistent hypotheses. It conditions on ten genuine target fit observations and six genuine calibration observations; if all hypotheses are falsified it abstains at probability 0.5. It does not program an imagined target outcome, copy donor weights into target cells, or claim that the native learner itself autonomously discovers analogies.

Required equal-witness controls: independently fitted conventional donor GF(2) + **the exact same full Bayesian analogue hypothesis set**, newly trained unmodified native target-only learner, independent degree-3 conventional GF(2) target-only, fully fitted degree-3 polynomial logistic, frequency, sham, and uncalibrated analogy. Genuine quartic negatives check confidence and falsification. The strongest conventional analogue must achieve identical predictions; a tie cannot be SCIENTIFIC_PASS.

### Frozen stop, before first-use

Preregistration commit `fa14893269bb93b2d192ab4134073d5c148898fd` predates source implementation. Two independent original pilots are `13851` and `13852`. Reserved primary `23851/23852/23853` remain unused even if engineering screening passes.

Both pilot seeds must have in-family analogue held Brier ≤0.08, at least 0.05 better than **both** target-only native and target-only conventional, perfect parity to conventional analogue, at least 50% high-confidence held primitive commitment and zero wrong high-confidence guesses. Six source-only calibration interventions must veto at least two of three quartic negatives, give zero wrong high-confidence accepted OOD guesses, and OOD gated Brier no worse than no calibration. Exact cold bytes, full 64-input donor and target retention after four pressure slots, source evidence provenance and atomic contradictory-source refusal must all pass.

`ENGINEERING_FEASIBLE` is not superiority. On failure preserve `SCREEN_NO_GO` and stop, no retune/replay of consumed seeds, no primary/merge/deployment. The expected useful outcome is a narrowly bounded test of transferring a remembered *source representation* through an externally supplied analogy method, not a proof of general causal transfer.

### Evidence and qualification

The frozen original pilot source blob and dependency/qualifier identities are pinned before first-use. `seal_pilot.py` independently reconstructs all analogical hypothesis predictions, source-only donor weights, held Brier and primitive confidence errors from original byte-for-byte GitHub receipts without importing the generator or native memory code. A final exact-candidate Linux and Windows full regression is mandatory; positive screening without final regression is only unqualified development evidence.
