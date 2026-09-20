TITLE: DG-1R-05I — Cross-Bit-Plane Fault-Type Confidence Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE CONFIDENCE-GATING PILOT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / FAULT-TYPE CONFIDENCE
BRANCH: dg1a-ar
PARENT: DG-1R-05H

PURPOSE

DG-1R-05H established:

- the HYPER20 representation contains enough information to localize
  simultaneous logical faults;
- iterative GREEDY_SYNDROME exactly repaired distributed two-region damage;
- iterative decoding outperformed one-pass decoding;
- four correlated integrity faults can still masquerade as a logical fault;
- some minimum-weight explanations are ambiguous, while others confidently
  prefer the wrong logical-plus-check explanation under equal fault cost.

DG-1R-05I asks:

CAN:
FAULT:
EVIDENCE
ACROSS:
THE:
FOUR:
BIT PLANES

PROVIDE:
A:
CONFIDENCE:
SIGNAL

FOR:

WHEN:
A:
LOGICAL:
REGION
SHOULD:
ACTUALLY:
BE:
REPAIRED?

BOUNDARY

Synthetic software-only pilot.

No living tissue.
No wetware.
No biological nanotechnology.
No production modification.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL / NON-EVIDENCE.

DG-1R-05 canonical frozen primary remains:
UNSPENT.

STATE REPRESENTATION

Exact DG-1R-05H HYPER20 representation.

48 logical bits.

80 integrity bits.

128 persistent bits.

20 frozen four-region hyperchecks.

No extra persistent state.

No hidden history.

No task labels.

No counterfactual information visible to decoder.

BASE LOCALIZER

Exact DG-1R-05H GREEDY_SYNDROME inference.

For each bit plane independently:

- compute 20-bit syndrome;
- choose the logical block whose hypothetical bit flip yields the largest
  strictly positive syndrome-weight reduction;
- tie by lowest logical block index;
- never select the same logical block twice inside one bit plane;
- iterate up to 4 logical flips per bit plane;
- stop if no logical flip strictly reduces syndrome weight.

Important:

DG-1R-05I separates:

INFERENCE

from:

APPLICATION.

The greedy engine first produces:

a:
proposed:
12 x 4:
logical-flip matrix

without:
mutating:
persistent:
logical state.

CROSS-PLANE SUPPORT

For logical block b:

PLANE_SUPPORT_b

=
number:
of:
bit planes
k in 0..3

for which:

the:
greedy:
inference

proposes:
a:
logical:
flip
at:
(b,k).

Frozen confidence threshold:

2.

A logical block is:

CROSS-PLANE-CONFIDENT

if:

PLANE_SUPPORT_b
>=2.

METHODS

1.
GREEDY_BASELINE

Exact:
DG-1R-05H:
GREEDY_SYNDROME.

Apply:
every:
greedy-inferred:
logical:
bit flip.

2.
CROSSPLANE2_GATE

Run:
the:
same:
greedy:
inference.

Apply:

only:
proposed:
logical:
bit flips

belonging:
to:
logical:
blocks

with:

PLANE_SUPPORT
>=2.

All:
proposed:
flips
for:
blocks
with:
support:
0
or:
1

are:
ABSTAINED.

3.
CROSSPLANE2_DETECT_ONLY

Run:
same:
inference.

Compute:
same:
support.

Apply:
no:
logical:
repair.

Purpose:

detection-only control.

EPHEMERAL ONLY

The:

12-region:
plane-support:
vector

is:
computed:
combinationally

from:
the:
current:
syndrome.

It:
is:
not:
stored
between:
external:
steps.

Persistent state remains:

128 bits.

DYNAMICS

Exact:
DG-1R-05H.

48 logical bits.

MIXED5:
one CA update per external input.

Input-mapped logical blocks:

1,
4,
7,
10.

Repair:

before:
current:
input overwrite.

Then:

logical CA update.

Then:

all 20 hyperchecks
recomputed.

Pre-damage:

