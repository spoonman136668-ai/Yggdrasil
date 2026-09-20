TITLE: DG-1A-AR-H173 — Non-Ratcheting Learned-State Amplitude-Envelope Tail-Containment Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh172-learned-state-trust-region-tail-containment-audit.ice

PURPOSE

H171 established:

fine-scale learned micro-functions
can survive:
approximately one body-equivalent
of:
local learned-state turnover

at:
high median task quality
and:
low observation cost.

But:

world-level learned-logit
tail drift remained.

H172 tested:

a cycle-relative
trust region

centered on:
the current developmental
repair prior.

H172 failed:

11 / 80
TRUST2 worlds
finished with:
negative learned-output fidelity,

including:
3
below:
-10.

The failure mechanism was:

RATCHETING.

Many catastrophic worlds
never violated:
one cycle's
delta bound.

A sequence of:
individually admissible
local updates

moved:
the learned-state magnitude
far away
over:
many repair cycles.

H173 asks:

CAN
A TARGET-BLIND
NON-RATCHETING
ABSOLUTE
LEARNED-STATE
AMPLITUDE ENVELOPE

contain:
the world-level logit tail

without:

- checkpoint restoration;
- extra functional observations;
- task-accuracy loss;
- frozen-state behavior?

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
H171/H172 exactly.

Cell scale:

g=0.25 only.

Tasks:

SMOOTH,
MIXED.

Turnover:

ROAMING,
HOTSPOT.

Feedback eta:

0,
0.10.

Matched lifetime:

292 repair cycles.

Teacher,
training,
student ridge,
damage,
query pool,
H169 HIST-GEOM purchase rule,
lambda,
and:
functional observation budget

remain:
unchanged.

LIFETIME AMPLITUDE CERTIFICATE

At:
the beginning
of:
the lifetime,

before:
the first lesion,

compute:

s0 =
sqrt(
mean(
w_learned^2
)
).

Persist:

ONLY:
this one scalar.

No:
individual coefficient,
region state,
teacher output,
test output,
or:
lost local weight

is retained
for:
repair.

This scalar is:

a TARGET-BLIND
LEARNED-STATE
AMPLITUDE CERTIFICATE.

It is:
not:
a coefficient checkpoint.

It cannot:
restore:
any lost state.

Its purpose is:
to prevent:
the allowable repair scale

from:
growing
as:
mutable state drifts.

LOCAL BOUNDARY SCALE

For:
each repair cycle,

after:
100%
membership return

and:
before:
functional repair,

collect:

currently surviving
live-neighbor cells

touching:
the lesion.

Compute:

rms_boundary =
sqrt(
mean(
w_boundary^2
)
).

Define:

s_local =
clip(
rms_boundary,
0.25 * s0,
2.00 * s0
).

Thus:

local surrounding scale
may:
adapt

but:

cannot:
inflate
the repair envelope

above:
2x
the original
whole-body learned-state RMS.

If:
no live-neighbor boundary exists,

use:

s_local = s0.

No:
functional target,
teacher label,
lost coefficient,
held-out test output,
or:
oracle information

enters:
s0
or:
s_local.

ABSOLUTE AMPLITUDE ENVELOPE

For:
a lesion of:
K cells

and:
candidate repaired coefficient vector:

u,

define:

B_kappa =
kappa
*
s_local
*
sqrt(K).

If:

||u||_2
<=
B_kappa,

accept:
u.

Otherwise:

project:

u_ENV =
B_kappa
*
u
/
||u||_2.

This is:

ABSOLUTE,

not:

delta-relative.

Its center is:
zero amplitude

rather than:
the historically accepted
lesion state.

Therefore:

a sequence of:
small cycle-to-cycle updates

cannot:
increase:
lesion-state norm
without bound.

The same:

s0,
s_local,
B_kappa

remain:
fixed

through:
all functional solves
inside:
one repair cycle.

At:
the next repair cycle,

s_local
is:
recomputed

but:
s0 remains:
the original
lifetime amplitude certificate.

ENVELOPE LEVELS

Primary:

ENV2-HIST-GEOM.

kappa =
2.0.

Robustness comparator:

ENV4-HIST-GEOM.

kappa =
4.0.

No:
kappa
may:
change
after:
sanity.

FUNCTIONAL OBSERVATIONS

Exact:
H171/H169
HIST-GEOM
one-plus-one controller.

Always:

one:
maximum-leverage
binary label.

Buy:
a second label

iff:

rho_geom >=0.98

OR:

cycle >1
AND:
rho_geom <=0.50
AND:
novelty5 >=0.75.

