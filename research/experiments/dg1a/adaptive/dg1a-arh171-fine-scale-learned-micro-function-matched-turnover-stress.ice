TITLE: DG-1A-AR-H171 — Fine-Scale Learned Micro-Function Matched-Turnover Stress
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh170-learned-micro-function-regeneration-turnover-audit.ice

PURPOSE

H170 established:

learned micro-function regeneration
is not scale neutral.

At:
g=1.00,

coarse learned specialization
can degrade materially
under:
ROAMING turnover
and:
noisy local labels.

At:
g=0.25,

the learned classifier
retains:
task accuracy,
Brier calibration,
and:
learned-output fidelity

through:
40 fixed repair events.

But:

40 events
at:
g=0.25

represent:
far less than:
one full body-equivalent
learned-state turnover.

H171 asks:

CAN THE FINE-SCALE
LEARNED MICRO-FUNCTION ARCHITECTURE

SURVIVE:

APPROXIMATELY ONE
BODY-EQUIVALENT
OF:
CUMULATIVE LEARNED-STATE REPLACEMENT

WITHOUT:

- checkpoint restoration;
- global retraining;
- expanding:
  the local functional budget;
- catastrophic accuracy / calibration drift?

BOUNDARY

Synthetic computational research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

PARENT MODEL

Reuse:
the exact H170
learned binary-classification substrate.

Cell scale:

g=0.25 only.

Body:

R=32.

N approximately 3209 cells.

Tasks:

SMOOTH,
MIXED.

Teacher,
training,
validation,
test,
student readout,
ridge alpha,
feature sigma:

unchanged from H170.

LEARNED BASELINE

Every world:

trains:
one cellular readout

from:
512 labeled training examples.

Test:
512 held-out examples.

No primary world
is discarded
for scientific performance.

Baseline competence
remains:
an acceptance gate.

DAMAGE

f0=0.05.

beta=2.

At g=.25:

expected damage:
approximately 11 cells / event.

TURNOVER

ROAMING
and:
HOTSPOT.

Persistent repaired state:
carries forward.

MATCHED BODY-EQUIVALENT LIFETIME

cycles =
ceil(
N / damage_cells
).

Expected:

approximately:
292 cycles.

Thus:

total replacement events
are:
approximately:
one full body count.

No cycle count
is reduced
because:
the fine-scale repair
is easy.

FUNCTIONAL FEEDBACK

eta:

0,
0.10.

Observed target:

teacher binary label.

Noise:

deterministic label flip
with probability eta.

QUERY / PURCHASE CONTROL

Reuse:
accepted H169
target-blind controller.

Always:

one maximum-leverage query.

Second query iff:

rho_geom >=0.98

OR:

cycle>1
AND:
rho_geom<=0.50
AND:
novelty5>=0.75.

At g=.25,
history trigger should normally remain:
inactive
because:
rho_geom
is in:
the fine-scale information regime.

No:
target value
enters:
query-purchase authority.

POLICIES

A — CONTEXT-ONLY

Developmental repair only.

B — MICRO2-LEVERAGE

Two information-designed labels
every cycle.

Learned-task reference.

C — HIST-GEOM-1PLUS1

Primary candidate.

D — LOCAL-CHECKPOINT-ORACLE

Restores:
the original learned cell coefficient
when:
a damaged cell returns.

Evaluation ceiling only.

PRIMARY FACTORIAL

Task:

SMOOTH,
MIXED.

Turnover:

ROAMING,
HOTSPOT.

eta:

0,
0.10.

Worlds / cell:

10.

Underlying worlds:

2 x 2 x 2 x 10
=
80.

Policies:

4.

Policy lifetimes:

320.

Expected repair cycles:

approximately:
93,440.

PRIMARY METRICS

1.
baseline test accuracy;

2.
HALF test accuracy;

3.
FINAL test accuracy;

4.
accuracy loss
relative to:
pre-lesion baseline;