1024 steps.

Post-damage:

32 steps.

WORLD FAMILY

8 worlds.

Seeds:

20260926059000
through:
20260926059007.

No prior DG-1R seed reuse.

DAMAGE FAMILIES

A.
LOCAL_DATA2_D6

Block 5.

Flip logical bit planes:

0,
1.

Purpose:

basic:
two-plane:
logical-region:
damage.

Expected:

plane support for block 5:

2.

B.
DISTRIBUTED_DATA2

Blocks:

2
and:
8.

Flip logical planes:

0,
1
in both.

Purpose:

preserve:
DG-1R-05H:
distributed:
repair.

Expected:

each:
damaged:
block
receives:
cross-plane:
support >=2.

C.
DATA2_PLUS_CHECK2_D6

Block 5:
logical planes:
0,
1.

Plus:

two:
incident:
integrity:
faults

in:
bit plane:
0.

Purpose:

preserve:
mixed:
logical-plus-integrity:
repair.

D.
DATA2_PLUS_CHECK3_D7

Block 2:
logical planes:
0,
1.

Plus:

three:
incident:
integrity:
faults

in:
bit plane:
0.

Purpose:

preserve:
the:
05H:
greedy:
positive
where:
MW_UNIQUE:
was:
ambiguous.

E.
CHECK4_BIT0_D6

No logical damage.

Flip:

bit plane 0

in:
four:
incident:
integrity:
checks

for:
degree-6:
block 5.

Purpose:

the:
05H:
false-repair:
boundary.

Expected:

GREEDY_BASELINE
infers:
one:
logical:
plane
at:
block 5.

Cross-plane support:

1.

CROSSPLANE2_GATE
should:
ABSTAIN.

F.
CHECK4_BIT0_D7

No logical damage.

Flip:

bit plane 0

in:
four:
incident:
integrity:
checks

for:
degree-7:
block 2.

Purpose:

second:
05H:
false-repair:
boundary.

Expected:
cross-plane support:

1.

G.
CHECK4_BITS01_D6

No logical damage.

Use:
the:
same:
four:
degree-6:
integrity:
checks

but:

flip:
both:
bit planes:
0
and:
1

in:
each:
check.

Purpose:

adversarial:
cross-plane:
correlated-integrity:
boundary.

Expected:

the:
same:
healthy:
logical:
region

may:
be:
falsely:
implicated
on:
two:
bit planes.

If:

CROSSPLANE2_GATE
repairs:
healthy:
logical:
state,

record:
the:
boundary.

H.
SINGLE_DATA1_D6

Block 5.

Flip:
only:
logical:
bit plane:
0.

Purpose:

sensitivity:
boundary.

A:
true:
single-bit:
logical:
fault

provides:

cross-plane support:

1.

CROSSPLANE2_GATE

is:
expected
to:
ABSTAIN.

This:
is:
not:
an:
implementation:
failure.

It:
measures:
the:
specificity /
sensitivity:
tradeoff
created:
by:
the:
confidence:
gate.

LESION ASSERTIONS

Harness MUST assert:

- exact logical flip count;
- exact integrity flip count;
- physical uniqueness;
- no logical lesion overlaps current input-mapped logical position.

PRIMARY TELEMETRY

Per scenario:

- inferred logical flips;
- applied logical flips;
- abstained inferred flips;
- false inferred logical flips;
- false applied logical flips;
- per-block plane support;
- max plane support;
- support histogram;
- final syndrome weight.

COUNTERFACTUAL METRICS

At horizons:

1,
4,
8,
16,
32:

- logical divergence;
- physical divergence;
- exact logical match.

Also:

- logical divergence area;
- physical divergence area;
- sustained exact logical recovery;
- logical recovery time.

FALSE APPLIED LOGICAL FLIP

An:
applied:
repair:
bit
is:
FALSE

if:

its:
post-correction:
logical:
value

does NOT:
match:
the:
undamaged:
counterfactual:
logical:
bit

