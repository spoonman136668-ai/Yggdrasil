# WSP-127 — Adaptive observation allocation for direct numerical causal weight construction

**DRAFT engineering-only research. Original scientific first-use denied; no accepted/native Yggdrasil integration.**

Source-pinned preregistration FIRST: `df73e6df969ee3cdfe4748f91f8e59fba690b076`.
Exact frozen predecessor: WSP126 final `8f6c6508daec4f99bb9318b464cdfd473ddef973`, PR #1142 (failed 95% FIT threshold). WSP127 draft is PR #1144; it preserves the predecessor's failed scientific hypotheses and does not mutate accepted `main`.

## What is being tested

WSP126 learned numerical basis factors but failed to witness the rank-four directions in 10/128 laws and tied the optimized symbolic solver. WSP127 changes **the policy for collecting consequences** at much higher scale, not the mathematical class of the representation.

- 128 deterministic hidden independent 64×64 GF(2)-rank-eight laws. All relevant source factors are private to the inspectable development evaluator, not returned to models.
- Exactly **1,024** charged consequence interventions per law, **131,072 per arm**; the learner initially has no task-specific factor weights.
- Feedback-adaptive full-row acquisition stops once eight independent directions have been witnessed, then probes pivot columns across the remaining rows, then spends any leftovers lexicographically. Fixed-policy comparator always probes nine complete rows, then the chosen eight columns of each remaining row, then eight lexicographic leftovers.
- Both intervention policies have an **independently implemented optimized symbolic GF(2) solver** on the same transcript; no deceptively weak symbolic comparator.
- 393,216 genuinely unqueried FIT decisions per arm; 256 zero-source relabel views of the **same 128 laws** (1,048,576 scored decisions/arm), and 64 zero-source rank-nine source modifications (262,144 negative decisions/arm).
- Frozen threshold: FIT >=95.0% correct with **zero** confident errors and >=8.0 percentage point gain over equal-budget fixed-policy optimized symbolic. An adaptive numerical/symbolic tie may prove an acquisition-policy benefit, but cannot establish numerical representation superiority.
- Rank-nine negative >1% confident wrong is unfamiliar-law safety NO-GO even if FIT passes. No post-score tuning, budget changes, first-use relabeling or protected-source experiments.

## Reproduction (source-safe public engineering only)

```bash
python -B -m unittest discover -s research/contrib/chatgpt/WSP-127 -p 'test_*.py' -v
python -B research/contrib/chatgpt/WSP-127/experiment.py --engineering
```

The full experiment is deliberately executed by the test suite **once**; avoid duplicate full runs unless exact-source qualification needs replay. The `WSP127_FINAL_ENGINEERING_JSON` log reports the original frozen score and both good and bad outcomes; no primary result artifact exists at prereg/source-implementation boundary.

The GitHub workflow `.github/workflows/wsp127-source-safe.yml` runs two-OS source-safe development on push. The explicit source-pin commit triggers the existing G29 archive regeneration pattern; a derived-only G29 commit then triggers **mandatory exact-candidate Linux/Windows final full WSP117–127 and root regression**. G29 archive drift prior to source pin is expected and is **not** a learning failure.

## What this cannot prove

GF(2), rank<=8 and the ability to identify linearly independent directions are supplied mathematical priors. No new algebra, unknown physics, general intelligence, numerical superiority over optimized symbolic, or gradient-free whole-process efficiency is demonstrated merely by factor allocation. Strong conventional model architecture/convergence and measured full path CPU/wall/RSS/energy remain scientifically unqualified in this engineering stage. The inspectable generator is not an independently held original scientific cohort.

All data, algorithms, thresholds, tests, source custody and negative failures remain in this repository. No controller, runner, scheduler, queue, paid API, accepted-state branch, Wingless or Hybrid state is modified by this PR.
