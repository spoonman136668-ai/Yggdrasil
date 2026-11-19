# ENERGY-66 — Multiple unfamiliar causal factors, external synthetic falsification

**Source freeze v1, before prospective tests.** This evidence-only lane tests whether a two-step residual sparse-factor learner can improve over **fully trained conventional learners on the identical supplied pair+quadratic-interaction bank** when there are *two* previously unseen causal fourth-order factors. It does not modify or train native Yggdrasil, and does not introduce a scheduler/agent/controller.

The contributor-authored simulator has eight binary causal interventions (256 possible action identities) and 212 disjoint identities per world: 56 witnessed OLD, 48 witnessed NEW, 36 OLD held, 36 NEW held, 36 COLD held. OLD is three planted signed pair parity factors. NEW contains two new fourth-order effects (double_quad), three effects (triple_quad), or two plus an out-of-grammar fifth-order effect (double_quad_plus_fifth); OLD pair coefficients may drift. Gaussian noise sd 0.18. All input bits remain observed. COLD is NEW with unseen randomized causal assignments, not an unfamiliar natural-world environment or a new regime.

Candidate: recover three pair supports with OLD OMP3; keep OLD readout immutable; make two rounds of residualized orthogonalized NEW quadruple selection, refitting NEW Ridge after selection. All operators and the finite bank (28 two-variable + 70 four-variable parity terms) are *given*, not autonomously invented. Matched controls: 3-fold train-only cross-validated ElasticNet on the same OLD-selected supports + all quadruples, full-bank 3-fold CV ElasticNet, matched OMP5, full-bank OMP5, and softmax memory. Negative controls: fixed old model, old-support-only new refit, shuffled NEW labels; planted truth oracle is diagnostic only and excluded from conventional comparisons. Every arm receives the same OLD 56 and NEW 48 labels; training computation and capacity are not identical across learners. OLD readout retention follows from frozen OLD checkpoint by design and does not demonstrate interference immunity in one mutable model.

Excluded prefreeze engineering smoke `999599` (world ID 0 x three families) passed independent audit; do not count it as prospective evidence. Prospective seeds `999637,999659` (world IDs 0–3 x three families = 24) and primary reserved seeds `108101,108119,108137` are specified separately in the preregistration. Stop if any critical gate fails; do not score primary. Independent source `audit.py` refits every learner and reconstructs the planted interventions/labels; it does not import scorer, but shares NumPy/sklearn and the described simulator semantics.

Reproduce from frozen `source.tar.bz2` with Python 3.13.5, NumPy 2.3.5 and sklearn 1.8.0, single-thread CPU:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
tar -xjf source.tar.bz2
python -B experiment.py --seeds 999637 999659 --out screen.json
python -B audit.py screen.json --out audit.json
```

Report scientific and CI qualifications separately. All held target outputs remain inaccessible to fitted learners; auditor/score archive exposes planted truth for verification only.