immediately:
before:
current:
input.

Decoder never sees this label.

It is evaluation telemetry only.

FROZEN SIGNALS

CROSSPLANE_FALSE_REPAIR_SUPPRESSION

TRUE
if:

CROSSPLANE2_GATE

on:

CHECK4_BIT0_D6
and
CHECK4_BIT0_D7

has:

false applied logical flips
=
0

AND:

logical divergence area
=
0

while:

GREEDY_BASELINE

has:

false applied logical flips
>
0

on:
at least:
one:
of:
those:
families.

LOGICAL_REPAIR_PRESERVATION

TRUE
if:

CROSSPLANE2_GATE

has:

logical divergence area median
=
0

AND:

sustained exact logical recovery
>=0.90

AND:

false applied logical flip fraction
<=0.01

for:

LOCAL_DATA2_D6.

DISTRIBUTED_DATA2.

DATA2_PLUS_CHECK2_D6.

DATA2_PLUS_CHECK3_D7.

CROSSPLANE_CONFIDENCE_SIGNAL

TRUE
if:

CROSSPLANE_FALSE_REPAIR_SUPPRESSION
=
TRUE

AND:

LOGICAL_REPAIR_PRESERVATION
=
TRUE.

SINGLE-BIT SENSITIVITY COST

Report:

SINGLE_DATA1_D6

for:

GREEDY_BASELINE
versus:
CROSSPLANE2_GATE.

No:
positive:
single-bit:
repair:
criterion
is:
required
for:
the:
cross-plane:
gate.

The:
expected:
tradeoff:

higher:
specificity

at:
the:
cost
of:
single-plane:
logical:
fault:
sensitivity.

CORRELATED CROSS-PLANE BOUNDARY

CHECK4_BITS01_D6

is:
the:
frozen:
adversarial:
boundary.

If:

CROSSPLANE2_GATE

false-repairs
the:
healthy:
logical:
region,

report:

CROSSPLANE_CORRELATED_FAILURE.

No:
post-run:
threshold:
change
is:
allowed.

IMPORTANT

A:
positive:
result

would NOT:
show:

that:
two-plane:
support
is:
a:
universal:
fault:
truth:
criterion.

It would show:

the:
four-bit:
regional:
organization

contains:
a:
useful:
fault-type:
confidence:
signal

that:
was:
ignored
by:
05H's:
independent:
per-plane:
decoder.

A:
failure:
on:
CHECK4_BITS01_D6

would:
bound:
that:
signal:

correlated:
integrity:
damage
across:
multiple:
bit planes

can:
imitate:

multi-bit:
logical:
region:
damage.

That:
would:
justify:

time,
history,
or:
independent:
topological:
evidence

as:
the:
next:
confidence:
axis.

REPRODUCIBILITY

Two complete 8-world sweeps.

Output SHA-256 must match exactly.

NO POST-RUN TUNING

After the first DG-1R-05I scenario:

do not alter:

- hypergraph;
- greedy inference;
- plane support definition;
- threshold 2;
- lesions;
- world family;
- metrics;
- classifications.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
last:
decoder
could:
find:
two:
damaged:
regions
perfectly.

But:

four:
bad:
backup:
channels
could:
sometimes:
trick:
it
into:
repairing:
healthy:
data.

This:
test
asks:
for:
one:
more:
piece
of:
confidence:

"Does:
the:
same:
data:
region
look:
damaged
in:
more:
than:
one:
bit:
plane?"

Our:
data:
damage
usually:
hits:
two:
bits
inside:
the:
same:
region.

The:
bad:
backup:
channels
in:
the:
05H:
failure
only:
lied
on:
one:
bit:
plane.

So:

if:
a:
region
is:
only:
accused
on:
one:
plane,

the:
new:
decoder
will:
refuse:
to:
repair:
it.

If:
the:
same:
region
is:
independently:
accused
on:
two:
planes,

the:
decoder
can:
act.