5.
fraction of worlds
within:
0.05 accuracy
of:
baseline;

6.
baseline Brier;

7.
FINAL Brier;

8.
Brier degradation;

9.
HALF learned-output fidelity;

10.
FINAL learned-output fidelity;

11.
HALF-to-FINAL
learned-output fidelity loss;

12.
late-life SelfRecovery;

13.
cumulative absolute
test-logit error exposure;

14.
body-equivalent turnover;

15.
maximum per-cell
replacement count;

16.
second-query duty;

17.
total observations;

18.
observation reduction
versus:
MICRO2-LEVERAGE;

19.
ROAMING / HOTSPOT interaction;

20.
clean / noisy-label interaction;

21.
oracle gap.

BASELINE COMPETENCE GATE

For:
SMOOTH
and:
MIXED,

median pre-lesion
test accuracy

>=0.85.

PRIMARY ACCEPTANCE SHAPE

H171 supports:
FINE-SCALE
LEARNED MICRO-FUNCTION
MATCHED-TURNOVER STABILITY

if:

1.
Baseline competence gate passes
for:
both task classes.

2.
HIST-GEOM
median FINAL test accuracy

is:
no more than:
0.03 absolute

below:
its own baseline

for:
every:
task x regime x eta group.

3.
>=90%
of HIST-GEOM worlds

finish:
within:
0.05
accuracy
of:
their own baseline

for:
every group.

4.
HIST-GEOM
median FINAL learned-output fidelity

>=0.95
for:
every group.

5.
HIST-GEOM
median HALF-to-FINAL
learned-output fidelity loss

<=0.02
for:
every group.

6.
HIST-GEOM
median Brier degradation

<=0.03
for:
every group.

7.
HIST-GEOM
cumulative absolute
test-logit error exposure

<=1.35x
MICRO2-LEVERAGE

for:
every group.

8.
HIST-GEOM
uses:
fewer observations
than:
MICRO2-LEVERAGE

for:
every group.

9.
HOTSPOT:

median maximum
per-cell replacement count

>=20

for:
both task classes
and:
both eta values.

This confirms:
deep repeated local
learned-state turnover.

10.
LOCAL-CHECKPOINT-ORACLE
retains:
exact baseline learned output.

SELF-RECOVERY

Because H170 showed:
relative SelfRecovery
can become unstable
when:
lesion effect denominators
are very small,

H171 reports:
SelfRecovery
as:
diagnostic,

not:
a primary pass/fail gate.

Instead:
absolute test-logit exposure
and:
accuracy retention

are:
the long-horizon functional criteria.

This change is:
preregistered
before:
H171 primary.

STRONG SUPPORT

H171 receives:
STRONG support

if:

all primary gates pass

and:

HIST-GEOM
pooled FINAL accuracy loss

<=0.01

and:

pooled cumulative exposure
<=1.15x
MICRO2-LEVERAGE.

MIXED / NEGATIVE CONDITIONS

Treat H171 as:
mixed / negative
if:

- fine learned-task accuracy
  drifts:
  under:
  one body-equivalent turnover;

- noisy labels
  accumulate:
  semantic loss;

- repeated HOTSPOT replacement
  degrades:
  learned specialization;

- H169's one-plus-one budget
  becomes:
  insufficient
  over:
  292 cycles;

- calibration drifts
  even when:
  top-line accuracy remains high;

- checkpoint oracle
  is needed
  for:
  stable learned function.

SANITY WORLD SEEDS

20260922090000...

PRIMARY WORLD SEEDS

20260922000000
through:
20260922000079.

Sanity:
NON-EVIDENCE.

No:
teacher architecture,
training set size,
ridge alpha,
damage law,
cycle formula,
query rule,
history window,
lambda,
feedback-noise rate,
or acceptance gate

may change
after:
the first held-out H171 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_FINE_SCALE_LEARNED_MICRO_FUNCTION_MATCHED_TURNOVER

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
