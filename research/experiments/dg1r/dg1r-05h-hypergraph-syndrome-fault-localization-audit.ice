TITLE: DG-1R-05H — Hypergraph Syndrome / Fault-Localization Decoder Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE DECODER-LIMIT PILOT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / FAULT LOCALIZATION
BRANCH: dg1a-ar
PARENT: DG-1R-05G

PURPOSE

DG-1R-05G established:

- the same 48 logical + 80 integrity bits can double witness incidence from 40 to 80 through four-region hyperchecks;
- naive local majority exactly repairs local damage with two bad witnesses;
- degree-7 majority exactly repairs local damage with three bad witnesses;
- exact 3-vs-3 evidence split safely abstains;
- four correlated bad witnesses form a wrong strict majority;
- two simultaneous logical lesions cause candidate contamination and secondary false repair.

Thus:

the:
representation

may:
contain:
enough:
information,

while:

NAIVE:
LOCAL:
MAJORITY

may:
be:
the:
actual:
failure.

DG-1R-05H asks:

IS:
THE:
DISTRIBUTED:
FAILURE

A:

REPRESENTATION:
LIMIT

OR:

A:
DECODER:
LIMIT?

BOUNDARY

Synthetic software-only pilot.

No:
living tissue.
No:
wetware.
No:
biological nanotechnology.
No:
production modification.
No:
canonical H191 execution.
No:
STAB-18-R1 execution.

NON-CANONICAL /
NON-EVIDENCE.

DG-1R-05 canonical frozen primary remains:
UNSPENT.

STATE REPRESENTATION

Exact:
DG-1R-05G:
HYPER20:
representation.

48:
logical bits.

80:
integrity bits.

128:
total:
persistent bits.

20:
four-region:
hyperchecks.

Exact:
frozen:
hyperedge set
from:
DG-1R-05G.

No:
representation:
change.

SYNDROME

For:
each:
logical:
bit plane
k in:
0..3:

for:
each:
hypercheck i:

s_i
=
stored_check_i[k]
XOR
XOR(
current logical bit k
for:
all:
logical blocks
in:
hypercheck i
).

Healthy:
state:

s_i = 0.

Faults:

logical:
data-bit:
fault
toggles:

every:
incident:
hypercheck:
syndrome.

Integrity-check:
bit fault
toggles:

only:
its:
own:
hypercheck:
syndrome.

Thus:

per:
bit plane,

the:
observed:
20-bit:
syndrome

contains:
information
about:

12:
possible:
logical-data:
fault locations

plus:

20:
possible:
integrity-bit:
fault locations.

METHOD 1 — NAIVE_MAJORITY

Exact:
DG-1R-05G:
HYPER20_MAJORITY_48.

Purpose:

frozen:
reference.

METHOD 2 — MW_UNIQUE

Minimum-weight:
syndrome:
decoder.

For:
each:
bit plane:

enumerate:

all:
2^12
=
4096:

logical-data:
fault masks.

For:
a:
candidate:
logical fault vector e_d:

compute:

predicted:
syndrome
from:
logical faults.

Residual:

r
=
observed_syndrome
XOR
predicted_syndrome.

Interpret:

r:

as:
the:
minimum:
integrity-check:
fault vector

for:
that:
logical:
fault mask

because:
each:
integrity bit
maps:
directly
to:
one:
syndrome:
position.

Total:
fault weight:

w
=
popcount(e_d)
+
popcount(r).

Find:

global:
minimum:
w.

If:

exactly:
one:
logical-data:
fault mask

achieves:
the:
minimum:

apply:
those:
logical:
bit:
corrections.

If:

multiple:
logical:
fault masks

tie:
for:
minimum:

ABSTAIN
for:
that:
bit plane.

Purpose:

information-content:
upper bound.

This:
is:
not:
claimed
as:
a:
local:
biological:
mechanism.

It asks:

does:
the:
same:
128-bit:
state

contain:
enough:
information
in:
principle?

METHOD 3 — GREEDY_SYNDROME

Iterative:
syndrome:
bit-flip:
decoder.

For:
each:
bit plane:

start:
with:
observed:
syndrome.

At:
each:
iteration:

for:
each:
logical:
block j:

compute:

syndrome weight
before:

W.

Compute:

W_j

after:
hypothetically:
flipping:
logical:
bit:
j.

Reduction:

R_j
=
W - W_j.

Choose:

the:
logical:
bit
with:

largest:
strictly:
positive:
R_j.

