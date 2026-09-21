TITLE: YGGDRASIL A28 / T8L — Distributed Dynamical Uncertainty Regimes
DATE: 2026-09-21
STATUS: PREREGISTERED DYNAMICAL-STATE EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8L / APPLICATION-A
PARENT: A27 Negative-Feedback Homeostatic Authority Correction
BRANCH: dg1a-ar

PURPOSE

A27 proved that negative feedback can materially repair bad trajectories,
but a short adverse block is noisy enough to create false corrections.

A28 tests the architectural hypothesis that uncertainty should not be represented
as one cumulative confidence number.

Instead,
uncertainty is encoded in the organism's own dynamical state:

STABLE;
METASTABLE;
COMMITTED.

Scalar measurements remain external experiment instrumentation only.

The controller itself stores:

current regime;
short persistence history;
and the actual candidate/stale policy composition carried by living cells.

It stores no cumulative confidence score.

BIOLOGICAL TRANSLATION

STABLE

Interpretation:

evidence has resolved against candidate authority.

Behavior:

candidate birth authority = 0 / 4.

The learned patch remains preserved but dormant.

STABLE is absorbing in A28.
Reactivation is not tested here.

METASTABLE

Interpretation:

uncertainty remains unresolved.

Behavior:

exactly 2 / 4 newborns receive candidate birth control.

Which two newborn slots receive candidate control changes deterministically
from a frozen post-freeze hash namespace.

This produces bounded population heterogeneity
without outcome-selected randomness.

COMMITTED

Interpretation:

persistent positive consequence has shifted the system
into a high-authority attractor.

Behavior:

3 / 4 newborns receive candidate birth control.

A28 never grants 4 / 4 authority.

COMMITTED has hysteresis:

entry requires two consecutive positive blocks;

exit requires three consecutive negative blocks.

Thus ordinary small reversals do not immediately undo commitment.

PARENT FRONTIER

A27 closure:

9d3467759563120c80c79681a7fb99a504c9e159.

A27 finding:

negative feedback rescued harmful trajectories,
but false correction nearly canceled trajectory-level safety gains.

A28 FREEZE

Let the exact A28 implementation freeze commit be:

F28.

No real A28 trajectory,
regime transition,
population-composition outcome,
or scientific result
may be derived before F28 exists.

FRESH TRAJECTORIES

After F28,
derive exactly:

384

fresh trajectories:

48 fixed A17 patch contexts
x
8 F28-derived replicas.

Each trajectory contains:

40 fresh demand epochs.

Control blocks:

B1 = 0-3;
B2 = 4-7;
B3 = 8-11;
B4 = 12-15;
B5 = 16-19;
B6 = 20-23;
B7 = 24-27;
B8 = 28-31;
B9 = 32-35;
B10 = 36-39.

Replacement episodes:

0;
4;
8;
12;
16;
20;
24;
28;
32;
36.

Every 40-demand sequence has exact mean
equal to the candidate target prior.

All demand / replacement / heterogeneity namespaces:

YGG-A28-*.

MATCHED STALE TWIN

Every controller runs against
an exact all-stale twin.

Controller and twin receive:

identical demands;
identical replacement cell IDs;
identical inherited migration rules.

BLOCK ERROR

After each four-epoch block:

E_i =
controller service
-
matched stale-twin service.

Only the SIGN of E_i drives regime transition.

Magnitude does not.

This avoids reintroducing A26 signal-magnitude thresholding.

INITIAL CONDITION

Every A28 dynamical controller begins in:

METASTABLE.

Reason:

the learned patch exists,
but authority is unresolved.

No scalar confidence is initialized.

DYNAMICAL TRANSITIONS

METASTABLE:

two consecutive positive block errors
->
COMMITTED.

two consecutive negative block errors
->
STABLE.

mixed signs or zero
->
remain METASTABLE.

COMMITTED:

positive or zero evidence
->
remain COMMITTED.

three consecutive negative block errors
->
METASTABLE.

This is the preregistered hysteresis.

STABLE:

remains STABLE for the rest of A28.

A28 does not test dormant reactivation.

METASTABLE HETEROGENEITY

At each METASTABLE replacement:

exactly two of four newborn slots
receive candidate birth-control authority.

The chosen two slots are selected by
a deterministic cryptographic ordering derived only from:

trial identity;
block identity;
birth-slot identity.

