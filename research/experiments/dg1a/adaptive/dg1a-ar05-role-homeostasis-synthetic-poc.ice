TITLE: DG-1A-AR-05/06 — Local Role-Homeostasis Synthetic Precursor
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX PRECURSOR — NOT FUNCTIONAL REGENERATION
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar

PURPOSE
Before attempting real functional-role regeneration, test the smallest local control question:

Can a population restore a depleted role fraction using only local neighborhood composition and a shared role-homeostasis rule?

This is NOT the functional-regeneration milestone.

It tests control stability only:
role fraction recovery
without proving the role performs useful computation.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BODY
40 x 40 lattice
radius-14 disk
613 live cells

Morphological occupancy is held fixed.
Selective role ablation changes role state but does not delete cells.

ROLES
Five synthetic roles:

growth
relay
repair
inhibitor
dormant

Declared target mixture:
growth     0.30
relay      0.20
repair     0.10
inhibitor  0.10
dormant    0.30

These ratios are toy control targets.
They are NOT proposed Yggdrasil biological constants.

PART A — HARD CATEGORICAL LOCAL RULE

Each cell has one categorical role.

Per step:
- stochastic update probability = 0.5;
- compute role fractions in a local square neighborhood;
- deficit(role) = target(role) - local_fraction(role);
- a cell may switch from an overrepresented current role to the most deficient role.

A hysteresis threshold h prevents switching unless:
current deficit < -h
and
best deficit > h.

TESTED NEIGHBORHOOD RADII
radius 1:
3 x 3

radius 2:
5 x 5

radius 4:
9 x 9

SELECTIVE ABLATION
After 100 stabilization steps:
70% of relay-role cells are reassigned to dormant.

Post-ablation:
160 homeostasis steps.

RECOVERY
relay fraction must remain in:
0.18..0.22
for 10 consecutive steps.

HARD-ROLE RESULT — IMPORTANT NEGATIVE

3 x 3 neighborhood
h = 0:
recovery rate = 45%
median recovery among successes = 2 steps
late switching = about 72.76 cells per step

This is chronic role chattering.

3 x 3 neighborhood
h = 0.05:
recovery rate = 0%
final relay fraction = about 0.159
late switching = about 2.33 cells per step

The combination of:
small discrete neighborhood
+
hard categorical roles
+
hysteresis

creates local ratio-resolution problems.

3 x 3 neighborhood
h = 0.12:
relay fraction can recover,
but total five-role mixture error remains materially worse.

Therefore:
a precise hard-role quota driven from a single instantaneous 3 x 3 neighborhood is a poor default design.

HARD-ROLE LARGER-NEIGHBOR RESULT
5 x 5 neighborhood
h = 0.05
20 seeds

70% relay ablation:
recovery rate = 95%
median recovery = 2 steps
final relay = 0.193
late switching = 0
mean total switches = 175.6

5 x 5
h = 0.08:

70% relay ablation:
recovery rate = 100%
median recovery = 2 steps
final relay = 0.193
late switching = 0

This shows the mechanism is feasible,
but it depends on a larger instantaneous composition estimate than Yggdrasil's current 3 x 3 perception directly provides.

PART B — SOFT ROLE LOGITS / PROBABILITIES

Because the roadmap already prefers soft roles,
a second toy uses continuous role mass per cell.

Each cell stores a normalized five-role vector.

Initialization:
near the target mixture with small multiplicative noise.

Local perception:
3 x 3 only.

Per step:
- stochastic update probability = 0.5;
- compute local mean soft-role vector;
- local deficit = target - local_mean;
- update log role mass by:
  log(p_new) = log(p_old) + eta * deficit
- renormalize with softmax.

No hard categorical role switch is required.

SELECTIVE RELAY ABLATION
To remove a declared fraction of total relay mass:
- select the most relay-like cells until the requested relay mass is reached;
- set their relay component to zero;
- transfer that mass to dormant;
- occupancy remains unchanged.

PRIMARY SOFT SETTING
eta = 0.8
3 x 3 local neighborhood
fire rate = 0.5

30 seeds per severity.

160-STEP RESULTS

relay-mass ablation | initial relay after ablation | recovery rate | median recovery | final relay
50%                 | 0.0978                       | 100%          | 47 steps        | 0.2075
70%                 | 0.0587                       | 100%          | 47.5 steps      | 0.2081
90%                 | 0.0195                       | 0% by 160     | not reached     | 0.1589
100%                | 0.0000                       | 0% by 160     | not reached     | 0.0148

Recovery criterion:
global relay mass remains in:
0.18..0.22
for 10 consecutive steps.

EXTENDED HORIZON
Same eta=0.8 / 3 x 3 soft-rule setup.

400-step horizon
20 seeds:

90% relay ablation:
recovery rate = 100%
median recovery = 215 steps

100% relay ablation:
recovery rate = 100%
median recovery = 325 steps

KEY RESULT
Soft local role homeostasis can restore even total removal of one synthetic role without changing morphology,
but recovery latency increases sharply with ablation severity.

This is substantially more informative than a binary pass/fail result.

SEVERITY-LATENCY PATTERN
50-70% loss:
about 47 steps

90% loss:
about 215 steps

100% loss:
about 325 steps

The local organism can recreate role mass from unrelated cells,
but near-total role extinction becomes a slow distributed reconstruction problem.

WHY SOFT ROLES ARE PREFERRED
The hard-role toy exposed:
- quantized local fractions;
- chattering without hysteresis;
- dead zones with excessive hysteresis.

The soft-role toy:
- works with 3 x 3 local perception;
- changes continuously;
- naturally supports partial specialization;
- avoids requiring every cell to choose one exclusive identity;
- aligns with the existing AR roadmap preference for soft role logits.

CRITICAL LIMITATION
This experiment hand-specifies the desired role mixture.

It does NOT show:
- that Yggdrasil will discover useful roles;
- that relay is a real functional specialization;
- that restored relay mass restores computation;
- that the correct global ratio is fixed across tasks;
- that a role target should be encoded explicitly in production.

Therefore this result must NOT be promoted to:
FUNCTIONAL REGENERATION.

WHAT IT DOES SHOW
A purely local shared controller can implement a viable negative-feedback mechanism for role composition.

That makes the later functional experiment mechanically plausible:

functional loss
->
local role deficit / performance error
->
soft role reassignment
->
eventual role population recovery.

The missing scientific step is proving that:
role identity corresponds to useful computation
and
restoring the role restores task performance.

DESIGN CONSEQUENCE
For future AR-05/06:
- prefer soft role logits;
- retain temporal state;
- do not enforce precise hard role quotas from one 3 x 3 snapshot;
- measure role turnover, not only final ratios;
- test severity-dependent recovery latency;
- include near-total ablation, not only modest loss;
- separate role-count recovery from functional recovery.

NEXT RESEARCH
Before real functional regeneration:
1. test whether role targets can emerge from local utility/error rather than hand-declared global ratios;
2. test spatially localized role deficits;
3. test whether role homeostasis remains stable under changing seasonal modes;
4. only then connect roles to a real computational task.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
hard_role_seeds = 20
soft_role_seeds_per_160_condition = 30
soft_role_seeds_per_extended_condition = 20