Tie:

smallest:
logical:
block:
index.

Apply:
that:
inferred:
logical:
flip
to:
the:
decoder's:
working:
syndrome.

Repeat:

maximum:
4:
logical:
flips
per:
bit plane.

Stop:
early
if:

no:
logical:
flip
strictly:
reduces:
syndrome:
weight.

After:
inference:

apply:
the:
inferred:
logical:
bit:
corrections

simultaneously
to:
the:
persistent:
logical:
state.

Remaining:
syndrome

is:
treated
as:
integrity-bit:
fault evidence.

Integrity:
slots
are:
not:
individually:
rewritten
during:
repair.

They:
are:
naturally:
re-encoded
after:
the:
logical:
CA:
update.

Purpose:

low-complexity:
syndrome-guided:
fault:
localization.

METHOD 4 — GREEDY_SINGLE_PASS

Same:
syndrome:
reduction:
score

but:

allow:
at most:

ONE:
logical:
bit:
flip
per:
bit plane.

Purpose:

test:
whether:
iterative:
multi-region:
localization

adds:
value
beyond:
one:
best:
repair.

DYNAMICS

Exact:
DG-1R-05G.

48:
logical:
bits.

MIXED5:
one:
CA:
update
per:
external:
input.

Input:
mapped:
logical:
blocks:

1,
4,
7,
10.

Pre-damage:

1024:
steps.

Post-damage:

32:
steps.

Repair:

before:
current:
input overwrite.

Then:

logical:
CA:
update.

Then:

all:
20:
hyperchecks
recomputed.

WORLD FAMILY

8:
worlds.

Seeds:

20260926058000
through:
20260926058007.

No:
prior:
DG-1R:
seed reuse.

DAMAGE FAMILIES

Use:
the:
exact:
DG-1R-05G:
hypergraph:
damage:
families.

LOCAL_DATA2_D6.

CHECK2_CORRELATED_D6.

CHECK3_CORRELATED_D6.

CHECK4_CORRELATED_D6.

DATA2_PLUS_CHECK2_D6.

DATA2_PLUS_CHECK3_D7.

CHECK4_CORRELATED_D7.

DISTRIBUTED_LOCAL_DATA2.

Exact:
target:
blocks,
integrity slots,
bit positions,
and:
lesion:
cardinalities

remain:
unchanged.

MECHANICAL ASSERTIONS

Harness MUST:

- reproduce:
  the:
  frozen:
  hypergraph:
  degree vector;
- reproduce:
  maximum:
  pair:
  co-occurrence:
  <=2;
- assert:
  exact:
  lesion:
  cardinalities;
- assert:
  no:
  logical:
  lesion
  overlaps:
  current:
  input-mapped:
  logical:
  bit;
- verify:
  duplicate:
  no-damage:
  trajectories.

PRIMARY METRICS

At:
horizons:

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
- logical recovery time;
- inferred logical flips;
- false logical flips;
- ambiguous MW bit-planes;
- final syndrome weight;
- decoder iterations.

FALSE LOGICAL FLIP

An:
inferred:
logical:
bit:
correction

is:
FALSE

if:

the:
post-correction:
logical:
bit

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

Decoder:

never:
sees:
this:
label.

It is:
evaluation:
telemetry only.

DISTRIBUTED LOCALIZATION SIGNAL

TRUE
if:

on:
DISTRIBUTED_LOCAL_DATA2:

MW_UNIQUE
and/or:
GREEDY_SYNDROME

has:

1.
median:
logical divergence
at:
h1
=
0;

2.
median:
logical divergence area
=
0;

3.
sustained exact logical recovery
>=0.90;

4.
false logical flip fraction
<=0.01;

while:

NAIVE_MAJORITY

fails:
at least:
one:
criterion.

REPRESENTATION-SUFFICIENT SIGNAL

TRUE
if:

MW_UNIQUE

passes:

DISTRIBUTED_LOCALIZATION_SIGNAL.

Interpretation:

the:
stored:
hypergraph:
state

contained:
enough:
information;

the:
DG-1R-05G:
failure

was:
a:
decoder:
failure.

LOCAL DECODER SIGNAL

TRUE
if:

GREEDY_SYNDROME

passes:

DISTRIBUTED_LOCALIZATION_SIGNAL

and:

its:
local:
positive:
results
on:

DATA2_PLUS_CHECK2_D6

and:
DATA2_PLUS_CHECK3_D7

