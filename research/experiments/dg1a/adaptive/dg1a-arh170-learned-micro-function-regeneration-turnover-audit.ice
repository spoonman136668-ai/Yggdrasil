TITLE: DG-1A-AR-H170 — Learned Micro-Function Regeneration / Turnover Transfer Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh169-repair-history-aware-one-plus-one-micro-anchor-audit.ice

PURPOSE

H150-H169 established a synthetic regenerative-control stack for:
small local cognitive lesions,
persistent mutable state,
bounded functional supervision,
and long-horizon turnover.

Until H169,
the target specialization field itself was analytically generated.

H170 changes that assumption.

Question:

DO THE ACCEPTED REGENERATIVE CONTROL LAWS TRANSFER TO
FUNCTIONAL SPECIALIZATION THAT WAS ACTUALLY LEARNED FROM DATA?

H170 trains the cellular readout on labeled examples,
then erases local learned coefficients,
regenerates them without checkpoint restoration,
and measures whether task competence survives repeated turnover.

BOUNDARY

Synthetic computational research only.

No production model repair.
No biological claim.
No STAB-18-R1 execution.
No canonical scientific execution.
No runtime activation.

BODY / CELLULAR REPRESENTATION

Normalized unit-disk body.

Cell scales:

g = 1.00, 0.25.

R(g) = round(8/g).

Expected body sizes:

g=1.00:
N approximately 197.

g=.25:
N approximately 3209.

Cell feature:

Gaussian radial basis function
centered on each cell.

sigma = 0.22
in normalized macro coordinates.

LEARNED TASK

Binary nonlinear classification.

Each world receives one immutable teacher:

teacher hidden width = 12.

Teacher input:
x,y coordinates plus radial terms:
[x, y, x*y, x^2-y^2, r].

Teacher:

h = tanh(W1 z + b1)

logit_teacher =
w2^T h + b2.

Teacher parameters:
deterministic from world seed.

Two task-complexity classes:

SMOOTH:

teacher weight scale 0.75.

MIXED:

teacher weight scale 1.25
plus:
a deterministic higher-frequency term:

0.45 * sin(5x + phase1) * cos(5y + phase2).

Binary label:

y = +1
iff:
logit_teacher >= 0,
else:
-1.

TRAIN / TEST DATA

Per world:

training:
512 points uniform in the unit disk.

validation:
256 points.

test:
512 points.

All three sets:
fixed for the lifetime.

TRAINED CELLULAR READOUT

Feature matrix:
Phi_train.

Learn one distributed scalar coefficient
per computational cell.

Ridge objective:

min_w
||Phi_train w - y_train||^2
+
alpha ||w||^2.

alpha = 0.01.

Use:
dual ridge solve
for computational efficiency.

No analytic coefficient field
is injected.

The resulting:
w_learned

is:
the organism's acquired functional specialization.

BASELINE COMPETENCE

Before any lesion:

evaluate on:
test set.

Metrics:

classification accuracy;
Brier score;
signed-margin MSE.

No primary world is discarded
for scientific performance.

Mechanical failure only
may invalidate a world.

Primary acceptance includes
a baseline competence gate.

PERSISTENT MUTABLE STATE

Each repair policy begins from:
the same learned w_learned.

After each repair cycle:

the repaired coefficient vector
becomes the starting state
for the next cycle.

No global reset.

No checkpoint restore
except:
LOCAL-CHECKPOINT-ORACLE.

LOCAL DAMAGE

f0 = 0.05.
beta = 2.

damage fraction:

0.05 * g^2.

Expected:
approximately 10..11 lost cells
at both scales.

Lost cells lose:
their current learned coefficient.

The lost value is unavailable
to non-oracle repair.

TURNOVER REGIMES

ROAMING:

new compact lesion center
each cycle
inside normalized radius 0.65.

HOTSPOT:

one persistent macro hotspot
with Gaussian jitter sd=0.08.

RECENT HISTORY

For H169 controller:

recent footprint =
union of previous 5 lesion sets.

novelty5 =
1 -
fraction of current lesion
already inside recent footprint.

REPAIR CYCLES

40 repair cycles / lifetime.

This first learned-function transfer test
uses fixed operational event count.

A matched-body-equivalent learned-task stress
is deferred until H170 closes.

MEMBERSHIP REGENERATION

Reuse accepted H161/H169 mechanics.

Moore-frontier local regeneration.

p=0.50.

New cells initialize
from live-neighbor coefficient context.

Context refinement:
0.50 current + 0.50 live-neighbor mean.

Surviving original coefficients:
fixed inside each repair cycle.

FUNCTIONAL MICRO-ANCHOR POOL

Per repair cycle:

64 local candidate task queries.

Query coordinates:
same lesion-local generator
used H165-H169.

Observed target:

teacher binary label
at that query.

Feedback noise:

eta = 0, 0.10.

For noisy feedback:

with probability eta,
flip the observed binary label.

Noise potential:
deterministic from:
world seed,
cycle,
query index,
eta.

No clean label is exposed
when a flip occurs.

QUERY PURCHASE

Use accepted H169 target-blind controller.

q1:
maximum leverage under:
A0 = lambda I.

q2:
maximum remaining leverage
after q1 information update.

rho_geom = L2/L1.

Always acquire q1.

Acquire q2 iff:

rho_geom >=0.98

OR:

cycle>1
AND
rho_geom<=0.50
AND
novelty5>=0.75.

No functional target
enters the purchase decision.

LOCAL REPAIR SOLVE

After 100% membership return:

jointly solve
only the restored lesion coefficients.

Prior:
current context-repaired lesion state.

lambda = 0.01.

Training data:
the one or two acquired local binary labels.

Surviving coefficients fixed.

Selected observations remain
active constraints
through:
12 post-membership maturation steps.

POLICIES

A — CONTEXT-ONLY

Developmental regeneration only.
Zero task labels.

B — MICRO2-LEVERAGE

Two leverage-selected labels
every repair cycle.

Learned-task exposure-safe reference.

C — HIST-GEOM-1PLUS1

Primary candidate.

Accepted H169 purchase controller.

D — LOCAL-CHECKPOINT-ORACLE

Restores the original learned coefficient
w_learned
when a damaged cell returns.

Evaluation ceiling for state preservation.

COMMON-WORLD DISCIPLINE

All policies in one world share:

teacher;
train/validation/test data;
trained starting weights;
lesion sequence;
membership potentials;
query coordinates;
label-flip potentials.

Policy state may diverge
only through repair history.

PRIMARY FACTORIAL

Task complexity:
SMOOTH, MIXED.

Cell scale:
1.00, 0.25.

Turnover:
ROAMING, HOTSPOT.

Feedback eta:
0, 0.10.

Worlds / cell:
10.

Underlying worlds:

2 x 2 x 2 x 2 x 10
=
160.

Policies:
4.

Policy lifetimes:
640.

Repair cycles:
40.

Total policy repair cycles:
25,600.

PRIMARY METRICS

1. pre-lesion test accuracy;
2. cycle-40 test accuracy;
3. minimum post-cycle test accuracy;
4. accuracy retention relative to baseline;
5. Brier score;
6. Brier degradation relative to baseline;
7. signed-margin MSE;
8. learned-output fidelity:

1 -
MSE(logit_current, logit_baseline)
/
Var(logit_baseline);

9. HALF and FINAL learned-output fidelity;
10. late-life SelfRecovery on baseline logits;
11. cumulative absolute test-logit error exposure;
12. query count / cycle;
13. second-query duty;
14. ROAMING / HOTSPOT interaction;
15. coarse / fine interaction;
16. clean / noisy-label interaction;
17. oracle gap.

BASELINE COMPETENCE GATE

For each:
task-complexity x scale group,

median pre-lesion test accuracy
must be:
>=0.85.

If not:

H170 cannot interpret repair quality
because the learned substrate itself
is too weak.

PRIMARY ACCEPTANCE SHAPE

H170 supports:
LEARNED MICRO-FUNCTION REGENERATION TRANSFER

if:

1.
Baseline competence gate passes
for all task-complexity x scale groups.

2.
HIST-GEOM-1PLUS1:

median FINAL test accuracy

is no more than:
0.03 absolute

below:
its own pre-lesion baseline

for every:
task x scale x regime x eta group.

3.
>=90% of HIST-GEOM worlds

finish:
within:
0.05 accuracy
of:
their own pre-lesion baseline

for every group.

4.
HIST-GEOM
median FINAL learned-output fidelity

>=0.95
for every group.

5.
HIST-GEOM
median HALF-to-FINAL
learned-output fidelity loss

<=0.02
for every group.

6.
HIST-GEOM
median Brier degradation

<=0.03
absolute

for every group.

7.
HIST-GEOM
late-life SelfRecovery
median

>=0.90
for every group.

8.
HIST-GEOM
cumulative absolute test-logit error exposure

is:
<=1.35x
MICRO2-LEVERAGE

for every group.

9.
HIST-GEOM
uses fewer observations than:
MICRO2-LEVERAGE

in:
every group.

10.
At g=.25,
HIST-GEOM median FINAL accuracy

is:
no more than:
0.03 below:
g=1.00

for corresponding:
task x regime x eta groups.

11.
CONTEXT-ONLY does not define success.

If CONTEXT-ONLY
matches the learned-task gates,
report it as:
a neutral / stronger developmental result.

12.
LOCAL-CHECKPOINT-ORACLE
remains:
the state-preservation ceiling.

STRONG SUPPORT

H170 receives STRONG support if:

all primary gates pass

and:

HIST-GEOM pooled observation reduction
versus:
MICRO2-LEVERAGE

>=25%

while:

pooled exposure
is within:
15%
of:
MICRO2-LEVERAGE.

MIXED / NEGATIVE CONDITIONS

Treat H170 as mixed / negative if:

- learned classification competence
  degrades even though synthetic logit fidelity
  previously looked stable;

- local label feedback is too weak
  to reconstruct learned specialization;

- label noise breaks the one-plus-one controller;

- fine-scale learned tasks
  require substantially more supervision;

- repeated turnover preserves logits
  but degrades task accuracy or calibration;

- checkpoint oracle is needed
  to prevent cumulative semantic loss.

SANITY WORLD SEEDS

20260921990000...

PRIMARY WORLD SEEDS

20260921900000
through:
20260921900159.

Sanity:
NON-EVIDENCE.

No:
teacher architecture,
training set size,
ridge alpha,
damage law,
query rule,
history window,
lambda,
feedback-noise rate,
lifetime,
or acceptance gate

may change
after:
the first held-out H170 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_LEARNED_MICRO_FUNCTION_REGENERATION_TRANSFER

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — LEARNED MICRO-FUNCTION HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H170 HELD-OUT PRIMARY EXECUTION.

FINAL H170 SANDBOX HARNESS

File:

h170_learned_micro_v2.py

SHA-256:

a3dbe6da369f3e0784e975c32f17ed9e1ad3b3043b0c3362cb00fc01c8f05b1a.

LEARNED SUBSTRATE

Binary nonlinear teacher.

Teacher hidden width:
12.

Student:
distributed Gaussian-RBF cellular readout.

Training:
512 labeled examples.

Validation:
256.

Test:
512.

Ridge alpha:
0.01.

Cell scales:

g=1.00
and:
g=0.25.

No analytic specialization coefficient field
is injected.

All mutable cell coefficients
come from:
the data-trained ridge readout.

FUNCTIONAL FEEDBACK

Local micro-anchor target:

teacher binary label.

Noise:

eta=0
or:
0.10
deterministic label-flip potential.

No clean label
is exposed
when:
a flip occurs.

QUERY PURCHASE