No:
new functional observation
is introduced.

POLICIES

A — H171-UNCONSTRAINED

Exact H171
HIST-GEOM-1PLUS1.

B — H172-TRUST2

Exact H172
cycle-relative
TRUST2 comparator.

C — ENV2-HIST-GEOM

PRIMARY CANDIDATE.

Absolute:
kappa=2
amplitude envelope.

D — ENV4-HIST-GEOM

Robustness comparator.

kappa=4.

E — MICRO2-LEVERAGE

Two-query
information-designed
reference.

F — LOCAL-CHECKPOINT-ORACLE

Exact learned-state ceiling.

PRIMARY FACTORIAL

Task:
2.

Turnover:
2.

eta:
2.

Worlds / cell:
10.

Underlying worlds:

80.

Policies:

6.

Policy lifetimes:

480.

Matched repair cycles:

approximately:
140,160.

PRIMARY METRICS

1.
baseline accuracy;

2.
FINAL accuracy;

3.
accuracy retention;

4.
Brier degradation;

5.
HALF / FINAL
learned-output fidelity;

6.
world fraction:
FINAL learned-output fidelity >=0.95;

7.
world count:
FINAL fidelity <0;

8.
world count:
FINAL fidelity <-10;

9.
minimum FINAL fidelity;

10.
cumulative absolute
test-logit error exposure;

11.
paired exposure ratio
versus:
MICRO2-LEVERAGE;

12.
paired exposure ratio
versus:
H171-UNCONSTRAINED;

13.
paired exposure ratio
versus:
H172-TRUST2;

14.
envelope projection cycles;

15.
envelope projection duty;

16.
median / maximum
norm-to-envelope ratio;

17.
s_local / s0 distribution;

18.
functional observation count;

19.
HOTSPOT repeat load;

20.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H173 supports:
NON-RATCHETING
LEARNED-STATE
AMPLITUDE CONTAINMENT

if:

1.
Baseline competence:

median test accuracy
>=0.85

for:
both task classes.

2.
ENV2
median FINAL accuracy

is:
no more than:
0.03 below:
its own baseline

for:
every:
task x regime x eta group.

3.
>=90%
of:
ENV2 worlds

finish:
within:
0.05 accuracy
of:
their own baseline

for:
every group.

4.
ENV2
median Brier degradation

<=0.03

for:
every group.

5.
ENV2
median FINAL
learned-output fidelity

>=0.95

for:
every group.

6.
WORLD-LEVEL TAIL:

>=95%
of:
ALL ENV2 worlds

finish:
FINAL learned-output fidelity
>=0.95.

7.
ZERO:

ENV2 worlds

with:
FINAL learned-output fidelity
<0.

8.
ZERO:

ENV2 worlds

with:
FINAL learned-output fidelity
<-10.

9.
ENV2
paired cumulative exposure
relative to:
MICRO2-LEVERAGE

has:
group median
<=1.35

for:
every group.

10.
ENV2
median cumulative exposure

is:
lower than:
H171-UNCONSTRAINED

in:
at least:
6 / 8 groups.

11.
ENV2
median cumulative exposure

is:
lower than:
H172-TRUST2

in:
at least:
6 / 8 groups.

12.
ENV2
uses:
the same median
functional observation count

as:
H171-UNCONSTRAINED

inside:
each group.

13.
ENV2
median envelope-projection duty

<0.50

for:
every group.

This prevents:
success
by:
effectively freezing
the learned state.

14.
ENV4
must NOT:
produce:
a new:
accuracy,
Brier,
or:
group-median fidelity
failure

that:
ENV2 avoids.

15.
LOCAL-CHECKPOINT-ORACLE
remains:
the exact learned-state ceiling.

STRONG SUPPORT

H173 receives:
STRONG support

if:

all primary gates pass

AND:

100%
of:
ENV2 worlds

finish:

FINAL learned-output fidelity
>=0.95

AND:

pooled ENV2
cumulative exposure

is:
no greater than:
H172-TRUST2.

MIXED / NEGATIVE CONDITIONS

Treat H173 as:
mixed / negative
if:

- absolute amplitude clipping
  removes:
  logit tails
  only by:
  degrading:
  classification accuracy;

- projection duty
  approaches:
  100%;

- ENV2
  and:
  ENV4
  disagree:
  catastrophically;

- clean-feedback
  tail worlds
  still:
  evade:
  the absolute envelope;

- observation cost
  must:
  increase;