No observed outcome affects slot selection.

Across the experiment,
all six possible 2-of-4 subsets are permitted.

Living cells are tagged with the policy source
that governed their birth:

candidate;
or stale.

That policy tag persists until cell replacement.

It is measurement of distributed state,
not a scalar confidence variable.

COMMITTED POPULATION

At each COMMITTED replacement:

the first three canonical newborn slots
receive candidate birth control.

The fourth remains stale-controlled.

STABLE POPULATION

At each STABLE replacement:

all four newborns use stale birth control.

No existing living cell is forcibly rewritten
when the regime changes.

REFERENCE / ABLATION CONTROLLERS

R3 — STATIC C3

3 / 4 candidate-controlled newborns
at every replacement.

This is the A27 static reference.

H1 — A27 ONE-STEP NEGATIVE FEEDBACK

Starts at authority 3.

Every negative block reduces future birth authority by one.

Nonnegative block holds.

No re-escalation.

This is the direct comparator
for A27's false-correction problem.

DYN — FULL A28 DYNAMICAL CONTROLLER

Three regimes;
METASTABLE heterogeneity;
two-positive commitment;
three-negative hysteretic exit;
absorbing STABLE.

NO_HYST — HYSTERESIS ABLATION

Identical to DYN,
except COMMITTED exits to METASTABLE
after two consecutive negative blocks.

NO_HET — HETEROGENEITY ABLATION

Identical regime-transition rules to DYN,
but every METASTABLE replacement
always gives candidate authority
to fixed newborn slots 0 and 1.

No rotating heterogeneous subset.

R0 — ALL STALE

External service reference.

R4 — ALL CANDIDATE

External full-candidate reference.

PRIMARY METRICS

For R3 / H1 / DYN / NO_HYST / NO_HET report:

aggregate 40-epoch service;

delta versus R0;

delta versus R3;

trajectory outcomes versus R0:

beneficial;
neutral;
harmful;

harmful-trajectory rate;

worst cumulative drawdown.

STATIC-C3 HARM CONTAINMENT

Let STATIC-HARMFUL mean:

R3 delta versus R0 < 0.

Report:

count;
improved relative to R3;
fully rescued to neutral-or-better.

STATIC-C3 BENEFIT RETENTION

Let STATIC-BENEFICIAL mean:

R3 delta versus R0 > 0.

Report:

count;
remaining beneficial.

FALSE-CORRECTION METRIC

Let STATIC-NONHARM mean:

R3 delta versus R0 >= 0.

Report how many STATIC-NONHARM trajectories
become harmful under each controller.

This directly targets A27's false-correction failure.

DYNAMIC-STATE METRICS

For DYN / NO_HYST / NO_HET report:

block occupancy in:

STABLE;
METASTABLE;
COMMITTED;

transition counts;

candidate-policy living-cell count
after each replacement;

mean candidate-policy living cells;

METASTABLE birth-slot subsets used;

time to commitment;

time to STABLE;

COMMITTED dwell duration;

COMMITTED exit count.

PRIMARY QUALIFICATION

DYN is DYNAMICAL-QUALIFIED iff all are true:

harmful-trajectory rate <= 0.05

AND

aggregate service >= R0

AND

at least 50% of STATIC-HARMFUL trajectories improve over R3

AND

at least 50% of STATIC-BENEFICIAL trajectories remain beneficial

AND

worst cumulative drawdown
is no worse than R3

AND

all integrity probes pass.

A28_DYNAMICAL_STATE_INFORMATION_GAIN

TRUE iff DYN:

has lower harmful-trajectory rate than H1

AND

creates fewer new harmful trajectories
from STATIC-NONHARM cases than H1

AND

rescues at least 75%
as many STATIC-HARMFUL trajectories
to neutral-or-better as H1

AND

aggregate service >= R0.

This is descriptive evidence only.

It does not authorize autonomous use.

INTEGRITY PROBES

P1:
exact A17 replay unchanged.

P2:
384 unique post-F28 trajectories.

P3:
40 demands per trajectory;
exact mean equals candidate target.

P4:
replacement episodes exactly
0 / 4 / 8 / 12 / 16 / 20 / 24 / 28 / 32 / 36;
four unique IDs each.

P5:
DYN starts METASTABLE.

P6:
STABLE candidate birth authority exactly 0 / 4.

P7:
METASTABLE candidate birth authority exactly 2 / 4.