Exact accepted H169
target-blind controller:

always:
q1 maximum leverage.

buy q2 iff:

rho_geom >=0.98

OR:

cycle>1
AND:
rho_geom<=0.50
AND:
novelty5>=0.75.

LOCAL REPAIR

After:
100%
membership return:

jointly solve:
restored lesion coefficients only.

lambda:
0.01.

Prior:
current context-repaired lesion state.

Surviving learned coefficients:
fixed.

Selected observations:
remain active
through:
12 post-membership maturation steps.

PERSISTENT STATE

Repaired learned coefficients
carry directly into:
the next repair cycle.

No:
global reset.

No:
lost learned coefficient
available
to:
non-oracle repair.

ORACLE CORRECTION

Initial sanity exposed:
a mechanical oracle-path defect
in:
h170_learned_micro_v1.py.

The oracle:
restored exact learned coefficients

but:
was then context-refined
during the post-membership horizon.

That violated:
the preregistered oracle ceiling.

Disposition:

h170_learned_micro_v1.py
sanity output:
NON-EVIDENCE.

v2 correction:

LOCAL-CHECKPOINT-ORACLE
restores:
the exact original learned coefficient

on:
each membership-return batch

and:

does NOT:
context-refine
the restored lesion afterward.

No:
non-oracle policy,
query rule,
teacher,
training rule,
noise,
threshold,
or:
acceptance gate

changed.

SANITY

Disjoint family:

20260921990000...

6 representative learned-task worlds.

4 policies.

24 policy lifetimes.

Mechanical checks:

- exactly four policies / seed;
- exact six sanity seeds;
- learned baseline test accuracy:
  approximately 0.969..1.000;
- median baseline competence
  by task x scale:
  all >0.97;
- LOCAL-CHECKPOINT-ORACLE
  final learned-output fidelity:
  exactly 1.0;
- no:
  lost learned coefficient,
  held-out test label,
  or:
  latent task class
  enters:
  non-oracle repair.

Accepted sanity matrix SHA-256:

0858bac34156350512ba05e87bbf19368f231f95b9bd25c83d997272ece612e3.

NON-EVIDENCE SIGNAL

Fine:
g=0.25

HIST-GEOM
generally retains:
learned classification accuracy

within:
approximately 0..0.4 percentage points
of:
baseline
in:
the representative MIXED worlds.

Coarse:
g=1.00

is:
materially harder.

Representative learned-task
HIST-GEOM accuracy losses:

SMOOTH ROAMING clean:

approximately:
-3.1 percentage points.

MIXED ROAMING eta=.10:

approximately:
-5.3 points.

MIXED HOTSPOT eta=.10:

approximately:
-5.1 points.

Representative coarse
learned-output fidelity:

approximately:
0.836..0.930.

This is:
a live held-out hypothesis.

No:

- teacher architecture;
- training size;
- ridge alpha;
- damage law;
- query rule;
- history window;
- lambda;
- feedback-noise rate;
- lifetime;
- sample size;
- acceptance gate

is changed.

PRIMARY FAMILY

20260921900000..20260921900159.

160 held-out learned-task worlds.

4 policies.

640 policy lifetimes.

40 repair cycles / lifetime.

H170 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H170 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — LEARNED MICRO-FUNCTION REGENERATION / TURNOVER TRANSFER

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-NEGATIVE GLOBAL TRANSFER / POSITIVE FINE-SCALE LEARNED TRANSFER.

FINAL H170 HARNESS SHA-256

a3dbe6da369f3e0784e975c32f17ed9e1ad3b3043b0c3362cb00fc01c8f05b1a.

ACCEPTED PRIMARY MATRIX SHA-256

03fc5ae5e192e63c2d585e9e8997ce7e41af63d571a2a08ca66fafd520910d55.

ACCEPTED PRIMARY FAMILY

20260921900000..20260921900159.

PRIMARY MATRIX

160 held-out learned-task worlds.

4 policies.