- the lifetime
  amplitude certificate
  is:
  insufficient
  because:
  spatially legitimate
  learned coefficients
  require:
  much larger local magnitude.

SANITY WORLD SEEDS

20260922290000...

PRIMARY WORLD SEEDS

20260922200000
through:
20260922200079.

Sanity:
NON-EVIDENCE.

No:
kappa,
lifetime amplitude-certificate definition,
boundary-scale clipping rule,
projection rule,
teacher,
training,
damage law,
query rule,
history window,
lambda,
feedback-noise rate,
lifetime,
or:
acceptance gate

may change
after:
the first held-out H173 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_NON_RATCHETING_LEARNED_STATE_AMPLITUDE_ENVELOPE

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — NON-RATCHETING AMPLITUDE-ENVELOPE HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H173 HELD-OUT PRIMARY EXECUTION.

FINAL H173 SANDBOX HARNESS

File:

h173_amplitude_envelope_v1.py

SHA-256:

f4d599f7bd8e5ec2dfcc311bdd529214b7d27d73e4b629fe3cc32672b051c905.

PARENT MECHANICS

Reuse:

H171
learned matched-turnover substrate,

H169
HIST-GEOM one-plus-one
functional observation controller,

and:
H172
comparison mechanics.

No:
teacher,
training,
damage,
query,
history,
lambda,
noise,
or:
lifetime
change.

LIFETIME AMPLITUDE CERTIFICATE

At:
pre-turnover initialization,

compute:

s0 =
RMS
of:
the original learned
student coefficient vector.

Persist:

one scalar only.

No:
coefficient checkpoint
is retained.

LOCAL SCALE

At:
100%
membership return
each cycle,

rms_boundary =
RMS
of:
surviving cells
touching:
the lesion.

s_local =
clip(
rms_boundary,
0.25*s0,
2.0*s0
).

If:
no boundary exists,

s_local=s0.

ABSOLUTE ENVELOPE

For:
K lesion cells,

ENV2:

bound =
2.0
*
s_local
*
sqrt(K).

ENV4:

bound =
4.0
*
s_local
*
sqrt(K).

After:
every local ridge solve,

if:
||u||_2
exceeds:
the bound,

project radially
toward:
zero amplitude.

The envelope:

is NOT centered
on:
the current lesion prior

and:
cannot expand beyond:
the frozen
s0-based scale cap.

H172-TRUST2 COMPARATOR

Exact:
cycle-relative
delta projection

is retained
as:
a comparator.

POLICIES

H171_UNCONSTRAINED.

H172_TRUST2.

ENV2_HIST_GEOM.

ENV4_HIST_GEOM.

MICRO2_LEVERAGE.

LOCAL_CHECKPOINT_ORACLE.

SANITY

Disjoint family:

20260922290000...

6 condition-world lifetimes.

6 policies.

36 policy lifetimes.

Sanity-output SHA-256:

b529dbaed3134e77fd6e45edcff11451f2443a7f1f9d7011e03c8b161f11393b.

Mechanical checks:

- exactly six policies / seed;
- exact six sanity seeds;
- oracle:
  final learned-output fidelity
  exactly 1.0;
- ENV2 / ENV4
  use:
  identical observation counts
  to:
  H171_UNCONSTRAINED;
- projection changes:
  repaired lesion coefficients only;
- no:
  teacher output,
  lost coefficient,
  held-out test output,
  or:
  target label

enters:
the amplitude certificate
or:
envelope.

NON-EVIDENCE SIGNAL

ENV2:

minimum sanity
FINAL learned-output fidelity:

approximately:
0.9482.

No:
negative-fidelity
sanity world.

Median projection duty:

approximately:
5.8%.

Maximum:

approximately:
11.3%.

Median maximum
candidate-norm /
envelope ratio:

approximately:
1.16.

ENV4:

mostly inactive

with:
median projection duty:
0%

and:
maximum:
approximately 0.68%.

Thus:

ENV2
is active
without:
approaching:
frozen-state behavior.

One:
sanity world

falls:
slightly below:
0.95
FINAL fidelity.

This is:
NON-EVIDENCE.

No:

- kappa;
- amplitude-certificate rule;
- boundary-scale cap;
- projection rule;
- teacher;
- training;
- damage law;
- query rule;
- history window;
- lambda;
- feedback-noise rate;
- lifetime;
- sample size;
- acceptance gate

was changed.

PRIMARY FAMILY

20260922200000..20260922200079.

80 held-out worlds.

6 policies.

480 policy lifetimes.

Approximately:

140,160
policy repair cycles.

H173 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H173 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