That:
may:
stop:
the:
false:
repairs
without:
adding:
any:
persistent:
memory.

We:
also:
include:
two:
important:
failure:
tests:

a:
real:
single-bit:
data:
fault

and:

backup:
damage
that:
lies
on:
two:
bit:
planes.

Those:
will:
show:
exactly:
what:
this:
confidence:
rule
can:
and:
cannot:
distinguish.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN LINEAGE NOTE — AUTHORITATIVE DG-1R-05I

DATE:
2026-09-20.

STATUS:
AUTHORITATIVE:
DG-1R-05I:
PREREGISTRATION.

A:
prior:
same-branch:
preregistration

used:
the:
same:
05I:
identifier
for:
a:
local-max:
message-passing:
audit.

That:
prior:
experiment

was:
never:
implemented,
frozen,
or:
executed

and:
is:
explicitly:
DEFERRED.

This:
later:
cross-bit-plane:
confidence:
audit

is:
the:
authoritative:
DG-1R-05I:
experiment.

Frozen:
seed family:

20260926059000..20260926059007.

No:
DG-1R-05I:
world
has:
been:
executed
at:
the:
time:
of:
this:
lineage:
clarification.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05I CROSS-BIT-PLANE CONFIDENCE

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05I:
WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05i_crossplane_confidence_v1.py

Harness commit:

ef6295de65066d0fe022c3a567e54f2e5525bc3d.

Git blob SHA:

00dc7efc861c1289a15266b85cd260a54ec2a178.

Remote source SHA-256:

444ae03bccdf292b3a40a3a2a62ad069d507ac72ea8ba2c6886077483d330778.

Remote source bytes:

12107.

LOCAL PRECHECK

Python syntax:

PASS.

Frozen support threshold:

2:
bit planes
per:
logical region.

Inference:

exact:
DG-1R-05H:
iterative:
greedy:
syndrome:
localization.

Application:

GREEDY_BASELINE:

apply:
all:
inferred:
logical flips.

CROSSPLANE2_GATE:

apply:
only:
inferred:
logical flips
for:
blocks
with:
plane support
>=2.

CROSSPLANE2_DETECT_ONLY:

apply:
none.

No:
DG-1R-05I:
experimental:
world

was:
executed
before:
this:
freeze.

PACKAGING NOTE

Local:
pre-transfer:
source
contained:
one:
final:
newline.

GitHub:
stored:
the:
same:
Python:
source
without:
that:
final:
newline.

No:
experimental:
semantic:
changed.

Execution copy
was:
aligned
to:
the:
authoritative:
remote:
bytes
before:
execution.

FROZEN WORLD FAMILY

20260926059000..20260926059007.

8 worlds.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

DG-1R-05I:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05I NON-EVIDENCE CLOSURE — CROSS-BIT-PLANE FAULT-TYPE CONFIDENCE

DATE:
2026-09-20.

STATUS:
COMPLETE /
STRONG POSITIVE ONE-PLANE FALSE-REPAIR SUPPRESSION /
FULL TWO-PLANE LOGICAL-REPAIR PRESERVATION /
SINGLE-BIT SENSITIVITY COST CONFIRMED /
CROSS-PLANE CORRELATED-INTEGRITY BOUNDARY CONFIRMED /
NON-CANONICAL /
NON-EVIDENCE.

FROZEN HARNESS

Git blob SHA:

00dc7efc861c1289a15266b85cd260a54ec2a178.

Source SHA-256:

444ae03bccdf292b3a40a3a2a62ad069d507ac72ea8ba2c6886077483d330778.

Source bytes:

12107.

OUTPUT

RUN 1 SHA-256:

822512fb20c2b2f943767f3e92a3f6188889a183a09487b975775c157b8ef8a2.

RUN 2 SHA-256:

822512fb20c2b2f943767f3e92a3f6188889a183a09487b975775c157b8ef8a2.

Byte-identical:

PASS.

MECHANICAL VALIDITY

mechanical_valid:

TRUE.

FROZEN SIGNALS

CROSSPLANE_FALSE_REPAIR_SUPPRESSION:

TRUE.

LOGICAL_REPAIR_PRESERVATION:

TRUE.

CROSSPLANE_CONFIDENCE_SIGNAL:

TRUE.

CROSSPLANE_CORRELATED_FAILURE:

TRUE.

SUPPORT THRESHOLD:

2:
bit planes.

ONE-PLANE CORRELATED-INTEGRITY FAILURE — FIXED

CHECK4_BIT0_D6.

GREEDY_BASELINE:

inferred flips:

8.

applied flips:

8.

false applied flips:

8.

false-applied fraction:

1.0.

median:
logical divergence area:

2.875.

CROSSPLANE2_GATE:

inferred flips:

8.

applied flips:

0.

abstained inferred flips:

8.

false applied flips:

0.

median:
logical divergence area:

0.

sustained exact logical recovery:

1.0.

CHECK4_BIT0_D7.

GREEDY_BASELINE:

false applied flips:

8.

median:
logical divergence area:

1.9999999999999998.

CROSSPLANE2_GATE:

applied flips:

0.

false applied flips:

0.

logical divergence area:

0.

sustained exact logical recovery:

1.0.

Thus:

one-plane:
integrity:
corruption

can:
still:
fool:
the:
05H:
localizer,

but:

the:
cross-plane:
confidence:
gate

correctly:
recognizes:

the:
same:
logical:
region

is:
NOT:
independently:
implicated
on:
multiple:
bit planes.

TRUE LOGICAL REPAIR — PRESERVED

LOCAL_DATA2_D6.

CROSSPLANE2_GATE:

logical divergence area:

0.

sustained exact recovery:

1.0.

false applied flips:

0.

DISTRIBUTED_DATA2.

Two:
damaged:
logical:
regions.

CROSSPLANE2_GATE:

logical divergence area:

0.

sustained exact recovery:

1.0.

applied flips:

32.

false applied flips:

0.

DATA2_PLUS_CHECK2_D6.

logical divergence area:

0.

sustained exact recovery:

1.0.

false applied flips:

0.

DATA2_PLUS_CHECK3_D7.

logical divergence area:

0.

sustained exact recovery:

1.0.

false applied flips:

0.

Thus:

the:
confidence:
gate

preserves:
all:
frozen:
two-plane:
logical:
repair:
positives

while:

eliminating:
the:
one-plane:
CHECK4:
false-repair:
mode.

LOGICAL_REPAIR_PRESERVATION:

PASS.

SINGLE-BIT SENSITIVITY COST

SINGLE_DATA1_D6.

GREEDY_BASELINE:

logical divergence area:

0.

sustained exact recovery:

1.0.

false applied flips:

0.

CROSSPLANE2_GATE:

inferred flips:

8.

applied flips:

0.

abstained inferred flips:

8.

false applied flips:

0.

median:
logical divergence area:

2.875.

sustained exact recovery:

0.25.

Thus:

the:
same:
confidence:
rule

that:
suppresses:
single-plane:
integrity:
masquerades

also:
suppresses:

true:
single-plane:
logical:
faults.

This:
is:
the:
frozen:
specificity /
sensitivity:
tradeoff.

ADVERSARIAL CROSS-PLANE BOUNDARY

CHECK4_BITS01_D6.

Four:
corrupted:
integrity:
channels.

Each:
lies
on:

bit plane 0
and:
bit plane 1.

GREEDY_BASELINE:

false applied flips:

16.

logical divergence area:

3.166666666666667.

CROSSPLANE2_GATE:

inferred flips:

16.

plane support:

2:
for:
the:
same:
healthy:
logical:
region.

applied flips:

16.

false applied flips:

16.

false-applied fraction:

1.0.

logical divergence area:

3.166666666666667.

sustained exact recovery:

0.

CROSSPLANE_CORRELATED_FAILURE:

TRUE.

