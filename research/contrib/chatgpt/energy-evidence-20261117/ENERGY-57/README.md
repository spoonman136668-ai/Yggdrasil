# ENERGY-57 — Stable relations between learned causal factors

Independent external synthetic Yggdrasil research lane; **not native model training**, autonomous learning, deployment or accepted science. Same existing draft PR #1210.

## Hypothesis

Does a persistent learner that retains old-context discovered primitive factors and shares only apparently invariant *relations* between them improve cold causal-consequence prediction across unseen nuisance distribution shifts? A frozen stage-old OMP4 first discovers four two-bit parity supports from witnessed old do-actions. An independently learned set of six pairwise products of these supports defines candidate relational edges. The old predictor is frozen. A new-context learner fits observed new actions and shares only old/new relational coefficients with consistent sign and distance. Its cold predictions use new-context labels and selected shared relationships; cold held labels are never used during fitting.

## Data, controls and limitations

Each world contains 12 observed intervention bits (10 randomized causal/distractor bits +2 nuisance cues), four hidden pair-parity primitives, stable two-factor relations, and one old-only and one new-only edge. Families: stable edges, one sign-flipped edge, and an unmodeled triple relation in the new context. Correlated nuisance cues change between old/new and become independent at cold. Each world has 408 unique underlying 10-bit causal assignments: 96 witnessed old, 96 witnessed new, and 72 each held old/new/cold. The source is a code-generated synthetic world, not a real environment, protected scientific first-use, JEPA training or proof of causal intelligence.

The proposed learner is compared against **same-learned-primitives independent context-specific Ridge** (exact matched capacity), unconditional relation pooling, fully trained order-4 OMP and ElasticNet (full authored Walsh dictionary), RBF kernel ridge, 48-tree ExtraTrees, frozen old no-adaptation, and shuffled-new-label negative. All methods get the same 192 factual training consequences, no held truth, no latent primitive IDs and no oracle edge identities. Original coefficient fitting uses ordinary sklearn ridge/OMP, not physical energy measurement. The independent auditor re-generates all cases without importing the scorer and refits all nine methods; both share NumPy and sklearn backends.

## Freeze and reproduction

Exactly two excluded local pilot seeds (99557, 99563), 3 worlds each, were used for implementation diagnostics *before* source freeze. The first favors proposed relational pooling and the second heavily favors conventional OMP; neither is confirmatory. A separate GitHub preregistration will freeze prospectively unseen screen seeds 99619, 99637, gates, stop criteria and reserved primary 100019,100043,100057 BEFORE scoring any prospective world. No post-screen tuning is permitted.

From an extracted `source.tar.bz2`, install Python 3.13.5, NumPy 2.3.5, sklearn 1.8.0, SciPy 1.17.0, set `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`, and run:

```bash
python -B experiment.py --seeds 99619 99637 --out screening.json
python -B audit.py screening.json --out independent_audit.json
```

Do not execute reserved primary if preregistered prospective screening fails. No accepted Yggdrasil state, controller, scheduler, runner, queue, merge, main or native weights are touched.