P8:
COMMITTED candidate birth authority exactly 3 / 4.

P9:
DYN METASTABLE uses more than one 2-of-4 subset mechanically.

P10:
NO_HET METASTABLE always uses slots 0 and 1.

P11:
COMMITTED entry can only occur from METASTABLE
after positive persistence.

P12:
DYN cannot jump directly COMMITTED -> STABLE.

P13:
STABLE is absorbing.

P14:
no controller creates 4 / 4 candidate authority.

P15:
no cumulative scalar confidence variable exists.

P16:
regime changes affect future births only.

P17:
learned patch remains preserved in STABLE.

P18:
restart equivalence at every block boundary.

P19:
two complete primary sweeps byte-identical.

P20:
no C-v3;
no duplicate context;
major history [v1,v2];
slot count 3.

NEGATIVE / LIMIT CONTROLS

N1 — STATIC C3

R3.

N2 — A27 H1

one-step reactive feedback.

N3 — NO HYSTERESIS

NO_HYST.

N4 — NO METASTABLE HETEROGENEITY

NO_HET.

N5 — CUMULATIVE CONFIDENCE SCORE

not permitted in A28.

N6 — FULL 4 / 4 COMMITMENT

not permitted in A28.

N7 — QUORUM AUTHORITY

not permitted in A28.

N8 — DORMANT REACTIVATION

not tested in A28.

PRE-REGISTRATION DEVELOPMENT NOTE

Before this preregistration file was committed,
the implementation design was exercised once
on a synthetic developer-only seed:

MECHANICAL-F28-NONPRIMARY.

That run was used only to verify
that the proposed controller was executable and nontrivial.

No real F28 world existed.

No scientific trajectory was observed.

No transition rule,
persistence requirement,
heterogeneity rule,
qualification threshold,
or ablation rule
was changed in response to the developer-only outcome.

The mechanical run is non-scientific
and will be recorded again at implementation freeze.

INTERPRETATION

If DYN reduces H1 false correction
while preserving most H1 rescue behavior,
the three-regime state dynamics
add information beyond reactive negative feedback.

If NO_HET performs materially worse than DYN,
population heterogeneity itself contributes useful exploration.

If NO_HYST performs materially worse than DYN,
commitment hysteresis contributes stability.

If DYN merely reduces harm by collapsing rapidly into STABLE,
it has become conservative rather than intelligent.

If DYN remains unsafe,
distributed dynamical state alone is insufficient
and later mechanisms must be added.

PLAIN-SPEAK QUESTION

A28 stops asking Yggdrasil
to calculate one number called confidence.

Instead,
the organism has three ways of physically existing.

STABLE:

the old state dominates
and the patch becomes dormant.

METASTABLE:

the organism admits that it does not know.

Half of each newborn group explores the candidate policy
and half stays with the old policy.

Which newborns explore changes over time,
so uncertainty appears as real population diversity.

COMMITTED:

persistent positive experience moves the organism
into a high-authority state.

Once committed,
ordinary noise cannot immediately knock it back out.

That is hysteresis.

The question is:

CAN UNCERTAINTY LIVE IN THE ORGANISM'S DYNAMICS
INSTEAD OF IN A NUMBER?

And more specifically:

CAN THAT DYNAMIC STATE
KEEP A27'S ABILITY TO REPAIR BAD TRAJECTORIES
WITHOUT FALSELY CORRECTING AS MANY GOOD ONES?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A28 DISTRIBUTED DYNAMICAL UNCERTAINTY REGIMES

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F28-DERIVED TRAJECTORY,
REGIME TRANSITION,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

e62838c07378ad2ec80d65924396746f8923d3a8.

SOURCE BUNDLE

Loader:

research/applications/track-a/a28_t8l_dynamical_uncertainty_regimes_v1.py

Loader Git blob:

d6462600858c47602cb525b83107b3387ff9821c.

Payload:

research/applications/track-a/a28_t8l_dynamical_uncertainty_regimes_v1.py.gz

Payload Git blob:

4e08a2fa6b87116b1811ef88e156c319a2fef224.

Decompressed source SHA-256:

26878a56abe92a9a42fb47af7e4b0e301fceb2843a7c12d259dfa217b44081cd.

Decompressed source bytes:

17881.

Deterministic gzip SHA-256:

cd001cf6735f7d3e74fc8cfc6da1579deb5daf3507eb288b0fa95f8b5a43ae1c.

