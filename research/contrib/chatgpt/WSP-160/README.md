# WSP-160 — Directly programmed continuous public-action weights

**Source-free research only. No original CartPoleWind actions, scientific superiority or accepted native state.**

## Lineage

- Qualified parent: WSP-159 PR #1212 at d550127634c50801b4060945e815f961eb104e1c, tree e4be55fd2ede6429a023be8e9fc65c7992d2cef2.
- Preregistration-only FIRST commit: 0098989292c684ceda0dd2f2a52ed4a07877fe46.
- WSP-158 frozen DTR calibration NO-GO remains unchanged, CKAD separate cumulative research untouched.
- Upstream static source CartPoleWind: CausalAILab/Causal-Gymnasium at c94e9a4cd3641588b6b8507e71ccee5c27032bdf, causal_gym/envs/cartpole_wind.py blob d65a6a31941709dc9201259d80dd4ebbcf48b4fa, Apache-2.0; original simulator never run/imported.

## Opt-in numerical program

Fixed authored 10-dimensional public feature grammar: intercept, four public observed state components, signed chosen action, and four action-state interactions. Four output channels directly write 40 coefficients for next-state delta. An inverse 10x10 regularized covariance tracks prior public training information. One numerical observed-state transition performs a gradient-free recursive least-squares rank-one direct weight update with lambda=1. The program is an explicit implementation of conventional online ridge, not an invention of unknown operators.

The versioned YDW1 cold checkpoint is exactly 1158 bytes: 4 magic, 2 count, 140 float64 values and 32 integrity bytes, with 2048 rows maximum. Only the six public fields admitted by the parent WSP159 public-boundary object may ever be presented by a real source actor. The weight program accepts only observed state, chosen action, next observed state. Hidden wind, simulator source objects, graph, info, and evaluator fields are outside its contract. A checkpoint SHA is integrity, not external source custody.

## Frozen source-free checks

Seeded fabricated continuous development only: 211,337,503, each 192 FIT + 64 disjoint VALID tuples. Independently trained full-batch ridge (separate Gaussian elimination normal-equation implementation) must tie the direct coefficient program numerically. Additional fully fitted action-erased ridge, permuted-action negative, and zero predictor expose source-free capacity and action sensitivity. Predeclared numeric requirements: max held prediction gap vs batch ridge <=1e-8; native RMSE <0.10; native advantage over action-erased >=0.01. Failing these is a new versioned development NO-GO, not grounds for post-result tuning.

All sourcefree tests require no external environment, no NumPy, no GPU or paid API:

    python -B -m unittest discover -s research/contrib/chatgpt/WSP-160 -p 'test_*.py' -v

Tests assert public-only numeric values, output fidelity, immutable updates, cold model continuation, checkpoint tamper/poison rejection and fixed capacity. A source-free GitHub workflow emits per-replica diagnostic metrics and runs mandatory exact-source dual-platform root+NKR05 and G29 qualification. All metrics must be reported as development findings, never SCIENTIFIC_PASS.

## Future source-owned scientific experiment — NOT authorized here

The prior CVH10 conditional 13,312-action cap is not a WSP160 lease. Before the first real original-source reset/step/do, owner-controlled actor/custody, virgin disjoint source cohort receipts, immutable admissible public fields, frozen fit/validation/transfer splits and fully converged, information/action and compute-matched conventional and independent model-based controls are required. Measure learned interventions, unfamiliar causal transfer, retention, repair and whole-process compute after that separate first-use qualification. This synthetic development cannot establish causal intelligence or transfer.

**ENGINEERING**: targeted source-free design; final qualification pending.
**SCIENTIFIC**: NOT RUN on original source, SCIENTIFIC_PASS=false.
**DEPLOYMENT**: NONE, draft/unmerged, no native owner or controller changes.
