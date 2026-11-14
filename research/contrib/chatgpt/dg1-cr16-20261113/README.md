# DG1-CR16 — continuous causal structure and selective repair

**External DEV-only successor; no native Yggdrasil model, official research loop, protected main, accepted refs, or controller modified.**

## Scientific question
Can a learner preserve independently learned causal relationships, selectively repair a changed relationship, recover after interference, and select better physical actions on an unfamiliar recombination than fully trained conventional and equally exposed negative controls?

This is **not** another six-bit context archive. It uses three continuous state variables; six signed motor interventions; physically paid state/action/next-state observations; nontrivial causal graph interventions; and held-out action-consequence goal selection. No causal parent labels, regime identities, true equations, or audit answers are provided to any learner.

## Frozen before implementation or first use

- Preregistration-only commit: \`cd2823483a9d984915e887cd6a076a15c0a59b68\`.
- Protected main parent: \`5e74f8db85b2f5839c42148c0dfba69a88b1a2c9\`.
- Independent predecessor is [negative DG1-SL15 PR #997](https://github.com/spoonman136668-ai/Yggdrasil/pull/997), final \`3f394900d242eac62dbb5358679b9eed9f3e0997\`. Do **not** retune SL15.
- All 16 first-use seed identities, physical budgets, active learner capacity, four controls, data order, cold boundaries, metrics, thresholds, and classification are in [prereg.json](prereg.json).

## Experimental custody

16 distinct worlds × 5 separately charged arms × 192 real training action-consequences = 15,360; plus 12 held-out goal-action consequences at each of four audits, per arm, per world = 3,840; total **19,200 independently charged actions**. The five arms receive identical training state/action/outcome traces. Each arm takes its own chosen held-out action. Audit labels are evaluator-only and never fed to the learner. Cold restores must preserve inference and snapshots exactly; no stored state >64 KiB.

Controls are the same mechanism without an archive, a same-capacity randomized repair selector, an independent forgetting recursive least-squares learner, and a conventional recurrent model with **every input, recurrent, and output weight updated**. Parameter counts and actual CPU are exposed; CPU matching is bounded rather than exact, and even a positive outcome would be a development signal only, not independent qualification or AGI evidence.

## Run boundaries

Pre-first-use static and structural tests (unregistered toy worlds only):

    python -m py_compile research/contrib/chatgpt/dg1-cr16-20261113/cr16.py research/contrib/chatgpt/dg1-cr16-20261113/test_cr16.py
    python -m unittest discover -s research/contrib/chatgpt/dg1-cr16-20261113 -p 'test_*.py' -v

The original registered primary is allowed **only after** this source and frozen prereg are reviewed and committed. The prospective GitHub Actions workflow launches it on the PR exact SHA; preserves the original full JSON in GitHub Actions only, and executes full repository regression with a generated temporary code atlas. Engineering and scientific results are reported separately. No post-result tuning of this CR16 experiment.