640 policy lifetimes.

40 repair cycles / lifetime.

Validation:

- exactly 160 unique held-out seeds;
- exact accepted seed interval;
- exactly four policy rows / seed;
- zero duplicate seed x policy rows;
- no missing accepted seeds;
- no post-primary teacher / repair / query tuning.

BASELINE LEARNED COMPETENCE

Median pre-lesion held-out accuracy:

SMOOTH,
g=1.00:
approximately 0.9873.

SMOOTH,
g=.25:
approximately 0.9883.

MIXED,
g=1.00:
approximately 0.9844.

MIXED,
g=.25:
approximately 0.9824.

Frozen competence floor:
>=0.85.

PASS:
all task x scale groups.

Thus:

the cellular substrate genuinely learned:
nontrivial held-out classification.

PRIMARY CANDIDATE

HIST-GEOM-1PLUS1.

FINE-SCALE LEARNED TRANSFER

g=.25.

Across:
SMOOTH / MIXED,
ROAMING / HOTSPOT,
eta=0 / .10,

median FINAL accuracy
remains:
within approximately:
0..0.4 percentage points
of:
the pre-lesion baseline
in nearly all groups.

Representative MIXED:

ROAMING,
eta=0:

baseline:
approximately 0.9834.

FINAL:
0.9824.

eta=.10:

0.9805
->
0.9795.

HOTSPOT,
eta=0:

0.9922
->
0.9902.

eta=.10:

0.9775
->
0.9785.

Fine-scale learned-output fidelity:

approximately:
0.979
to:
0.995.

Brier degradation:

near zero,
often slightly improved.

World-level accuracy-retention:

100%
within:
0.05
of baseline

for:
all fine-scale groups.

Thus:

the learned micro-function
transfer hypothesis
is:
strongly supported
at:
small-cell scale.

COARSE LEARNED TRANSFER FAILURE

g=1.00.

The same controller
does NOT:
transfer reliably.

MIXED ROAMING:

eta=0:

baseline:
approximately 0.9873.

FINAL:
0.9609.

median learned-output fidelity:
approximately 0.9167.

eta=.10:

baseline:
approximately 0.9824.

FINAL:
approximately 0.8730.

median accuracy loss:
approximately 0.116.

learned-output fidelity:
approximately 0.558.

HALF-to-FINAL fidelity loss:
approximately 0.136.

Brier degradation:
approximately 0.0439.

SMOOTH ROAMING,
eta=.10:

baseline:
approximately 0.9893.

FINAL:
approximately 0.9268.

learned-output fidelity:
approximately 0.760.

Thus:

coarse learned specialization
is:
materially more fragile

than:
the prior synthetic coefficient-field model.

GLOBAL GATE REVIEW

PASS:

1.
Baseline competence.

6.
Brier degradation
for:
most groups.

9.
HIST-GEOM
uses fewer observations
than:
MICRO2-LEVERAGE
in:
every group.

10.
Fine-scale FINAL accuracy
is:
not below:
coarse accuracy
by:
>0.03
in:
corresponding groups.

12.
LOCAL-CHECKPOINT-ORACLE
remains:
exact learned-state ceiling.

FAIL / MIXED:

2.
FINAL accuracy
within:
0.03
of baseline
for:
every group.

Fails:
coarse noisy ROAMING
for:
both task classes.

3.
>=90%
of worlds
within:
0.05
of baseline
for:
every group.

Fails:
multiple coarse ROAMING groups.

4.
FINAL learned-output fidelity
>=0.95
for:
every group.

Fails:
five coarse groups.

5.
HALF-to-FINAL
learned-output fidelity loss
<=0.02
for:
every group.

Fails:
coarse noisy ROAMING
for:
both task classes.

6.
Brier degradation
<=0.03
for:
every group.

Fails:
MIXED coarse noisy ROAMING.

7.
Late-life SelfRecovery
>=0.90
for:
every group.

Fails:
multiple noisy-label groups
including:
some fine-scale conditions.

