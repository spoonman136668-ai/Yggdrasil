# AAI-12U — Cold persistent primitive reuse under interference (source-only)

**Classification: `DEV_NO_GO_NO_SCIENCE`.** This is a new tokenless, source-only developmental experiment; it has **not** qualified independent scientific discovery, native Yggdrasil integration, production, or autonomous research-loop changes. No merge requested.

## Freeze and custody

- Base: AAI-12P PR #1074 at `abd374e7dc433981df991e103d8ebdff0b5eb093`; prior AAI-12Q/R/S/T negatives remain isolated.
- Preregistration **committed before implementation and outcomes**, exact commit `993d9057e8eed2e04eaf10037c83de49e35a48ff`, blob `b8fbdd75d1a1a136f57b2306f8c6064a3e1b261b`.
- Complete local evaluated source and uploaded Git exact blobs: `source_world.py` = `91244e8f07e258cc9e7a814a739dbce9acbb58fe`, `learners.py` = `6b77fb394fa68c592018a4a23dcb6b11979af4f1`, `dev.py` = `3dbd670a0041130778c8457c24cab01f3c1f8fbe`.
- Post-screen focused tests `test_dev.py` blob `ec551c0397fe5729202f4cecea7da8a98a27bdb6`; **11/11 local PASS**. Tests were added after the initial successful local developmental screen and **are not represented as pre-outcome confirmatory science**.
- One GitHub file creation had an extra terminal newline and was immediately mechanically corrected to the exact locally tested `source_world.py` blob. No algorithm, source-output, controls, preregistration or test labels changed. Local first completed screen preceded Git source commits; source identities were subsequently verified by readback and SHA-1 Git blob matching. The source-only result is not elevated to independent sealed science.

## What the experiment tests

A public 6-bit system has a three-input Boolean primitive `table[4*a+2*b+c]` combined with a fourth input through XOR. Every model receives the identical **public port mapping** (which physical inputs play the four roles), not the hidden eight-bit table or world class. The learner must observe eight real one-bit interventions in a donor world, eight in an interfering world, then only two in a recipient world with changed port bindings. Donor/interference each yield 16 public x/y observations; the recipient yields four, leaving **60 genuinely unseen input configurations**. The learner must cold-restore a bounded two-slot memory and predict all unseen recipient outputs.

There are eight frozen source groups and two source fixtures, for exactly **960 held-out predictions per method**: 480 genuine-reuse predictions, 240 changed-operator predictions, and 240 familiar-operator predictions. A full-public-state hidden source function is used **only** for fixture generation and heldout scoring. The learner implementation is in the separate `learners.py` module and does not import the privileged generator, hidden operator masks, family flags, or scoring oracle.

The candidate accepts a remembered primitive only when it makes **zero** errors on actual recipient public observations and its unseen ternary-code confidence is at least **0.75**. Otherwise it backs off to a local Beta(1,1) table estimate. The main comparator is a **same-information two-slot Bayesian memory**, plus a last-memory shortcut, donor-only shortcut, and local-only Beta estimator. These compare retention against credible memory baselines, not just memoryless models.

## Results from exact source bytes (Linux x86_64, CPython 3.13.5)

| Arm | 960 total | 480 genuine reuse | 240 changed operator | 240 familiar |
|---|---:|---:|---:|---:|
| **Uncertainty-gated two-slot** | **0.925000** | **1.000000** | **0.700000** | **1.000000** |
| Matched Bayesian two-slot | 0.918750 | **1.000000** | 0.675000 | **1.000000** |
| Donor-only fixed | 0.875000 | **1.000000** | 0.500000 | **1.000000** |
| Local-only Beta | 0.608333 | 0.600000 | 0.633333 | 0.600000 |
| Last-slot reuse | 0.402083 | 0.283333 | 0.741667 | 0.300000 |

All eight genuinely reusable receiver cases (four groups × two fixtures) were correctly recognized as usable cached operators. However, **three of four changed-operator cases were incorrectly accepted as compatible with existing memory**. In the two observed receiver ternary-code cells, different hidden primitives can coincide, so public consistency alone was not enough to rule out false reuse.

### Frozen acceptance gates

- Overall candidate gain over **strongest** non-oracle matched control **+0.00625** versus required **≥+0.02**: **FAIL**.
- Genuine reuse gain over local-only **+0.40** versus required ≥+0.15: PASS.
- Genuine reuse accuracy 1.00 versus required ≥0.85: PASS.
- Changed/familiar accuracy nonregression within 0.03 of local-only: PASS.
- True reuse cached slots 8/8 versus required ≥6/8: PASS.
- Changed operator false cache acceptances **3/4** versus maximum **1/4**: **FAIL**.
- Measured source-only model fit/cold-restore/predict process ≤10× fastest comparator: PASS **locally only**; OS/native end-to-end performance is unverified.

**All gates mandatory, so final `DEV_NO_GO_NO_SCIENCE`**. This is evidence that explicit two-slot relational memory can retain and remap previously learned operations on these mechanical fixtures, but **not** evidence of superiority over conventional equally informed memory. It falsifies the practical sufficiency of this particular zero-error-plus-confidence novelty gate on the frozen changed-world cases.

Source-observation SHA256 `0ae952f00ffe98df05a92318ed5f6c5312ca5a9b26a4dcfa1028d7eed32d381d`; exact all-arm prediction trace SHA256 `298318975016c134a5a431b7ffed4316a43557d30895ac458f13a54a1cd7c5b3`. Two local screening runs and the post-screen test reruns reproduced identical deterministic prediction traces, metrics and classifications (CPU times varied). 80 cold round trips passed. No original reserved science cases or seeds were used.

## Reproduction

From `research/contrib/chatgpt/AAI-12U`:

```sh
python -m unittest -v test_dev.py
python dev.py --source-dev
python dev.py --primary  # MUST be rejected
```

Only the frozen mechanical source is supported. An exact-final Ubuntu/Windows native regression, G29 source-locator regeneration, official project CI qualification, independent first-use scientific evaluation and owner acceptance were **not performed**. If automatic pull-request G29 checks fail on added source paths, that is an **engineering atlas mismatch**, not scientific proof or disproof.

## Closure and next distinct mechanism

Preserve this negative without after-result tuning. Future research should test whether **discriminating interventions can actively resolve cached-primitive ambiguity before reuse**, against the equally informed two-slot Bayesian control and with frozen action budgets. Merely increasing cache size or lowering this threshold would be after-outcome tuning, not an independent hypothesis. All changes in this draft are research-contribution files only. Main, accepted native state, FORGE, Wingless, Hybrid, project owners, runners, controllers, queues, schedulers and deployment are unchanged.
