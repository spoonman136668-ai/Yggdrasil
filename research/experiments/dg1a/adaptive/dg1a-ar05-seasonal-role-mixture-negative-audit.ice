TITLE: DG-1A-AR-05/06 — Seasonal Fixed Role-Mixture Negative Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX NEGATIVE — DO NOT HARD-CODE SEASONAL ROLE QUOTAS
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-ar05-role-homeostasis-synthetic-poc.ice

PURPOSE
Test a tempting direct integration of:
AR-01 seasonal modes
with
AR-05/06 role homeostasis.

Naive proposal:
each season directly specifies a desired global mixture of soft cell roles.

Question:
Can a 3 x 3 local controller reliably track those changing global role mixtures over an AR-01-like lifecycle?

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BOUNDARY
This is a deliberately simple negative control.

It does not:
- identify real Yggdrasil roles;
- train a functional task;
- execute Yggdrasil;
- alter AR-01;
- execute STAB-18-R1.

BODY
40 x 40
radius-14 disk
613 live cells

SOFT ROLES
growth
relay
repair
inhibitor
dormant

SEASONAL TARGET MIXTURES
Rows sum to 1.

EXPANSION
growth     0.45
relay      0.15
repair     0.05
inhibitor  0.10
dormant    0.25

CONSOLIDATION
growth     0.25
relay      0.20
repair     0.10
inhibitor  0.15
dormant    0.30

MAINTENANCE
growth     0.15
relay      0.20
repair     0.10
inhibitor  0.10
dormant    0.45

REPAIR
growth     0.15
relay      0.15
repair     0.40
inhibitor  0.10
dormant    0.20

DORMANCY
growth     0.05
relay      0.10
repair     0.05
inhibitor  0.10
dormant    0.70

REACTIVATION
growth     0.35
relay      0.20
repair     0.15
inhibitor  0.10
dormant    0.20

These targets are not biological claims.
They intentionally demand substantial role reallocation.

LOCAL CONTROL
3 x 3 neighborhood only.
stochastic update probability = 0.5.

Primary multiplicative soft-role update:
local_deficit = target_mix - local_mean_mix

log(p_new) =
log(p_old)
+
eta * local_deficit

then softmax normalize.

PRIMARY eta:
0.3

PHASE LENGTH
96 steps per season.

SUCCESS
Global role-mixture L1 error:
<= 0.05

for 8 consecutive steps.

PRIMARY RESULT — eta 0.3
20-seed initial sweep:

EXPANSION:
success = 100%
median latency = 1 step

CONSOLIDATION:
success = 100%
median latency about 73 steps

MAINTENANCE:
success about 80%
median latency about 78 steps among successes

REPAIR:
success = 0%
final mean L1 error about 0.103

DORMANCY:
success = 0%
final mean L1 error about 0.241

REACTIVATION:
success = 0%
final mean L1 error about 0.329

NEGATIVE
The multiplicative rule becomes strongly history-dependent / canalized.

Role components driven very low in one regime recover too slowly when a later regime needs them.

PLASTICITY-FLOOR TEST
To prevent any role from becoming too small,
mix the updated role vector with a uniform floor mass.

Tested floor mass:
0
0.005
0.01
0.02
0.05
0.10

8 seeds per floor condition.
eta = 0.3.

Result:
No tested floor produced successful tracking of REPAIR, DORMANCY, and REACTIVATION under the 96-step success criterion.

Small floors improved some later final errors,
but larger floors increasingly prevented accurate expression of strongly specialized regimes.

Examples:

floor = 0
final L1:
REPAIR ~0.103
DORMANCY ~0.237
REACTIVATION ~0.327

floor = 0.005
final L1:
REPAIR ~0.054
DORMANCY ~0.172
REACTIVATION ~0.136

floor = 0.010
final L1:
REPAIR ~0.056
DORMANCY ~0.154
REACTIVATION ~0.089

The floor reduces canalization but imposes a competing inability to specialize.

Therefore:
STATIC PLASTICITY FLOOR != SOLUTION.

ADDITIVE ROLE-UPDATE ABLATION
A second local controller used:

p_new =
normalize(
    clip(
        p_old
        +
        eta * local_deficit,
        0,
        infinity
    )
)

Tested eta:
0.02
0.05
0.10
0.20
0.40
0.80

16 seeds per 96-step condition.

Result:
No eta successfully tracked all six seasonal mixtures.

Representative:

eta = 0.05
CONSOLIDATION:
100% success
median ~83 steps

MAINTENANCE:
100% success
median ~78 steps

REPAIR:
0% success

DORMANCY:
0% success

REACTIVATION:
0% success

eta = 0.80
CONSOLIDATION:
100% success
median ~21 steps

MAINTENANCE:
12.5% success

REPAIR:
6.25% success

DORMANCY:
0% success

REACTIVATION:
87.5% success
median ~59 steps among successes

Higher gain accelerates some transitions while destabilizing or mis-tracking others.

LONGER DWELL-TIME TEST
Additive controller.

eta:
0.05
0.10
0.20
0.40

phase lengths:
96
192
384

8 seeds per combination.

Across every tested eta/dwell combination:
the minimum success rate across post-expansion modes remained:
0%

Longer dwell time alone therefore did not solve the architecture mismatch.

INTERPRETATION
The problem is not merely:
"give roles more time."

A fixed global role quota is a poor object for a purely local controller.

Reasons include:
- local neighborhoods need not reproduce the global mixture;
- boundary neighborhoods differ;
- different spatial regions may legitimately need different roles;
- specialization creates history dependence;
- a useful organism should allocate roles according to local functional demand, not satisfy a global histogram.

KEY NEGATIVE
DO NOT DEFINE ROLE HOMEOSTASIS AS:
season
->
fixed global role ratios
->
local cells forced to match those ratios.

That architecture is both over-specified and mechanically awkward.

PREFERRED DIRECTION
Season should modulate local incentives or sensitivities.

Roles should respond to:
- local task utility;
- local information bottlenecks;
- predictive error;
- missing-neighbor functionality;
- communication demand;
- repair demand;
- resource state.

Desired behavior:

season/context
->
changes the value/cost of local functions

local evidence
->
drives soft role adaptation

collective role distribution
->
emerges

rather than being directly prescribed.

RELATION TO END GOAL
This is favorable for the developmental-intelligence thesis.

A fixed global role mixture would effectively encode a handcrafted body plan for computation.

Utility-driven local role allocation leaves open the more powerful possibility:
different tasks and injuries produce different computational organizations from the same developmental genome.

NEXT RESEARCH
Before functional-regeneration execution:
design a synthetic utility-driven role market where no global target ratios are provided.

Candidate local utility terms:
- communication delay reduction;
- local prediction-error reduction;
- damage-response contribution;
- energy/update cost;
- redundancy benefit;
- neighborhood bottleneck relief.

Test whether useful role distributions emerge and recover after selective ablation.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX_NEGATIVE
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
