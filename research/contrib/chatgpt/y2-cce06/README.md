# Y2-CCE06 CAL source and comparator engineering

This folder is a **draft calibration source implementation**, not a completed
calibration study, CCE-06 learner, stronger-control suite, native Yggdrasil
integration, or protected scientific result.

## Source boundary

- `calibration_worlds.py` is evaluator-only. It has two distinct positive causal
  graph templates, action-null and intervention-identifiable observational alias
  negative controls. It emits ONLY public two-bit (observation, action,
  next-observation) records. Source-side hidden dynamics and oracle diagnostic
  must never be imported into candidate or comparator code.
- `calibration_plan.json` fixes the calibration families, seeds, split sizes and
  action costs. Train and cal-eval use deterministic **independently keyed RNG
  streams**, not disjoint theoretical source families.
- Calibration-sized generation is blocked without matching code/plan SHA-256 and
  source-commit fields in a caller-provided lock. This **does not** constitute
  independent custody. No lock or calibration datasets are committed here;
  protected PRIMARY is not implemented or generated.
- Evaluator-generator fixtures are restricted to seed 997 (<=32 events).
  Standalone public fixture RNGs are not registered CAL or PRIMARY sources.
- `calibration_controls.py` contains a full-context public suffix table and an
  EM-fitted action-conditioned HMM. HMM needs >=3 TRAIN-only restarts per
  dimension 2..8, train-only dimensional selection, proper convergence checks
  and a matched evaluation runner before it can count as a **fully fitted**
  comparator.

- `calibration_psr.py` learns 12 observable action-observation operators; a
  finite predictive state is updated recurrently at inference without a
  suffix lookup. `calibration_psr_selection.py` chooses test-basis width,
  context depth and ridge strength using TRAIN only. This is an operator
  model control, not proof of identifiable hidden-state recovery.
- `calibration_active_bayes.py` uses public Dirichlet action-response
  posteriors, priced interventions and expected Bayesian parameter
  information gain. `choose()` is paired with a real public
  `update()` witness. Off-policy evaluation against unrelated logged
  actions is forbidden: the interactive cost/accuracy frontier remains
  unmeasured.

## Current gaps / strict stop

- No CCE06 split/merge candidate or learned relations, and no fully trained
  recurrent neural estimator. A learned-operator PSR comparator and public-only
  Bayesian probe policy now exist, but neither establishes superiority over the
  strongest controls. No interactive matched cost/accuracy Pareto frontier.
- No committed independent-source lock, evaluator, data manifests or independent
  custody receipt. No CAL-EVAL materialized and **no primary first-use**.
- No physical-world evidence, learning gain, accepted promotion, deployment or
  reviewer authority.
- This code adds Python research files; the pre-existing G29 generated atlas may
  require its **approved source-pinned generator** before full CI passes. Never
  hand-edit `.ice` or bypass atlas checks.
- For exact next gate: finish the remaining genuine strong controls + training
  convergence checks + source-custody lock, verify identifiability, freeze
  evaluator and execute TRAIN-only control selection. Only then consider CAL
  scoring and separately governed PRIMARY preregistration.

## Fixtures only

```bash
cd research/contrib/chatgpt/y2-cce06
python -m unittest -v test_calibration test_calibration_fit_selection
python -m unittest -v test_calibration_psr test_calibration_psr_selection test_calibration_active_bayes
```

Fixture tests never use the frozen experimental seed list and cannot validate
the scientific headroom or OOD-transfer hypotheses.