remain:
exact.

ITERATION VALUE SIGNAL

TRUE
if:

GREEDY_SYNDROME

outperforms:

GREEDY_SINGLE_PASS

on:
DISTRIBUTED_LOCAL_DATA2

without:
worse:
false-flip:
rate
on:
local:
fault:
families.

AMBIGUITY BOUNDARY

MW_UNIQUE

must:
report:

minimum-weight:
ties.

A:
tie:

means:

the:
stored:
integrity:
state

does NOT:
uniquely:
identify:

which:
logical:
fault:
explanation

is:
correct

under:
equal:
fault:
cost.

No:
repair
is:
allowed
for:
that:
bit plane.

This:
is:
an:
information:
boundary,

not:
a:
decoder:
failure.

CORRELATED-FAULT BOUNDARY

CHECK4_CORRELATED_D6.
CHECK4_CORRELATED_D7.

No:
positive:
claim
is:
pre-registered.

These:
remain:
adversarial:
boundary:
tests.

If:

MW_UNIQUE
or:
GREEDY_SYNDROME

still:
mislocalizes:
them,

report:
the:
boundary.

IMPORTANT

MW_UNIQUE
is:

an:
upper-bound:
information:
probe.

GREEDY_SYNDROME
is:

the:
architecturally:
interesting:
candidate.

A:
positive:
MW result
and:
negative:
GREEDY result

means:

the:
information
exists

but:

the:
local:
repair:
algorithm
is:
insufficient.

A:
positive:
GREEDY result

means:

the:
same:
128-bit:
organism

can:
use:

syndrome:
reduction

to:
prevent:
the:
hypergraph:
damage:
cascade

without:
more:
persistent:
state.

RELATION TO EXTERNAL RESEARCH

Sparse:
parity-check:
codes

and:
bit-flipping:
decoders

use:

parity:
syndrome
and:
check:
reliability

to:
localize:
faults.

DG-1R-05H:

does NOT:
claim:
novelty
over:
coding:
theory.

Its:
purpose:

test:
whether:
that:
principle

is:
useful
inside:
Yggdrasil's:
same-budget:
developmental:
software-tissue:
architecture.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-05H:
scenario:

do not alter:

- hypergraph;
- fault cost;
- MW uniqueness rule;
- greedy score;
- greedy iteration cap;
- tie rule;
- damage family;
- world family;
- thresholds;
- metrics.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
hypergraph:
had:
lots:
of:
backup:
information,

but:
our:
repair:
system
was:
using:
a:
very:
simple:
rule:

"whichever:
answer
has:
the:
most:
votes
wins."

That:
worked:
when:
only:
one:
region
was:
damaged.

With:
two:
damaged:
regions,

their:
errors
contaminated:
other:
votes

and:
the:
system
started:
repairing:
healthy:
regions.

This:
experiment
asks:

what:
if:
the:
organism
looks:
at:

THE:
PATTERN:
OF:
BROKEN:
CHECKS

instead:
of:
only:
counting:
votes?

A:
damaged:
data:
bit
breaks:
many:
checks
in:
a:
specific:
pattern.

A:
damaged:
backup:
bit
breaks:
only:
one:
check.

That:
pattern
may:
tell:
the:
system

where:
the:
real:
damage
is.

If:
it:
can:

the:
hypergraph's:
distributed:
failure

was:
not:
because:
we:
lacked:
enough:
backup:
information.

It:
was:
because:
we:
were:
reading:
the:
backup:
information
too:
simply.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN CLARIFICATION 01 — GREEDY LOCATION REUSE

DATE:
2026-09-20.

STATUS:
CLARIFIED BEFORE:
ANY:
DG-1R-05H:
WORLD.

Within:
one:
logical:
bit plane,

GREEDY_SYNDROME
and:
GREEDY_SINGLE_PASS

may:
select:
a:
given:
logical:
block:
location

at most:

ONCE.

Reason:

an:
inferred:
fault:
bit

is:
a:
binary:
correction.

Repeatedly:
selecting:
the:
same:
location

would:
toggle:
the:
same:
hypothesis
back:
off

and:
turn:
the:
iteration:
count

into:
an:
implementation:
artifact.

All:
other:
frozen:
decoder:
semantics
remain:
unchanged.

No:
DG-1R-05H:
scenario
was:
executed
before:
this:
clarification.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05H HYPERGRAPH SYNDROME DECODING

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05H:
WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05h_hypergraph_syndrome_v1.py