Thus:

cross-plane:
agreement

is:
useful:

only:
to:
the:
extent
that:

faults:
across:
bit planes

are:
not:
themselves:
correlated.

MECHANISTIC CONCLUSION

DG-1R-05I adds:

FAULT-TYPE:
CONFIDENCE

as:
a:
distinct:
software-tissue:
function.

The:
same:
hypergraph:
syndrome:

can:
suggest:
a:
logical:
repair

without:
proving:
that:
logical:
state
is:
the:
source:
of:
the:
fault.

Cross-plane:
coherence

provides:
additional:
evidence:

multi-bit:
logical:
damage
often:
implicates:
the:
same:
region

across:
multiple:
planes.

That:
lets:
the:
system

reject:
some:
integrity:
masquerades

without:
additional:
persistent:
state.

However:

the:
confidence:
signal

is:
not:
independent:
truth.

If:
integrity:
faults

are:
correlated
across:
the:
same:
multiple:
planes,

they:
can:
manufacture:
the:
same:
confidence:
pattern.

Likewise:

true:
single-bit:
logical:
damage

does:
not:
provide:
cross-plane:
support

and:
is:
missed.

Therefore:

the:
remaining:
problem

is:
not:

which:
static:
threshold
to:
choose.

It is:

IDENTIFIABILITY.

Some:
fault:
classes

produce:
overlapping:
observations

under:
the:
current:
128-bit:
snapshot.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05J —
FAULT:
IDENTIFIABILITY /
SYNDROME-COLLISION:
AUDIT.

No:
new:
repair:
heuristic.

Instead:

exhaustively:
analyze:

the:
frozen:
HYPER20:
observation:
space.

For:
each:
bit plane:

enumerate:
bounded:
combinations
of:

- logical:
  faults;
- integrity:
  faults.

Map:

fault explanation
->
20-bit syndrome.

Measure:

- exact:
  syndrome collisions;
- minimum:
  integrity-fault:
  count
  that:
  can:
  imitate:
  one:
  logical:
  fault;
- minimum:
  logical-plus-integrity:
  explanation
  for:
  check-only:
  patterns;
- degree-6:
  and:
  degree-7:
  decision:
  boundaries;
- ambiguity:
  under:
  weighted:
  fault-cost:
  ratios.

Then:
lift:
the:
analysis

across:
multiple:
bit planes

to:
measure:

when:
cross-plane:
support
is:
actually:
independent

and:

when:
correlated:
integrity:
faults
can:
exactly:
imitate:
multi-bit:
logical:
damage.

Primary question:

WHAT:
FAULT:
CLASSES

ARE:
DISTINGUISHABLE

FROM:
THE:
CURRENT:
128-BIT:
STATE

IN:
PRINCIPLE?

If:
two:
different:
fault:
classes

produce:
the:
same:
observable:
syndrome:

no:
decoder:
can:
distinguish:
them
without:

additional:
information,
time,
prior:
assumptions,
or:
independent:
state.

That:
boundary
should:
be:
mapped
before:
adding:
another:
repair:
heuristic.

PLAIN-SPEAK SUMMARY

This:
worked
exactly:
the:
way:
we:
hoped.

When:
four:
backup:
channels
lied
on:
only:
one:
bit:
plane,

the:
old:
decoder
thought:
healthy:
data
was:
damaged.

The:
new:
confidence:
rule
asked:

"Does:
this:
same:
data:
region
look:
damaged
on:
more:
than:
one:
plane?"

The:
answer
was:
no,

so:
it:
refused:
the:
bad:
repair.

At:
the:
same:
time,

real:
two-bit:
data:
damage
still:
repaired:
perfectly,

including:
two:
damaged:
regions
at:
once.

But:
there:
are:
two:
costs.

A:
real:
single-bit:
data:
fault
only:
shows:
up:
on:
one:
plane,

so:
the:
new:
rule
refuses:
to:
repair:
that:
too.

