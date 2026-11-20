# ENERGY-BOUND-03 — Correct-Bayes envelope and directed-causal research pivot

**2026-11-20. Independent Yggdrasil contributor only. This is an analytical boundary and proposed next experiment, not a new learner, qualified scientific result, or integration.**

## Source and scope
- Accepted `main` on first commit: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Prior source-free negative: ENERGY-FLUX-01 in [draft PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346): identical Beta-Bayes rule, zero superiority.
- Follow-up ENERGY-TOPO-02, frozen code at `4ca7843a7a0e018f0f23d4f75570f1ef6a19174e`, exact local-source Git blob `91c5e6f30e5fc568d15391e53286ff4993b65bd9`; recorded aggregate primary: MAP flow Brier 0.465444 vs correctly specified graph Bayes 0.228828, 4/10 false-null alarms, no full-process efficiency proof. Do **not** replay consumed primary seeds.

## Mathematical claim (not empirical science)
Let `Y` be a categorical next state, `D` all permitted action/consequence observations, `p_i=P(Y=i|D)` the **correct** posterior predictive distribution under the actual data-generating model, and `q_i` any alternative prediction using the same information. For multiclass Brier `L(q,Y)=sum_i(q_i-1[Y=i])^2`:

```
E[L(q,Y) | D]
= sum_i q_i^2 - 2 sum_i q_i p_i + 1
= (1 - sum_i p_i^2) + sum_i (q_i - p_i)^2
= E[L(p,Y)|D] + ||q-p||_2^2.
```

Therefore `E[L(q,Y)|D] >= E[L(p,Y)|D]`, with equality iff `q=p`. The result applies independently to each held action/state/context and remains true after adaptive interventions when conditioning on the actual information history. A fully informed, correctly specified exact Bayesian control **cannot be beaten systematically on expected Brier** by another predictor receiving the same evidence. Finite-sample wins can occur by evaluation noise; they do **not** establish a new representational or intelligence advantage. A point-estimate topology learner cannot refute this theorem.

## Consequence for prior qualification design
ENERGY-FLUX-01 and ENERGY-TOPO-02 froze a primary threshold requiring positive Brier superiority over a correctly specified exact Bayes control. Keep their preregistrations, source, results, and NO-GO unchanged. Such superiority is not an appropriate default future hypothesis under matched exact-specification assumptions. Do **not** retroactively change decision rules to rescue them.

A meaningful future success can instead be either:
1. **Resource–quality Pareto:** approach the correct oracle posterior within predeclared Brier noninferiority while reducing **measured end-to-end** CPU, maximum RAM, serialized checkpoint bytes, cold restore time, and fixed-source actions by >=2x against genuinely strong approximations; or
2. **Model misspecification/unfamiliar mechanism transfer:** on disjoint held mechanisms the learner's initial class does not explicitly cover, beat the *strongest fully fitted, equally informed and comparably flexible* conventional control, with an exact correct-specification Bayes control retained as an **oracle floor** (not a target to outperform).

Under (2), include non-Bayesian and flexible Bayesian dynamic controls, a frozen blind no-op, sham action, null causal effect, reversals, interference, and complete cold functional retention. Any training continuation must prove old knowledge still works; a JSON roundtrip alone is not cold retention.

## Mechanistic proposal to falsify
A bounded, action-conditional directed-flow state with *local contradictions, edge rewiring and uncertainty* could adapt to previously unseen action–transition relationships without rebuilding all known relationships. This differs from scalar equilibrium energy; cycle affinity measures nonconservative flow. However, a mechanism is **not novel intelligence** merely because it stores a graph, picks an action from known rules, or reproduces a Bayesian approximation.

Before allocating fresh primary trials, require:
- One native `NativeEpisodeExperience` / `NativeCausalAmalgam.observe_experience` interface audit as **read-only research seam**, subject to central Amalgam owner review; no direct edits or writes to that owner's branch.
- A disjoint, source-free frozen cohort with a structural break not visible in the learner's prior hypothesis class, separate fit/transfer/retention worlds and matched actions.
- At least fully trained contextual Dirichlet Markov, online change-point Bayes, dynamic graph Bayesian inference, and random/sham probes as controls; equal stream information, actions, memory/capacity constraints, and whole-process compute.
- Primary metric: novel-relationship intervention utility under held transitions, subject to absolute familiar-memory regression ceiling, false action-effect ceiling, and all-in efficiency. Test uncertainty calibration separately.
- Frozen stop: reject at 0/2 disjoint seeds showing qualifying advantage, any false causal effect, retention deterioration, information/custody mismatch, or compute overrun. Negative/null outcomes remain preserved. **These are design recommendations, not already frozen experimental thresholds.** A separate full `prereg.json` must be committed before any primary scoring.

## Authority, state and deployment
- `ENGINEERING`: algebraically testable proof; no claim of full native regression or atlas qualification.
- `SCIENCE`: mathematical restriction is exact. ENERGY-FLUX-01/TOPO-02 empirical claims stay bounded and negative; **no native scientific gain**.
- `DEPLOYMENT`: none. Preserve accepted `main`, the one cumulative Amalgam owner, source/seed custody, and all checkpoint lineages.
- Atlas CI on draft PR #1346 currently fails source-set pinning on Windows and Linux. Resolving it requires legitimate regeneration at one exact final source commit and full dual-platform qualification; do not disable or weaken the atlas guard just to turn CI green.