Harness commit:

599253a50aa9bcbe0d2327cb07ee3f7771d6830a.

Git blob SHA:

95f3aaf2b195197e459db6d18584f912a7598e9f.

Remote source SHA-256:

53c5585408734648883b1063d79cf19f99feb207e6ebe3a68c75f15d4122e127.

Remote source bytes:

14718.

LOCAL PRECHECK

Python syntax:

PASS.

Hypergraph mechanical validation:

PASS.

Distributed:
block-2 /
block-8:
bit-plane:
fault

minimum-weight:
solution:

weight:

2.

Unique logical fault mask:

{2,8}.

PASS.

No:
DG-1R-05H:
experimental:
world
was:
executed
before:
this:
freeze.

PACKAGING NOTE

GitHub:
stored:
the:
same:
Python:
source

without:
the:
local:
final:
newline.

No:
experimental:
semantic:
changed.

The:
execution copy
was:
aligned
to:
the:
authoritative:
remote:
bytes.

FROZEN WORLD FAMILY

20260926058000..20260926058007.

8 worlds.

FROZEN METHODS

NAIVE_MAJORITY.

MW_UNIQUE.

GREEDY_SYNDROME.

GREEDY_SINGLE_PASS.

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

DG-1R-05H:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05H NON-EVIDENCE CLOSURE — HYPERGRAPH SYNDROME / FAULT LOCALIZATION

DATE:
2026-09-20.

STATUS:
COMPLETE /
STRONG POSITIVE DECODER-LIMIT RESULT /
REPRESENTATION SUFFICIENT /
ITERATIVE SYNDROME REPAIR POSITIVE /
MINIMUM-WEIGHT AMBIGUITY BOUNDED /
FOUR-CORRELATED-CHECK BOUNDARY CONFIRMED /
NON-CANONICAL /
NON-EVIDENCE.

FROZEN HARNESS

Git blob SHA:

95f3aaf2b195197e459db6d18584f912a7598e9f.

Source SHA-256:

53c5585408734648883b1063d79cf19f99feb207e6ebe3a68c75f15d4122e127.

Source bytes:

14718.

OUTPUT

RUN 1 SHA-256:

07542b76c3ff6b9d8737cddb055d362331faec8ede695c39dc58ef5fda088b35.

RUN 2 SHA-256:

07542b76c3ff6b9d8737cddb055d362331faec8ede695c39dc58ef5fda088b35.

Byte-identical:

PASS.

MECHANICAL VALIDITY

mechanical_valid:

TRUE.

FROZEN SIGNALS

DISTRIBUTED_LOCALIZATION_SIGNAL:

MW_UNIQUE.
GREEDY_SYNDROME.

REPRESENTATION_SUFFICIENT_SIGNAL:

TRUE.

LOCAL_DECODER_SIGNAL:

TRUE.

ITERATION_VALUE_SIGNAL:

TRUE.

PRIMARY DISTRIBUTED RESULT

DISTRIBUTED_LOCAL_DATA2:

two:
simultaneous:
logical:
regions

with:
two:
damaged:
data bits
each.

NAIVE_MAJORITY:

median:
h1 logical divergence:

0.19791666666666669.

median:
logical divergence area:

8.354166666666668.

sustained exact logical recovery:

0.

inferred logical flips:

32:
across:
8 worlds.

false logical flips:

32.

false-flip fraction:

1.0.

Thus:

the:
DG-1R-05G:
cascade

is:
reproduced.

MW_UNIQUE:

median:
h1 logical divergence:

0.

median:
logical divergence area:

0.

sustained exact logical recovery:

1.0.

inferred logical flips:

32.

false logical flips:

0.

final syndrome weight:

0.

No:
minimum-weight:
ambiguity.

Thus:

the:
same:
stored:
128-bit:
hypergraph state

contains:
enough:
information
to:
identify:
the:
distributed:
fault
exactly.

REPRESENTATION_SUFFICIENT_SIGNAL:

PASS.

GREEDY_SYNDROME:

median:
h1 logical divergence:

0.

median:
h4:

0.

median:
h32:

0.

median:
logical divergence area:

0.

sustained exact logical recovery:

1.0.

inferred logical flips:

32.

false logical flips:

0.

final syndrome weight:

0.

Median:
decoder iterations:

4:
bit flips
across:
the:
two:
damaged:
bit planes.

Thus:

a:
bounded:
iterative:
syndrome-reduction:
decoder