And:
if:
the:
backup:
channels
lie:
on:
two:
planes
at:
the:
same:
time,

they:
can:
fake:
the:
same:
confidence:
signal

and:
the:
system
is:
fooled
again.

So:
we:
have:
reached:
a:
more:
fundamental:
question:

are:
some:
different:
kinds:
of:
damage

literally:
indistinguishable
from:
the:
information
currently:
stored?

The:
next:
experiment
will:
map:
that:
boundary
directly

instead:
of:
guessing:
another:
threshold.

DG-1R-05:
canonical frozen primary remains:

UNSPENT.

DG-1R-05I remains:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05I CROSS-BIT-PLANE CONFIDENCE

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05I:
WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05i_cross_plane_confidence_v1.py

Harness commit:

2de820a82832a1f72d5a07cd798f3739e0b7b9e7.

Git blob SHA:

3b41748cc3832602d53e28370e9e06ea0bc21bf0.

Remote source SHA-256:

989bc8499f3c087596072053132461ade0c39153b42f3d03b99834e9f6d2731e.

Remote source bytes:

13527.

LOCAL PRECHECK

Exact:
Git blob:
identity:

PASS.

Python syntax:

PASS.

Frozen:
hypergraph:
mechanical:
validation:

PASS.

Pre-run:
algebra:
sanity:

LOCAL_DATA2_D6:

block 5:
plane support:

2.

CHECK4_BIT0_D6:

block 5:
plane support:

1.

CHECK4_BITS01_D6:

block 5:
plane support:

2.

SINGLE_DATA1_D6:

block 5:
plane support:

1.

These:
sanity:
checks

are:
NON-EVIDENCE.

No:
DG-1R-05I:
world
was:
executed
before:
this:
freeze.

FROZEN WORLD FAMILY

20260926059000..20260926059007.

8 worlds.

FROZEN METHODS

GREEDY_BASELINE.

CROSSPLANE2_GATE.

CROSSPLANE2_DETECT_ONLY.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

DG-1R-05I:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-FREEZE REVALIDATION CLOSURE — CURRENT AUTHORITATIVE DG-1R-05I HARNESS

DATE:
2026-09-20.

STATUS:
COMPLETE /
PROVENANCE RECONCILED /
TWO BYTE-IDENTICAL SWEEPS /
NON-CANONICAL /
NON-EVIDENCE.

WHY THIS REVALIDATION WAS REQUIRED

An earlier DG-1R-05I closure certified the earlier harness blob:

00dc7efc861c1289a15266b85cd260a54ec2a178.

The branch later re-froze a byte-distinct authoritative harness.
Therefore the earlier closure was historical evidence for the earlier bytes,
not certification of the current frozen bytes.

LIVE BRANCH VERIFICATION BEFORE WRITE

Branch:
dg1a-ar.

Verified pre-write HEAD:

3e98be98cbc3ea875efa77ad933e253ceeba6e08.

Commit message:

Freeze DG-1R-05I cross-plane confidence harness.

CURRENT AUTHORITATIVE HARNESS

Path:

research/experiments/dg1r/harnesses/dg1r_05i_cross_plane_confidence_v1.py

Git blob SHA:

3b41748cc3832602d53e28370e9e06ea0bc21bf0.

Source SHA-256:

989bc8499f3c087596072053132461ade0c39153b42f3d03b99834e9f6d2731e.

Source bytes:

13527.

The executed local copy was verified byte-for-byte by source size and SHA-256
against the frozen remote source before primary execution.

PRIMARY EXECUTION

Frozen worlds:

20260926059000..20260926059007.

World count:

8.

Sweep 1 output SHA-256:

fe4a36fad97f1c166a058b4593d3753c2cb62cde4f324c9e9d6a627d05208cc5.

Sweep 2 output SHA-256:

fe4a36fad97f1c166a058b4593d3753c2cb62cde4f324c9e9d6a627d05208cc5.

Byte-identical:

PASS.

Mechanical validity:

TRUE.

FROZEN SIGNALS

CROSSPLANE_FALSE_REPAIR_SUPPRESSION:

TRUE.

LOGICAL_REPAIR_PRESERVATION:

TRUE.

CROSSPLANE_CONFIDENCE_SIGNAL:

TRUE.

CROSSPLANE_CORRELATED_FAILURE:

TRUE.

TECHNICAL EVIDENCE

CHECK4_BIT0_D6:

GREEDY_BASELINE false applied logical flips:
8.

GREEDY_BASELINE median logical divergence area:
2.875.

CROSSPLANE2_GATE false applied logical flips:
0.

CROSSPLANE2_GATE median logical divergence area:
0.0.

CROSSPLANE2_GATE sustained exact logical recovery:
1.0.

CHECK4_BIT0_D7:

GREEDY_BASELINE false applied logical flips:
8.

GREEDY_BASELINE median logical divergence area:
1.9999999999999998.

CROSSPLANE2_GATE false applied logical flips:
0.

CROSSPLANE2_GATE median logical divergence area:
0.0.

CROSSPLANE2_GATE sustained exact logical recovery:
1.0.

TRUE TWO-PLANE LOGICAL DAMAGE

LOCAL_DATA2_D6:
gate median logical divergence area 0.0;
sustained exact logical recovery 1.0;
false applied flips 0.

DISTRIBUTED_DATA2:
gate median logical divergence area 0.0;
sustained exact logical recovery 1.0;
false applied flips 0;
applied logical flips 32 across the sweep.

DATA2_PLUS_CHECK2_D6:
gate median logical divergence area 0.0;
sustained exact logical recovery 1.0;
false applied flips 0.

DATA2_PLUS_CHECK3_D7:
gate median logical divergence area 0.0;
sustained exact logical recovery 1.0;
false applied flips 0.

SINGLE-BIT SENSITIVITY COST

SINGLE_DATA1_D6:

GREEDY_BASELINE median logical divergence area:
0.0.

GREEDY_BASELINE sustained exact logical recovery:
1.0.

CROSSPLANE2_GATE applied logical flips:
0.

CROSSPLANE2_GATE median logical divergence area:
2.875.

CROSSPLANE2_GATE sustained exact logical recovery:
0.25.

CORRELATED CROSS-PLANE BOUNDARY

CHECK4_BITS01_D6:

GREEDY_BASELINE false applied logical flips:
16.

CROSSPLANE2_GATE false applied logical flips:
16.

CROSSPLANE2_GATE median logical divergence area:
3.166666666666667.

CROSSPLANE2_GATE sustained exact logical recovery:
0.0.

INTERPRETATION

The current authoritative harness reproduces the same mechanistic conclusion
as the historical DG-1R-05I closure.

Cross-plane agreement is a useful confidence signal when integrity faults are
not themselves correlated across planes.

It suppresses the frozen one-plane integrity masquerades without sacrificing
the frozen two-plane logical-repair positives.

It is not an independent truth signal.

A true single-plane logical fault is rejected by the same confidence rule,
and correlated integrity faults spanning two planes can manufacture the
required support and trigger a false logical repair.

The unresolved boundary is therefore IDENTIFIABILITY, not threshold tuning.

PLAIN-SPEAK INTERPRETATION

The extra confidence check really does help.

If only one bit plane says a region is damaged, the system can refuse a bad
repair and avoid being tricked by several corrupted backup checks.

But that safety comes with a cost: a real one-bit data fault also looks like
only one vote, so it can be missed.

And if corrupted backup checks coordinate across two bit planes, they can
fake two votes and fool the system again.

So the next problem is not finding a cleverer cutoff. We need to determine
which kinds of damage can actually be told apart from the information stored
in the current 128-bit state.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05J —
FAULT IDENTIFIABILITY / SYNDROME-COLLISION AUDIT.

No new repair heuristic should be introduced before that boundary is mapped.

No post-result tuning was performed.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
