TITLE: DG-1A-AR-H26 — Shared Evidence-Budget Contention / Runaway-Probe Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SHARED-BUDGET RESULT + URGENCY-MONOPOLY AND MYOPIC-STARVATION LIMITS
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh25-coupled-trust-layer-integration-audit.ice

PURPOSE
H25 showed that typed trust layers can interact safely only if:
- stored state is separated from current authority;
- trust cycles retain a bounded bootstrap evidence path.

H26 tests the next systems-level problem:

WHEN MULTIPLE TRUST LAYERS BECOME UNCERTAIN AT ONCE,
HOW SHOULD THEY SHARE ONE BOUNDED LOCAL EVIDENCE BUDGET?

The central risks are:

- runaway probing;
- urgency monopoly;
- starvation of slower adaptive layers;
- permanent structural-write suppression.

BOUNDARY
This is synthetic.

It does not:
- freeze a production token budget;
- define biological energy units;
- establish final layer stakes;
- justify one central scheduler;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TRUST / ADAPTIVE LAYERS
Five concurrent evidence consumers:

0
CAUSAL CONTROL.

1
VALUE-OF-INFORMATION / RESOURCE POLICY.

2
SLOW STRUCTURAL LEARNING.

3
CONTEXT / ROUTING.

4
PERSISTENT NOISY DEMAND.

Layer 4 is deliberately adversarial:

it stays highly uncertain,
looks urgent,
but additional probes have very low marginal value.

SHARED PROBE CAP
Maximum:

6 probe tokens per step.

PRIMARY PROBE COST
0.04 synthetic loss units per probe.

UNCERTAINTY DYNAMICS
Each layer accumulates:
- baseline uncertainty;
- occasional shocks.

Each probe reduces current uncertainty by a layer-specific resolvability factor.

Primary resolvability:

layer 0:
0.35

layer 1:
0.25

layer 2:
0.15

layer 3:
0.30

layer 4:
0.03.

Thus layer 4 is deliberately hard to resolve.

RAW URGENCY WEIGHTS
The noisy layer is given high apparent urgency:

layer 4 urgency:
8

despite low actual marginal benefit.

This creates a clean runaway-demand stress.

POLICIES

INDEPENDENT LOCAL PROBING
Each layer spends according to its own raw uncertainty with no shared cap.

This is a diagnostic baseline.

SHARED RAW-URGENCY GREEDY
Allocate each of six shared tokens to the layer with highest:

urgency
*
current uncertainty.

This ignores:
- probe resolvability;
- diminishing returns;
- true marginal functional value.

SHARED MARGINAL VoI
For each next probe:

score
=
functional_loss_weight
*
current_uncertainty
*
probe_resolvability
-
probe_cost.

Allocate the next token to the highest positive marginal score.

Stop early if all marginal scores are non-positive.

SHARED VoI + BOUNDED FAIRNESS
Same marginal-VoI allocator.

Additionally,
every tenth step,
reserve at most one audit token for a currently high-uncertainty layer with the lowest recent allocation share.

This is a crude anti-starvation mechanism.

It is not frozen.

PRIMARY CONFIRMATION
30 matched seeds.

4,000 steps per seed.

PRIMARY RESULTS

INDEPENDENT LOCAL PROBING

mean total synthetic loss:
2.53323

SD:
0.00551.

mean probes per step:
4.16983.

probe allocation shares:

layer 0:
2.33%.

layer 1:
5.78%.

layer 2:
13.76%.

layer 3:
3.65%.

layer 4 noisy demand:
74.48%.

INTERPRETATION
Even without a shared cap,
raw local uncertainty causes most evidence spending to flow into the chronically unresolved layer.

The system is not resource-aware enough.

SHARED RAW-URGENCY GREEDY

loss:
5.25117

SD:
0.05565.

probes:
6.0
every step.

allocation:

layer 0:
0.18%.

layer 1:
0.13%.

layer 2:
0.004%.

layer 3:
0.32%.

layer 4:
99.36%.

PRIMARY RUNAWAY / MONOPOLY NEGATIVE
The persistent noisy layer captures essentially the entire evidence budget.

Starvation fraction while a layer is highly uncertain:

layer 0:
96.0%.

layer 1:
99.3%.

layer 2:
99.97%.

layer 3:
93.7%.

layer 4:
0%.

This is a full evidence-budget monopoly.

High raw urgency plus persistent uncertainty creates:

PROBE STORM
+
STARVATION.

Thus:

MOST UNCERTAIN
or
MOST URGENT

does not imply:

BEST USE OF ONE MORE PROBE.

SHARED MARGINAL VoI

loss:
1.72281

SD:
0.00172.

mean probes:
3.25217.

allocation:

layer 0:
21.59%.

layer 1:
24.12%.

layer 2:
21.16%.

layer 3:
33.14%.

layer 4:
0%.

PRIMARY VoI POSITIVE
Marginal-value allocation rejects the chronically noisy layer because its:

uncertainty is high

but

expected reduction per probe is tiny.

Compared with raw urgency:

loss falls from:
5.25117

to:
1.72281.

Probe use falls from:

6.0

to:

3.25 per step.

The system is allowed to say:

THIS UNCERTAINTY IS NOT CURRENTLY WORTH RESOLVING.

This is critical for bounded developmental computation.

SHARED VoI + FAIRNESS

loss:
1.72339.

mean probes:
3.34587.

allocation:

layer 4 receives:
2.98%

of probe tokens.