matches:
the:
global:
minimum-weight:
upper bound

on:
the:
distributed:
fault
family.

LOCAL_DECODER_SIGNAL:

PASS.

SINGLE-PASS CONTROL

GREEDY_SINGLE_PASS:

median:
h1 logical divergence:

0.05208333333333333.

median:
logical divergence area:

3.645833333333333.

sustained exact logical recovery:

0.125.

false logical flips:

0.

It:
finds:
some:
real:
damage

but:

one:
logical:
flip
per:
bit plane

is:
not:
enough
to:
localize:
both:
damaged:
regions
before:
the:
next:
state:
transition.

ITERATION_VALUE_SIGNAL:

PASS.

Thus:

REPEATED:
SYNDROME:
RE-EVALUATION

is:
a:
real:
part
of:
the:
repair:
mechanism.

LOCAL + TWO BAD CHECKS

DATA2_PLUS_CHECK2_D6.

GREEDY_SYNDROME:

median:
logical divergence area:

0.

sustained exact logical recovery:

1.0.

false logical flips:

0.

MW_UNIQUE:

same:
exact:
repair.

Thus:

syndrome localization
preserves:
the:
DG-1R-05G:
two-bad-witness:
gain.

LOCAL + THREE BAD CHECKS

DATA2_PLUS_CHECK3_D7.

GREEDY_SYNDROME:

median:
logical divergence area:

0.

sustained exact logical recovery:

1.0.

false logical flips:

0.

Thus:

the:
iterative:
decoder

also:
preserves:
the:
three-bad-witness:
local:
repair
result.

MW_UNIQUE:

ambiguous:
bit planes:

8:
across:
8 scenarios.

Median:
logical divergence area:

2.197916666666667.

sustained exact logical recovery:

0.25.

Interpretation:

under:
equal:
data-bit /
integrity-bit:
fault:
cost,

one:
damaged:
logical:
bit
plus:
three:
damaged:
check bits

can:
tie:

an:
alternative:
pure:
integrity-fault:
explanation.

MW_UNIQUE:

correctly:
ABSTAINS

because:
the:
information
is:
not:
unique
under:
that:
fault prior.

GREEDY_SYNDROME:

still:
repairs:
the:
frozen:
case
correctly

because:
its:
steepest:
syndrome-reduction:
bias

selects:
the:
logical:
fault.

This:
is:
an:
important:
distinction:

MINIMUM:
WEIGHT

is:
not:
the:
same
as:

BEST:
OPERATIONAL:
REPAIR:
INDUCTIVE:
BIAS.

CORRELATED CHECK BOUNDARY

CHECK4_CORRELATED_D6.

NAIVE_MAJORITY:

false logical flip fraction:

1.0.

GREEDY_SYNDROME:

1.0.

GREEDY_SINGLE_PASS:

1.0.

MW_UNIQUE:

1.0.

Thus:

four:
correlated:
integrity:
faults

around:
the:
degree-6:
region

can:
still:
look:
cheaper
as:

one:
logical:
fault
plus:
fewer:
check:
faults.

The:
stored:
code
does NOT:
uniquely:
protect:
against:
this:
pattern.

CHECK4_CORRELATED_D7.

GREEDY_SYNDROME:

false logical flip fraction:

1.0.

NAIVE_MAJORITY:

1.0.

GREEDY_SINGLE_PASS:

1.0.

MW_UNIQUE:

false logical flip fraction:

0.

But:

MW_UNIQUE:
reports:
8:
ambiguous:
bit planes

and:
abstains.

Thus:

the:
strict:
minimum-weight:
decoder

is:
safer
on:
this:
specific:
degree-7:
boundary,

at:
the:
cost
of:
also:
abstaining
on:
the:
valid:
DATA2_PLUS_CHECK3_D7:
repair case.

CORE MECHANISTIC CONCLUSION

DG-1R-05G's:
distributed:
failure

was:

A:
DECODER:
LIMIT,

not:

A:
REPRESENTATION:
LIMIT.

The:
same:
48:
logical bits

plus:
80:
hypergraph:
integrity bits

already:
contained:
enough:
information

to:
recover:
two:
simultaneous:
damaged:
logical:
regions.

Naive:
candidate:
majority

threw:
that:
information
away

by:
treating:
each:
candidate
as:
an:
independent:
vote.

Syndrome:
localization

uses:

the:
PATTERN:
OF:
BROKEN:
CHECKS