Compressed payload bytes:

5438.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F28-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized result-file SHA-256:

fdc8d2d647ea93e90133e87229b5e67d047cfbd6c90bf3b28bfb56a115eb6a2a.

Serialized semantic output SHA-256:

5910a026790a45e36cdb271f177c1a56359ae874cba4bbbf7dee7ad5f9f1cbe1.

All P1-P20 integrity probes:

PASS.

Exact A17 replay remained:

3978 / 3950 / 37-of-48
with the exact 11 below-stale pairs.

MECHANICAL R3

delta versus R0:

-100.

harmful trajectories:

177 / 384;
46.09%.

MECHANICAL H1

delta versus R0:

+30.

harmful trajectories:

170 / 384;
44.27%.

static-harmful rescued:

41.

false harm from static-nonharm:

34.

MECHANICAL DYN

delta versus R0:

+191.

harmful trajectories:

144 / 384;
37.50%.

static-harmful improved:

127.

static-harmful rescued:

65.

static-beneficial retained:

123.

false harm from static-nonharm:

32.

regime occupancy:

STABLE = 492 blocks;
METASTABLE = 2780 blocks;
COMMITTED = 568 blocks.

transitions:

METASTABLE -> COMMITTED = 118;
METASTABLE -> STABLE = 96;
COMMITTED -> METASTABLE = 4.

all six 2-of-4 METASTABLE birth-slot subsets were exercised.

MECHANICAL NO_HYST

delta versus R0:

+181.

harmful trajectories:

144 / 384;
37.50%.

MECHANICAL NO_HET

delta versus R0:

+30.

harmful trajectories:

160 / 384;
41.67%.

The mechanical result suggests
that heterogeneous metastable population state
can matter materially.

However:

DYN remained far above
the absolute 5% harmful-trajectory ceiling.

DYN was NOT qualified.

This mechanical evidence is NON-SCIENTIFIC.

REAL A28 STATUS

No real F28 trajectory has been derived.

No real regime transition has been observed.

No real scientific population-composition outcome exists.

Let the resulting commit SHA be:

F28.

After F28 exists:

1. derive exactly 384 fresh 40-epoch trajectories from F28;
2. bind the complete manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. compare DYN to H1, NO_HYST, and NO_HET without post-result tuning.

NO TRANSITION-RULE CHANGE.
NO PERSISTENCE-RULE CHANGE.
NO HETEROGENEITY-RULE CHANGE.
NO QUALIFICATION CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A28 DISTRIBUTED DYNAMICAL UNCERTAINTY REGIMES

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A28 REGIME TRANSITION
OR SCIENTIFIC OUTCOME.

F28:

2994159bf6b17b14a0c444c2cad388eb6a81a0b8.

FROZEN SOURCE SHA-256:

26878a56abe92a9a42fb47af7e4b0e301fceb2843a7c12d259dfa217b44081cd.

TRAJECTORY COUNT:

384.

STRUCTURE:

48 fixed A17 patch contexts
x
8 fresh F28-derived replicas.

EPOCHS PER TRAJECTORY:

40.

CONTROL BLOCKS:

10 blocks of 4 epochs.

REPLACEMENT EPISODES:

0 / 4 / 8 / 12 / 16 / 20 / 24 / 28 / 32 / 36.

COMPLETE MANIFEST SHA-256:

ff89829d8952ce0e38792a0105cb86d2a0a8cd7405ecd39d714d7f93372f9009.

Serialized manifest-wrapper SHA-256:

71355406c0a219b8e9fe8761260fad2d04ed9a00ddbf8cf16b8ee752ac3ee864.

Serialized manifest-wrapper bytes:

269345.

Every 40-demand sequence has exact mean equal to its candidate target.

Every replacement set contains exactly four unique cell IDs.

All scientific namespaces are:

YGG-A28-*.

PRIMARY STATUS AT MANIFEST BIND

Real DYN regime transitions observed:

0.

Real H1 outcomes observed:

0.

Real NO_HYST outcomes observed:

0.

Real NO_HET outcomes observed:

0.

The next permitted operation is:

two complete deterministic A28 primary sweeps
over this exact manifest.

NO TRAJECTORY REDRAW.
NO TRANSITION CHANGE.
NO HYSTERESIS CHANGE.
NO HETEROGENEITY CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
