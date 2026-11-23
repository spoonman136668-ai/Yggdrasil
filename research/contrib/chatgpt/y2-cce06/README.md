# Y2-CCE06 CAL source and comparator engineering

This folder is a **draft calibration source implementation**, not a completed
calibration study, CCE-06 learner, stronger-control suite, native Yggdrasil
integration, or protected scientific result.

## Source boundary

- \`calibration_worlds.py\` is evaluator-only. It has two distinct positive causal
  graph templates, action-null and intervention-identifiable observational alias
  negative controls. It emits ONLY public two-bit (observation, action,
  next-observation) records. Source-side hidden dynamics and oracle diagnostic
  must never be imported into candidate or comparator code.
- \`calibration_plan.json\` fixes the calibration families, seeds, split sizes and
  action costs. Train and cal-eval use deterministic **independently keyed RNG
  streams**, not disjoint theoretical source families.
- Calibration-sized generation is blocked without matching code/plan SHA-256 and
  source-commit fields in a caller-provided lock. This **does not** constitute
  independent custody. No lock or calibration datasets are committed here;
  protected PRIMARY is not implemented or generated.
- Small fixture-only seed 997 (<=32 events) is the sole test source used.
- \`calibration_controls.py\` contains a full-context public suffix table and an
  EM-fitted action-conditioned HMM. HMM needs >=3 TRAIN-only restarts per
  dimension 2..8, train-only dimensional selection, proper convergence checks
  and a matched evaluation runner before it can count as a **fully fitted**
  comparator.

## Current gaps / strict stop

- No CCE06 split/merge candidate or learned relations, no PSR, no fully trained
  recurrent estimator, no fitted active Bayesian cost/accuracy frontier.
- No committed independent-source lock, evaluator, data manifests or independent
  custody receipt. No CAL-EVAL materialized and **no primary first-use**.
- No physical-world evidence, learning gain, accepted promotion, deployment or
  reviewer authority.
- This code adds Python research files; the pre-existing G29 generated atlas may
  require its **approved source-pinned generator** before full CI passes. Never
  hand-edit \`.ice\` or bypass atlas checks.
- For exact next gate: finish the remaining genuine strong controls + training
  convergence checks + source-custody lock, verify identifiability, freeze
  evaluator and execute TRAIN-only control selection. Only then consider CAL
  scoring and separately governed PRIMARY preregistration.

## Fixtures only

\`\`\`bash
cd research/contrib/chatgpt/y2-cce06
python -m unittest -v test_calibration
\`\`\`

Fixture tests never use the frozen experimental seed list and cannot validate
the scientific headroom or OOD-transfer hypotheses.
