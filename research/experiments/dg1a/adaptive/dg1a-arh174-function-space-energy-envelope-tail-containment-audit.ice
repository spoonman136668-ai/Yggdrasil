TITLE: DG-1A-AR-H174 — Target-Blind Function-Space Energy-Envelope Tail-Containment Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh173-non-ratcheting-learned-state-amplitude-envelope-audit.ice

PURPOSE

H171:
learned fine-scale micro-functions
survived:
matched turnover
at:
high median task quality.

H172:
cycle-relative
coefficient-space trust regions
failed:
world-level logit-tail containment.

H173:
non-ratcheting
absolute coefficient-norm envelopes
also failed.

H173 mechanism result:

catastrophic learned-output drift
can occur

while:

the repaired coefficient vector
remains:
inside:
a reasonable Euclidean norm bound.

Therefore:

the residual failure
is:
FUNCTION-SPACE
GAIN / DIRECTION,

not:
raw coefficient magnitude.

H174 asks:

CAN
A TARGET-BLIND
FUNCTION-SPACE
ENERGY ENVELOPE

identify:
and:
contain

high-gain
local learned-state directions

without:

- labels;
- held-out test outputs;
- lost coefficients;
- checkpoint restoration;
- extra functional observations;
- task-accuracy loss?

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
H171 / H173
exactly.

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

LIFETIME COEFFICIENT-SCALE CERTIFICATE

At:
pre-turnover initialization,

compute:

s0 =
sqrt(
mean(
w_learned^2
)
).

Persist:

one scalar only.

No:
individual learned coefficient
is retained
for:
repair.

UNLABELED FUNCTION-SPACE PROBES

At:
pre-turnover initialization,

generate:

128
deterministic
unlabeled
unit-disk probe points.

Domain:

world seed
|
"H174_UNLABELED_PROBES".

These probes are:

- independent of:
  teacher labels;
- independent of:
  training targets;
- independent of:
  validation targets;
- independent of:
  held-out test queries;
- fixed:
  for:
  the complete lifetime.

No:
target value
is ever observed
at:
these probes.

They supply:

READOUT GEOMETRY ONLY.

FUNCTION-SPACE ENERGY

For:
one repair cycle
with:
K lesion cells,

let:

P =
Phi(
unlabeled probes,
lesion cells
).

Define:

G =
P^T P
/
128.

For:
candidate lesion coefficient vector:

u,

define:

E(u)
=
u^T
G
u.

Define:

E_scale
=
s0^2
*
trace(G).

If:

trace(G)
<=1e-15,

the envelope
is:
inactive
for:
that cycle.

Otherwise:

normalized function-space energy:

z(u)
=
sqrt(
E(u)
/
E_scale
).

Interpretation:

z approximately 1

is:
the function-space energy
expected
from:
coefficients
with:
RMS scale
approximately s0

under:
the actual lesion
readout geometry.

FUNCTION-SPACE ENVELOPE

Primary:

FENV2-HIST-GEOM.

gamma =
2.0.

Robustness:

FENV4-HIST-GEOM.

gamma =
4.0.

After:
every local ridge solve,

if:

z(u)
<= gamma,

accept:
u.

Else:

project radially:

u_F =
u
*
gamma
/
z(u).

Because:

E(cu)
=
c^2 E(u),

this projection places:
the repaired lesion state
exactly on:
the target-blind
function-energy boundary.

The same:

G,
E_scale,
gamma

remain:
fixed

for:
all local solves
inside:
one repair cycle.

At:
the next repair cycle,

G
changes only because:
lesion geometry changes.

s0:

remains:
lifetime-frozen.

Therefore:

the allowed function-space scale
cannot:
ratchet upward
with:
historically drifted coefficients.

FUNCTIONAL OBSERVATIONS

Exact:
H171/H169
HIST-GEOM
one-plus-one controller.

Always:
one maximum-leverage
binary label.

Second label iff:

rho_geom >=0.98

OR:

cycle>1
AND:
rho_geom<=0.50
AND:
novelty5>=0.75.

No:
extra labels.

POLICIES

A — H171-UNCONSTRAINED

Exact:
H171
HIST-GEOM.

B — H173-ENV2

Exact:
H173
coefficient-space
absolute-envelope comparator.

C — FENV2-HIST-GEOM

PRIMARY CANDIDATE.

gamma=2.

D — FENV4-HIST-GEOM

Robustness comparator.

gamma=4.

E — MICRO2-LEVERAGE

Two-label
information-designed reference.

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
FINAL fidelity >=0.95;

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
H173-ENV2;

14.
function-envelope
projection cycles;

15.
projection duty;

16.
median / maximum
z(u) / gamma
pre-projection ratio;

17.
trace(G);

18.
functional observation count;

19.
HOTSPOT repeat load;

20.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H174 supports:
TARGET-BLIND
FUNCTION-SPACE
TAIL CONTAINMENT

if:

1.
Baseline competence:

median test accuracy
>=0.85

for:
both tasks.

2.
FENV2
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
FENV2 worlds

finish:
within:
0.05 accuracy
of:
baseline

for:
every group.

4.
FENV2
median Brier degradation

<=0.03

for:
every group.

5.
FENV2
median FINAL
learned-output fidelity

>=0.95

for:
every group.

6.
WORLD-LEVEL TAIL:

>=95%
of:
all FENV2 worlds

finish:
FINAL learned-output fidelity
>=0.95.

7.
ZERO:

FENV2 worlds
with:
FINAL fidelity <0.

8.
ZERO:

FENV2 worlds
with:
FINAL fidelity <-10.

9.
FENV2
paired cumulative exposure
relative to:
MICRO2-LEVERAGE

has:
group median
<=1.35

for:
every group.

10.
FENV2
median cumulative exposure

is:
lower than:
H171-UNCONSTRAINED

in:
at least:
6 / 8 groups.

11.
FENV2
median cumulative exposure

is:
lower than:
H173-ENV2

in:
at least:
6 / 8 groups.

12.
FENV2
uses:
the same median
functional observation count

as:
H171-UNCONSTRAINED

inside:
each group.

13.
FENV2
median projection duty

<0.50

for:
every group.

14.
FENV4
must NOT:
produce:
a new:
accuracy,
Brier,
or:
group-median fidelity
failure

that:
FENV2 avoids.

15.
LOCAL-CHECKPOINT-ORACLE
remains:
the exact learned-state ceiling.

STRONG SUPPORT

H174 receives:
STRONG support

if:

all primary gates pass

AND:

100%
of:
FENV2 worlds

finish:
FINAL fidelity >=0.95

AND:

pooled FENV2
cumulative exposure

is:
no greater than:
H173-ENV2.

MIXED / NEGATIVE CONDITIONS

Treat H174 as:
mixed / negative
if:

- function-space clipping
  removes:
  tail drift
  only by:
  harming:
  task accuracy;

- projection duty
  approaches:
  100%;

- unlabeled probe geometry
  fails:
  to detect:
  high-gain directions;

- FENV2 / FENV4
  disagree:
  catastrophically;

- observation cost
  must increase;

- tail worlds
  remain:
  negative
  despite:
  low function-space energy.

SANITY WORLD SEEDS

20260922390000...

PRIMARY WORLD SEEDS

20260922300000
through:
20260922300079.

Sanity:
NON-EVIDENCE.

No:
probe count,
probe generator,
gamma,
energy normalization,
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
the first held-out H174 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_TARGET_BLIND_FUNCTION_SPACE_ENERGY_ENVELOPE

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — FUNCTION-SPACE ENERGY-ENVELOPE HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H174 HELD-OUT PRIMARY EXECUTION.

FINAL H174 SANDBOX HARNESS

File:

h174_function_energy_v1.py

SHA-256:

6c08a6fb98d1b5a3e8ea3341196304883bc64416726fcca0f23ec3665072a554.

PARENT MECHANICS

Reuse:
H171 learned matched-turnover substrate,
H169 HIST-GEOM one-plus-one controller,
and:
H173 comparator mechanics.

No:
teacher,
training,
damage,
query,
history,
lambda,
noise,
or:
lifetime change.

UNLABELED PROBES

128 deterministic
unit-disk points

from domain:

world seed
|
"H174_UNLABELED_PROBES".

No:
target,
teacher,
training,
validation,
or:
held-out test
value

is read
at:
these probes.

FUNCTION-SPACE ENERGY

For:
one lesion,

P =
Phi(
unlabeled probes,
lesion cells
).

G =
P^T P
/
128.

Candidate:
u.

E =
u^T G u.

Lifetime coefficient-scale certificate:

s0 =
RMS
of:
the original learned
student coefficient vector.

E_scale =
s0^2
*
trace(G).

z =
sqrt(
E / E_scale
).

If:
trace(G)<=1e-15,

projection:
inactive.

Otherwise:

FENV2:

gamma=2.

FENV4:

gamma=4.

When:
z>gamma,

project radially:

u <- u * gamma / z.

No:
functional target
enters:
z.

POLICIES

H171_UNCONSTRAINED.

H173_ENV2.

FENV2_HIST_GEOM.

FENV4_HIST_GEOM.

MICRO2_LEVERAGE.

LOCAL_CHECKPOINT_ORACLE.

SANITY

Disjoint family:

20260922390000...

6 condition-worlds.

6 policies.

36 policy lifetimes.

Sanity-output SHA-256:

0baee1dc5b049c5725d330ef91c79296e6f6c7b86b385aa2b1b0d0ffca98dd77.

Mechanical checks:

- exactly six policies / seed;
- exact six sanity seeds;
- oracle fidelity:
  exactly 1.0;
- FENV2 / FENV4:
  identical functional-observation counts
  to:
  H171_UNCONSTRAINED;
- function-space projection
  changes:
  lesion coefficients only;
- no:
  label,
  teacher output,
  lost coefficient,
  or:
  held-out test output

enters:
the envelope.

NON-EVIDENCE SIGNAL

FENV2:

minimum sanity
FINAL learned-output fidelity:

approximately:
0.866.

Median projection duty:

approximately:
97.3%.

Maximum:

approximately:
99.0%.

Minimum accuracy delta:

approximately:
-0.0332.

Thus:

gamma=2
appears:
highly restrictive
in:
sanity.

FENV4:

minimum sanity
FINAL learned-output fidelity:

approximately:
0.944.

Median projection duty:

approximately:
47.8%.

Maximum:

approximately:
71.6%.

This sanity signal
suggests:
a possible:
overconstraint failure.

It is:
NON-EVIDENCE.

No:

- gamma;
- probe count;
- probe generator;
- normalization;
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

20260922300000..20260922300079.

80 held-out worlds.

6 policies.

480 policy lifetimes.

Approximately:

140,160
policy repair cycles.

H174 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H174 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
