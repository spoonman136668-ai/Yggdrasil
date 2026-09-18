TITLE: DG-1A Adaptive-Rule Research Frontier R3 — Causal Credit Boundary
DATE: 2026-09-18
STATUS: ACTIVE RESEARCH FRONTIER
TRACK: DG-1A / ADAPTIVE RULES
BRANCH: dg1a-ar
SOURCE_RESEARCH_HEAD: f1197477e3aedf1d89ce38379b3c806f63e858b4
CANONICAL_P0_HEAD_UNCHANGED: b45703418a7097782a032a142665c4642c2945fa

PURPOSE
Advance the R2 frontier after completion of AR-U6.

R1
STAB-18-R1 remains frozen and unexecuted.
Canonical seed-0 / 200-iteration execution remains unspent.
No adaptive-rule result modifies R1.

NEW COMPLETED RECORD

AR-U6
research/experiments/dg1a/adaptive/dg1a-aru6-delayed-confounded-causal-credit-audit.ice

CORE RESULTS

1. DELAYED OBSERVATIONAL CREDIT DEGRADES TOWARD CHANCE

With environmental random-walk drift,
naive:

future consequence
-
current consequence

loses causal-sign accuracy as delay and environmental variance increase.

At delay 32 / per-step sigma 0.20:
accuracy = 51.65%.

2. MATCHED FUTURE DISTURBANCE IS HIGHLY PROTECTIVE

Compare:
perturbed future
vs
intact future

under the same environmental disturbance realization.

Across all tested:
delay = 1,4,16,32
sigma = 0.02,0.05,0.10,0.20

sign accuracy remained approximately:
96.4..96.6%.

This residual error is dominated by measurement noise in the toy.

3. DOMAIN SEPARATION FIXES BIAS, NOT ALL VARIANCE

When the same random variable both:
selects the probe
and
contributes to future disturbance,

a truly harmful +0.01 action is falsely classified beneficial at:

76.25%
93.02%
96.07%
97.51%

as tested disturbance scale increases.

Independent probe-selection randomness restores the mean estimate to approximately the true +0.01 effect,
but noisy single-trajectory sign errors remain common.

A matched intact/perturbed future removes that common disturbance and drives the false-benefit rate to about 0.02% in this toy.

4. SIMULTANEOUS ACTION CREDIT IS NOT IDENTIFIABLE FROM ONE SCALAR

When two local role changes happen simultaneously
and one combined consequence is credited to both:

approximately 24.89% of reinforced role assignments are individually harmful in the balanced additive toy.

Therefore:
one later scalar reward cannot safely identify which simultaneous local action caused improvement.

CURRENT META-RULE REQUIREMENTS

A future local adaptation mechanism should preserve:

ACTION IDENTITY
what changed?

TEMPORAL ELIGIBILITY
which prior change is still eligible for credit?

DISTURBANCE COMPARABILITY
what changed in the environment independently?

CONSEQUENCE
what local outcome improved?

CREDIT
which action caused the improvement?

These are separate state variables/concepts.

DO NOT IMPLEMENT LITERAL FULL COUNTERFACTUALS YET
Paired futures are an information-theoretic control,
not necessarily an affordable production mechanism.

The next research problem is to approximate their causal reliability cheaply.

NEXT PRIMARY FRONTIER

AR-U7 — CHEAP CAUSAL CREDIT APPROXIMATIONS

Compare:

A.
naive delayed local consequence

B.
sparse staggered one-role perturbation
+
eligibility trace

C.
local predictive-error residual
+
action tag

D.
short paired local future probe
where affordable

Evaluate:
- causal-sign accuracy;
- wrong-role reinforcement;
- adaptation quality;
- compute/update overhead;
- sensitivity to delay;
- environmental confounding.

PARALLEL FRONTIER

AR-C1 — REPEATED DECENTRALIZED CONTEXT ORDERING

The existing context relay solves one mode transition only.

Need repeated local switch ordering without:
- global broadcast;
- stale-context overwrite;
- a second controller.

READINESS STATEMENT
The synthetic research now supports:
- conditional shared-rule regimes;
- context robustness mapping;
- decentralized relay plausibility;
- soft role homeostasis;
- utility-driven functional placement;
- multi-role coexistence;
- reversible moving-demand specialization;
- freshness-aware utility memory;
- partially independent credit evidence;
- derivative-free local consequence adaptation;
- explicit causal-confound characterization.

Still NOT shown:
- real Yggdrasil emergent functional roles;
- real computational regeneration;
- learned local consequence source;
- cheap causal credit in the real NCA;
- developmental cognition.

NEXT ACTION
AR-U7.

PROVENANCE
evidence_class = RESEARCH_FRONTIER_SUMMARY
canonical_scientific_execution = false
canonical_r1_execution_spent = false