8.
Cumulative logit-error exposure
<=1.35x
MICRO2-LEVERAGE
for:
every group.

Fails:
MIXED
coarse HOTSPOT
eta=.10
at:
approximately 1.49x.

STRONG SUPPORT:

FAIL.

IMPORTANT SELF-RECOVERY NOTE

Fine-scale:
FINAL task accuracy
and:
learned-output fidelity

remain:
strong

even in:
some noisy-label groups
where:
the relative SelfRecovery metric
falls below:
0.90.

Because:

small lesions
can create:
very small
pre/post lesion denominators,

the relative SelfRecovery ratio
is:
numerically sensitive

in:
this learned-task regime.

The gate remains:
FAILED
as frozen.

Future learned-task work
should report:

both:

- relative SelfRecovery;

and:

- absolute task-error exposure /
  accuracy restoration.

No gate is:
retroactively changed.

EXPOSURE VERSUS MICRO2

HIST-GEOM
is:
often LOWER exposure
than:
MICRO2-LEVERAGE
at:
fine scale.

Representative ratios:

approximately:
0.70..1.02.

At coarse scale:

most groups remain:
near:
1.05..1.25,

but:

MIXED HOTSPOT
eta=.10:

approximately:
1.49.

Thus:

cheap one-plus-one control
does NOT:
explain:
the coarse learned-transfer failure.

The learned substrate itself
requires:
more local functional information
or:
finer representational granularity.

FINAL INTERPRETATION

H170 is:

MIXED-NEGATIVE
for:

GLOBAL
LEARNED-MICRO-FUNCTION
TRANSFER.

But:

it is:
POSITIVE

for:

FINE-SCALE
LEARNED-MICRO-FUNCTION
TRANSFER.

This is:
a major architectural result.

The prior synthetic program suggested:

SMALLER CELLS
should:
reduce repair blast radius
and:
functional supervision burden.

H170 now shows:

that advantage
becomes:
MORE IMPORTANT,
not less,

when:
the local specialization
was actually learned
from data.

At:
fine granularity:

- learned classification competence survives;
- calibration remains stable;
- learned logits remain near baseline;
- one-plus-one local feedback remains sufficient;
- noisy labels do not cause:
  terminal capability drift.

At:
coarse granularity:

local developmental context
plus sparse labels
cannot reliably reconstruct:
the lost learned specialization,
especially:
under moving damage
and:
label noise.

ARCHITECTURAL CONSEQUENCE

Do NOT:

spend the next phase
trying to rescue:
coarse learned cells

with:
ever-larger repair budgets.

That would:
fight:
the small-cell architecture
the research now supports.

Instead:

stress the:
FINE-SCALE
learned-function regime

under:
matched cumulative turnover.

H170 used:
40 fixed repair events.

At:
g=.25,
that is:
far below:
one full body-equivalent
learned-state turnover.

NEXT:

H171 —
FINE-SCALE
LEARNED-MICRO-FUNCTION
MATCHED-TURNOVER STRESS.

Primary target:

g=.25 only.

Use:
approximately one
body-equivalent
local learned-state turnover

with:
292 repair cycles.

Test:

SMOOTH / MIXED learned tasks;
ROAMING / HOTSPOT;
eta=0 / .10.

Compare:

- CONTEXT-ONLY;
- MICRO2-LEVERAGE;
- HIST-GEOM-1PLUS1;
- LOCAL-CHECKPOINT-ORACLE.

Measure:

- FINAL task accuracy;
- baseline-relative accuracy retention;
- Brier drift;
- learned-output fidelity;
- absolute logit-error exposure;
- long-horizon drift;
- repeated HOTSPOT learned-state replacement;
- observation cost.

If:
fine-scale learned capability
survives:
one body-equivalent turnover,

the next research phase
can move beyond:
synthetic coordinate classification

into:
multi-function /
memory-bearing
learned micro-organs.

H170 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- global retraining;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