to:
infer:
where:
the:
fault
must:
be.

This:
is:
a:
major:
architectural:
shift.

The:
repair:
system

should:
not:
ask:

"Which:
state:
has:
the:
most:
votes?"

It:
should:
ask:

"Which:
small:
set:
of:
faults
best:
explains:
the:
pattern:
of:
integrity:
violations?"

ITERATION AS REPAIR COMPUTATION

The:
single-pass:
control

shows:

one:
repair:
decision
is:
insufficient
for:
multiple:
damaged:
regions.

The:
successful:
greedy:
decoder

does:

repair:
one:
high-confidence:
fault,

recompute:
the:
syndrome,

then:
repair:
the:
next.

Thus:

repair
is:
a:
process,

not:
a:
single:
reaction.

This:
connects:
directly
to:
Yggdrasil's:
developmental:
thesis:

local:
state
can:
be:
reorganized:
iteratively

until:
integrity:
constraints
are:
restored.

IMPORTANT LIMIT

GREEDY_SYNDROME

is:
bounded
and:
low-complexity,

but:

the:
frozen:
implementation

still:
compares:
syndrome:
reduction
across:
all:
12:
logical:
regions

to:
select:
the:
best:
next:
flip.

Therefore:

it:
is:
not:
yet:

a:
fully:
local:
distributed:
software-tissue:
repair:
mechanism.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05I —
LOCAL-MAX:
SYNDROME:
MESSAGE-PASSING:
AUDIT.

Keep:

the:
exact:
HYPER20:
128-bit:
representation.

Keep:

48:
logical bits.

Keep:

80:
integrity bits.

Replace:

global:
best:
syndrome:
selection

with:

LOCAL:
COMPETITION.

For:
each:
logical:
bit plane:

each:
logical:
region
computes:

its:
own:
syndrome-weight:
reduction
score

using:
only:

its:
incident:
checks.

A:
region
may:
flip

only if:

1.
its:
score
is:
strictly:
positive;

2.
its:
score
is:
greater
than:
all:
competing:
regions
sharing:
an:
unsatisfied:
check;

3.
ties:
use:
a:
frozen:
local:
block-ID:
rule.

Apply:

all:
non-conflicting:
local:
winners

in:
parallel.

Recompute:
syndrome.

Repeat:

bounded:
rounds.

Compare:

- GLOBAL_GREEDY:
  DG-1R-05H:
  positive reference;

- LOCAL_MAX:
  distributed:
  message-passing candidate;

- SYNCHRONOUS_THRESHOLD:
  every:
  positive-score:
  region
  flips:
  simultaneously;

- ONE_ROUND:
  local-max:
  control.

Primary question:

can:
distributed:
local:
competition

recover:
the:
same:
two-region:
damage

without:

a:
central:
winner-selection:
controller?

If:
yes:

the:
repair:
algorithm

can:
move:
from:

centralized:
syndrome:
decoding

toward:

EMERGENT:
LOCAL:
TISSUE:
REPAIR.

PLAIN-SPEAK SUMMARY

This:
was:
a:
very:
important:
result.

The:
hypergraph
did:
not:
actually:
lack:
the:
information
needed:
to:
repair:
two:
damaged:
regions.

Our:
first:
repair rule

was:
just:
too:
simple.

It:
counted:
votes.

That:
let:
damage:
in:
one:
region
poison:
the:
votes
for:
another.

When:
we:
instead:
looked:
at:

which:
checks
were:
broken

and:
asked:

"Which:
fault:
would:
explain:
this:
whole:
pattern?"

the:
same:
128-bit:
organism

repaired:
both:
damaged:
regions
perfectly.

No:
extra:
memory.

No:
extra:
backup:
bits.

The:
information
was:
already:
there.

Even:
better:

a:
simple:
iterative:
decoder
worked.

It:
fixed:
one:
likely:
fault,

looked:
again,

then:
fixed:
the:
next.

That:
means:
repair
does not:
have:
to:
be:
one:
instant:
decision.

It:
can:
be:
an:
iterative:
healing:
process.

The:
next:
step
is:
to:
remove:
the:
remaining:
central:
decision.

Instead:
of:
one:
global:
controller
choosing:
the:
best:
repair,

let:
local:
regions
compete
using:
only:
their:
nearby:
integrity:
signals.

If:
that:
works,

we:
will:
have:
moved:
another:
step
toward:

distributed:
self-healing:
software:
tissue.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

DG-1R-05H remains:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