The fairness mechanism slightly increases total resource use
and provides no primary-task advantage in this first working point.

This is expected:
the noisy layer truly has very low marginal utility.

Thus:

FAIRNESS SHOULD NOT MEAN
EQUAL ALLOCATION.

ANTI-STARVATION STRESS
A second benchmark changes layer 2,
slow structural learning.

Its immediate functional-loss weight is reduced to:

0.35.

This represents a layer whose:
short-horizon payoff is small

but
long-horizon evidence access is necessary for structural adaptation.

A structural-starvation event is defined as:

100 consecutive high-uncertainty steps

with
zero structural probes.

40 matched seeds.

MYOPIC VoI

mean loss:
1.62226.

mean probes:
2.57618.

structural layer allocation:
0.247%.

structural high-uncertainty starvation:
99.48%.

mean 100-step starvation events:
12.55 per run.

PRIMARY MYOPIC-VoI NEGATIVE
A purely immediate marginal-value objective can rationally starve:

slow
low-immediate-payoff
but strategically necessary

adaptation.

This is the opposite of the raw-urgency failure.

Raw urgency:
overspends on loud unresolved states.

Pure immediate VoI:
can underspend on slow-return structural learning.

VoI + BOUNDED FAIRNESS

mean loss:
1.59906.

mean probes:
2.67205.

structural allocation:
1.925%.

structural high-uncertainty starvation:
94.90%.

mean 100-step starvation events:
0.

PRIMARY FAIRNESS POSITIVE
The tiny reserved evidence path eliminates all tested 100-step structural-starvation events.

It does so while changing mean probe spending only modestly:

2.58
->
2.67.

Total synthetic loss also improves slightly in this stress.

The important result is not the exact improvement.

It is:

A SMALL MINIMUM EVIDENCE FLOOR
CAN PRESERVE LONG-HORIZON ADAPTIVE ACCESS
WITHOUT REVERTING TO EQUAL SHARES.

RELATION TO H25
H25 circular trust deadlock required:
bootstrap evidence.

H26 resource contention shows the same bootstrap path also protects against:
budget starvation.

Thus one bounded audit/fairness mechanism may serve two purposes:

1.
break epistemic deadlock;

2.
preserve minimum adaptive access.

RELATION TO S4-S9
S4-S9 established:
evidence is a local finite resource
and
should be allocated by value.

H26 adds a systems-level correction:

PURE GREEDY VALUE
IS NOT ENOUGH
WHEN SOME adaptive processes have:
delayed
or
long-horizon benefit.

The shared evidence economy therefore needs:

MARGINAL VALUE

plus

BOUNDED ANTI-STARVATION / BOOTSTRAP ACCESS.

CURRENT SHARED EVIDENCE-BUDGET RULE
Conceptually:

CURRENT UNCERTAINTY

+

FUNCTIONAL STAKE

+

EXPECTED PROBE RESOLVABILITY

+

DIMINISHING RETURNS

+

PROBE COST

+

URGENCY / DEADLINE

+

RECENCY / VALUE-POLICY TRUST

+

MINIMUM BOOTSTRAP / FAIRNESS FLOOR

->

NEXT LOCAL EVIDENCE TOKEN.

No layer receives permanent ownership of the budget.

GENERAL PRINCIPLE
Do not allocate adaptive resources by:

WHO IS LOUDEST.

Do not allocate them only by:

WHO HAS THE BEST IMMEDIATE RETURN.

Use:

MARGINAL VALUE
+
LONG-HORIZON ACCESS CONSTRAINTS.

DECISION
AR-H26 is POSITIVE.

Supported synthetically:

- a shared evidence budget prevents independent unlimited demand from becoming invisible;
- raw urgency can create near-total evidence monopoly;
- marginal VoI strongly suppresses a persistent low-resolvability probe hog;
- marginal VoI can stop probing before the budget is exhausted;
- pure short-horizon VoI can starve slow structural adaptation;
- a very small fairness/bootstrap path can eliminate long starvation episodes with little extra resource use.

Not demonstrated:

- final local budget representation;
- real Yggdrasil probe costs;
- learned long-horizon value;
- optimal fairness cadence;
- distributed token exchange among real cells;
- global resource conservation under population growth.

CLEAN SCIENTIFIC PAUSING POINT
H23-H26 now produce a coherent generic meta-controller boundary:

H23:
share update law,
not trust state.

H24:
retain distinct causal,
fit,
freshness,
and resource dimensions.

H25:
preserve learned state while suppressing current authority;
avoid circular trust deadlock.

H26:
share one bounded evidence economy using marginal value,
but preserve a small anti-starvation/bootstrap path.

NEXT HIGH-VALUE QUESTION
AR-H27 — DISTRIBUTED BUDGET WITHOUT CENTRAL TOKEN AUTHORITY

H26 uses one abstract shared local token budget.

Question:

Can many cells approximate this resource allocation without:
- one central scheduler;
- global queue;
- global role histogram?

Candidate mechanisms:

- local token diffusion;
- neighborhood prices;
- inhibitory resource fields;
- bounded bid / lease signals;
- local conservation.

The experiment should test:
- oversubscription;
- dead zones;
- local monopolies;
- spatial fairness;
- recovery after a high-demand region disappears.

This is a direct bridge from meta-control theory
toward the intended decentralized developmental architecture.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_matched_seeds = 30
primary_steps = 4000
shared_budget_per_step = 6
primary_probe_cost = 0.04
structural_starvation_seeds = 40
structural_starvation_window = 100
