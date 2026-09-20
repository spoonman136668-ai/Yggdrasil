TITLE: DG-1R-05E — Multi-Witness Repair Quorum / Correlated-Fault Tolerance Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE DISTRIBUTED-QUORUM PILOT
TRACK: DG-1R / SOFTWARE CELLS / DISTRIBUTED INTEGRITY / REPAIR QUORUM
BRANCH: dg1a-ar
PARENT: DG-1R-05D

PURPOSE

DG-1R-05D showed:

- syndrome-blind neighbor-triggered repair can recover locally silent damage exactly;
- one bad witness is safely rejected by two-sided disagreement;
- two correlated bad witnesses can agree on the same wrong reconstruction and cause a false repair.

DG-1R-05E asks:

CAN:
A:
SPATIALLY:
DIVERSE:
REPAIR:
QUORUM

TOLERATE:
CORRUPTION
OF:
THE:
REPAIR:
NETWORK
ITSELF?

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

DG-1R-05:
canonical frozen primary
remains:
UNSPENT.

FIXED TOTAL STATE BUDGET

128:
persistent bits.

FIXED LOGICAL CAPACITY

32:
logical:
data bits.

8:
logical:
blocks
x:
4:
data bits.

LOCAL CODE

Each:
logical:
block
uses:

extended:
Hamming(8,4)
SECDED.

Thus:

8 blocks
x
8 bits
=
64:
local:
physical bits.

Each block:

4:
logical:
data bits.

3:
local:
Hamming:
parity bits.

1:
overall:
parity:
guardian bit.

DISTRIBUTED WITNESS NETWORK

Nearest-neighbor:
XOR ring:

8:
edges
x:
4 bits
=
32 bits.

Edge:
N_i

stores:

D_i
XOR
D_(i+1 mod 8).

Second-neighbor:
XOR ring:

8:
edges
x:
4 bits
=
32 bits.

Edge:
S_i

stores:

D_i
XOR
D_(i+2 mod 8).

Total:

64 local
+
32 nearest
+
32 second-neighbor

=
128:
persistent bits.

Each:
logical:
block b

has:
four:
candidate:
reconstruction:
witnesses:

L1:
block b-1
plus:
nearest:
edge N_(b-1).

R1:
block b+1
plus:
nearest:
edge N_b.

L2:
block b-2
plus:
second-neighbor:
edge S_(b-2).

R2:
block b+2
plus:
second-neighbor:
edge S_b.

All:
indices:
wrap:
periodically.

LOGICAL DYNAMICS

One:
MIXED5:
CA update
per:
external:
input

over:
the:
32-bit:
periodic:
logical:
ring.

Pre-damage:

1024 steps.

Post-damage:

32 steps.

Input mapping:

4:
logical:
input positions

inside:
blocks:

1,
3,
5,
7.

Primary:
damage blocks:

0,
2,
4,
6.

Thus:

damage:
blocks
are:
not:
directly:
input mapped.

METHOD 1 — TWO_WITNESS_NEAREST

Use:

L1
and:
R1.

If:

L1 == R1

AND:

current local data
!=
candidate,

repair:
to:
the:
candidate.

If:
L1 != R1:

abstain.

Purpose:

DG-1R-05D-style:
two-source:
reference.

METHOD 2 — QUORUM3_OF_4

Compute:

L1,
R1,
L2,
R2.

Count:
identical:
4-bit:
candidate:
vectors.

If:

at least:
3:
of:
4

agree
on:
one:
candidate

AND:

current local
!=
candidate,

repair:
to:
the:
quorum:
candidate.

Otherwise:

abstain.

Local:
SECDED:
status

is:
telemetry
only.

The:
quorum
may:
trigger
even:
when:
local:
SECDED
does NOT:
identify:
the:
damage.

METHOD 3 — QUORUM2_OF_4

Compute:
the:
same:
four:
witnesses.

If:

at least:
2:
agree
on:
one:
candidate

AND:

that:
candidate
is:
the:
unique:
largest:
vote group,

repair:
to:
it.

If:

2 vs 2:
tie:

abstain.

Purpose:

more:
aggressive:
quorum:
control.

METHOD 4 — QUORUM3_LOCAL_GATE

Require:

at least:
3:
of:
4:
witnesses
agree

AND:

either:

local:
SECDED:
reports:
non-clean:

OR:

current local
!=
quorum candidate.

This:
retains:
the:
syndrome-blind:
path
because:

current-vs-quorum:
mismatch
is:
sufficient
even:
if:
SECDED:
appears:
clean.

Purpose:

telemetry:
separation
of:
local:
and:
distributed:
diagnosis.

METHOD 5 — DETECT_ONLY

Compute:

local:
SECDED status

and:
four:
witness:
candidates /
vote counts.

Perform:

NO:
repair.

REPAIR ORDER

1.
inspect:
persistent:
pre-input:
local:
and:
witness:
state;

2.
perform:
allowed:
repair /
abstention;

3.
decode:
32:
logical:
data bits;

4.
apply:
current:
external:
input;

5.
one:
logical:
MIXED5:
update;

6.
recompute:
8:
local:
SECDED:
codewords;

7.
recompute:
8:
nearest-neighbor:
XOR:
edges;

8.
recompute:
8:
second-neighbor:
XOR:
edges.

DAMAGE FAMILIES

Harness MUST:
assert:
actual:
lesion:
cardinality.

LOCAL_DATA2

Inside:
one:
primary:
damage block:

flip:
physical:
local:
data positions
for:

d1,
d2.

Actual lesion size:

2.

LOCAL_SILENT3

Flip:

d1,
d2,
d3.

Actual lesion size:

3.

Purpose:

syndrome-blind /
local-code:
boundary.

LOCAL_DATA2_PLUS_ONE_WITNESS

Flip:

local:
d1,
d2

plus:

the:
L1:
nearest:
witness:
bit
for:
d1.

Actual lesion size:

3.

Expected:
quorum has:

3:
correct:
witnesses

and:

1:
bad:
witness.

TWO_CORRELATED_WITNESSES

No:
local:
data:
damage.

Flip:

L1:
witness:
d1

and:

R1:
witness:
d1.

Actual lesion size:

2.

Expected:

nearest:
two-source:
method
can:
be:
fooled.

Four-witness:
3-of-4:
method

has:

2:
correct

and:
2:
wrong

for:
d1.

No:
3-of-4:
quorum.

It:
should:
abstain.

THREE_CORRELATED_WITNESSES

No:
local:
data damage.

Flip:

L1:
d1.

R1:
d1.

L2:
d1.

Actual lesion size:

3.

Expected:

3:
witnesses
agree
on:
the:
same:
wrong:
candidate.

Purpose:

frozen:
boundary
for:
3-of-4:
quorum.

DISTRIBUTED_LOCAL_DATA2

Simultaneously:

block 0:
d1,d2.

block 4:
d1,d2.

Actual lesion size:

4.

Purpose:

parallel:
quorum:
repair.

PRIMARY METRICS

Counterfactual:
logical /
physical:
divergence
at:

1,
4,
8,
16,
32.

Also:

- logical:
  divergence area;
- physical:
  divergence area;
- sustained:
  exact:
  logical:
  recovery;
- recovery time;
- repairs;
- abstentions;
- false repairs;
- witness:
  vote:
  histogram;
- quorum:
  size;
- local:
  SECDED:
  status.

FALSE REPAIR

A:
repair:
candidate
is:
FALSE

if:

it:
does NOT:
match:
the:
counterfactual:
reference:
logical:
block

immediately:
before:
repair.

Repair logic:

never:
sees:
this:
evaluation:
label.

ONE-BAD-WITNESS TOLERANCE SIGNAL

TRUE
if:

LOCAL_DATA2_PLUS_ONE_WITNESS:

QUORUM3_OF_4

has:

1.
median:
logical divergence
at:
h1
=
0;

2.
sustained:
exact logical recovery
>=0.90;

3.
false repair fraction
<=0.01;

4.
median:
logical divergence area
=
0.

TWO-CORRELATED-WITNESS SAFETY

TRUE
if:

TWO_CORRELATED_WITNESSES:

QUORUM3_OF_4

has:

false repair count
=
0

AND:

median:
logical divergence
at:
h4
=
0.

TWO-WITNESS CONTROL FAILURE

Expected:
TRUE
if:

TWO_WITNESS_NEAREST

on:
TWO_CORRELATED_WITNESSES

has:

false repair fraction
>0.10.

This:
reproduces:
the:
DG-1R-05D:
pairwise:
consensus:
boundary.

DISTRIBUTED QUORUM SIGNAL

TRUE
if:

DISTRIBUTED_LOCAL_DATA2:

QUORUM3_OF_4

has:

median:
logical divergence
at:
h4
=
0

AND:

sustained:
exact logical recovery
>=0.75.

THREE-CORRELATED-WITNESS BOUNDARY

Flag:
QUORUM3_OF_4

if:

THREE_CORRELATED_WITNESSES:

false repair fraction
>0.10.

This:
is:
the:
expected:
quorum:
failure:
boundary.

CAPACITY COST

DG-1R-05E:

32:
logical:
bits
inside:
128:
physical:
bits.

DG-1R-05C/D:

48 logical bits.

DG-1R-05A/B:

64 logical bits.

Therefore:

increasing:
witness:
diversity

reduces:
independent:
logical:
capacity.

Any:
positive:
fault-tolerance:
result

must:
report:
this:
tradeoff.

WORLD FAMILY

8:
worlds.

Seeds:

20260926055000
through:
20260926055007.

No:
prior:
DG-1R:
seed reuse.

NO POST-RUN TUNING

After:
the:
first:
scenario:

do not alter:

- local:
  SECDED:
  representation;
- nearest:
  witness:
  ring;
- second-neighbor:
  witness:
  ring;
- quorum:
  definitions;
- damage:
  families;
- damage:
  blocks;
- world:
  family;
- metrics;
- thresholds.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

PLAIN-SPEAK PRE-REGISTERED QUESTION

Two:
neighbors
were:
enough
to:
repair:
ordinary:
damage.

But:
if:
both:
neighbors
were:
damaged
in:
the:
same:
way,

they:
could:
agree
on:
the:
same:
wrong:
answer.

So:
now:
each:
region
gets:
four:
independent:
witnesses:

two:
nearby

and:
two:
farther:
away.

A:
repair
needs:
at least:
three:
of:
the:
four
to:
agree.

If:
one:
witness
is:
wrong,

the:
other:
three
should:
still:
recover:
the:
right:
state.

If:
two:
witnesses
are:
wrong
in:
the:
same:
way,

there:
should:
be:
no:
three-vote:
majority,

so:
the:
tissue
should:
refuse:
to:
guess.

If:
three:
witnesses
are:
corrupted
together,

the:
quorum
may:
still:
be:
fooled.

That:
will:
show:
the:
next:
fault-tolerance:
boundary.

The:
cost
is:
real.

We:
have:
only:
32:
logical:
data bits
left
inside:
the:
same:
128-bit:
organism.

So:
this:
experiment
is:
also:
measuring:
how:
much:
capacity
we:
have:
to:
spend
for:
stronger:
self-repair.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05E MULTI-WITNESS QUORUM HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05E:
SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05e_multiwitness_quorum_v1.py

Harness commit:

89c81b17b56b89fec84bbf71c0df0919e4e673fe.

Git blob SHA:

2af536002441f63ea46a1fad714cc44484435392.

Source SHA-256:

1c35eae936d76542fccd757c9b26fe153b69ad81083888638e9c05181c382e88.

Source bytes:

11803.

LOCAL PRECHECK

Exact:
Git blob:
identity:

PASS.

Python:
syntax:

PASS.

No:
DG-1R-05E:
scenario
was:
executed
before:
this:
freeze.

FROZEN WORLD FAMILY

20260926055000..20260926055007.

8 worlds.

FROZEN LOGICAL CAPACITY

32 bits.

FROZEN PHYSICAL BUDGET

128 bits.

FROZEN WITNESS TOPOLOGY

4 candidates:
L1,
R1,
L2,
R2.

DG-1R-05 CANONICAL STATUS

Still:

UNSPENT.

DG-1R-05E:

NON-CANONICAL /
NON-EVIDENCE.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05E NON-EVIDENCE CLOSURE — MULTI-WITNESS REPAIR QUORUM

DATE:
2026-09-20.

STATUS:
COMPLETE /
STRONG POSITIVE ONE-BAD-WITNESS TOLERANCE /
STRONG POSITIVE TWO-CORRELATED-WITNESS SAFETY /
DISTRIBUTED QUORUM REPAIR PASS /
THREE-CORRELATED-WITNESS BOUNDARY CONFIRMED /
NON-CANONICAL /
NON-EVIDENCE.

FROZEN HARNESS

Git blob SHA:

2af536002441f63ea46a1fad714cc44484435392.

Source SHA-256:

1c35eae936d76542fccd757c9b26fe153b69ad81083888638e9c05181c382e88.

Source bytes:

11803.

OUTPUT

RUN 1 SHA-256:

e686fc0fe1b7e459e1396b581c5ff38c8d5126e3bde72f8426c7b4c011b16419.

RUN 2 SHA-256:

e686fc0fe1b7e459e1396b581c5ff38c8d5126e3bde72f8426c7b4c011b16419.

Byte-identical:

PASS.

MECHANICAL VALIDITY

mechanical_valid:

TRUE.

FROZEN SIGNALS

ONE_BAD_WITNESS_TOLERANCE_SIGNAL:

TRUE.

TWO_CORRELATED_WITNESS_SAFETY:

TRUE.

TWO_WITNESS_CONTROL_FAILURE:

TRUE.

DISTRIBUTED_QUORUM_SIGNAL:

TRUE.

THREE_CORRELATED_WITNESS_BOUNDARY:

TRUE.

ONE BAD WITNESS + LOCAL DAMAGE

LOCAL_DATA2_PLUS_ONE_WITNESS.

QUORUM3_OF_4:

median:
logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

h1:
logical divergence:

0.

repairs:

32.

3-vote repairs:

32.

false-repair fraction:

0.

Thus:

one:
corrupted:
integrity:
channel

does NOT:
prevent:

exact:
local:
state:
reconstruction

when:

three:
independent:
witnesses
still:
agree.

TWO CORRELATED BAD WITNESSES

TWO_CORRELATED_WITNESSES.

QUORUM3_OF_4:

repairs:

0.

abstentions:

32.

false repairs:

0.

logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

The:
local:
data
was:
healthy.

Two:
witnesses
agree
on:
one:
wrong:
candidate.

Two:
witnesses
agree
on:
the:
correct:
candidate.

No:
3-of-4:
quorum
exists.

The:
system
therefore:

REFUSES:
TO:
REPAIR.

The:
damaged:
witness:
state
is:
subsequently:
refreshed
from:
healthy:
logical:
state.

TWO_CORRELATED_WITNESS_SAFETY:

PASS.

TWO-WITNESS REFERENCE FAILURE

TWO_WITNESS_NEAREST:

same:
two-correlated-witness:
damage.

repairs:

32.

false-repair fraction:

1.0.

median:
logical divergence area:

2.875.

sustained:
exact logical recovery:

0.46875.

Thus:

the:
additional:
spatially:
diverse:
witnesses

directly:
eliminate:
the:
pairwise:
consensus:
failure
from:
DG-1R-05D.

LOCAL DAMAGE

LOCAL_DATA2.

QUORUM3_OF_4:

logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

4-vote repairs:

32.

LOCAL_SILENT3:

logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

4-vote repairs:

32.

Thus:

the:
quorum
retains:
syndrome-blind:
self-diagnosis
and:
repair.

DISTRIBUTED DAMAGE

DISTRIBUTED_LOCAL_DATA2:

two:
separated:
damaged:
logical:
regions.

QUORUM3_OF_4:

logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

repairs:

16.

false repairs:

0.

DISTRIBUTED_QUORUM_SIGNAL:

PASS.

THREE CORRELATED BAD WITNESSES

THREE_CORRELATED_WITNESSES.

QUORUM3_OF_4:

repairs:

32.

3-vote repairs:

32.

false-repair fraction:

1.0.

median:
logical divergence area:

2.875.

sustained:
exact logical recovery:

0.46875.

Thus:

a:
3-of-4:
quorum

can:
be:
confidently:
wrong

when:

three:
integrity:
channels

share:
the:
same:
correlated:
fault.

This:
is:
the:
expected:
quorum:
boundary.

QUORUM2_OF_4

Under:
the:
frozen:
unique-largest-group:
rule,

QUORUM2_OF_4:

also:
abstains
on:

2-vs-2:
ties.

Therefore:

for:
the:
specific:
frozen:
fault:
families,

its:
primary:
outcomes
match:
QUORUM3_OF_4.

This:
does NOT:
show:

2-of-4
and:
3-of-4

are:
generally:
equivalent.

It shows:

the:
current:
fault:
geometry

creates:

4-0,
3-1,
2-2,
or:
1-3:
vote:
patterns

where:
the:
unique-largest:
tie:
rule
already:
blocks:
2-2.

CAPACITY COST

DG-1R-05E:

32:
logical:
data bits

inside:

128:
physical:
bits.

DG-1R-05C/D:

48:
logical bits.

DG-1R-05A/B:

64:
logical bits.

Therefore:

the:
strong:
quorum:
fault tolerance

uses:

50%:
less:
logical:
capacity

than:
the:
64-bit:
local-code:
architecture.

The:
next:
research question

should NOT:
be:

"How many more witnesses
can:
we:
add?"

It should be:

"How much:
fault tolerance
can:
we:
obtain

per:
redundancy:
bit?"

CORE MECHANISTIC CONCLUSION

The:
software-tissue:
line

now:
supports
a:
layered:
integrity:
architecture:

1.
local:
state
can:
carry:
redundant:
repair:
information;

2.
neighbors
can:
reconstruct:
a:
damaged:
region;

3.
neighbors
can:
diagnose:
damage
that:
the:
region
cannot:
see;

4.
spatial:
witness:
quorums
can:
tolerate:
damage
to:
the:
repair:
network
itself;

5.
correlated:
faults
still:
define:
a:
quorum:
failure:
boundary.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05F —
SPARSE:
INTEGRITY:
GRAPH /
FAULT-TOLERANCE-PER-BIT:
AUDIT.

Goal:

recover:
more:
logical:
capacity

without:
falling:
all:
the:
way
back
to:
fragile:
two-witness:
repair.

Candidate architecture:

12:
logical:
blocks

x:
4:
data bits

=
48:
logical:
bits.

Do NOT:
use:
full:
local:
Hamming
plus:
four:
witnesses.

Instead:

store:
a:
sparse:
graph
of:
cross-block:
XOR:
constraints

inside:
the:
remaining:

80:
physical:
bits.

20:
4-bit:
integrity:
edges

over:
12:
logical:
regions.

Average:
graph degree:

3.33.

Compare:

- 48-bit:
  sparse:
  integrity:
  graph;
- 48-bit:
  two-witness:
  DG-1R-05C-style:
  tissue;
- 32-bit:
  four-witness:
  DG-1R-05E:
  quorum.

Measure:

repair:
success

per:

redundancy bit,

logical:
capacity,

fault:
class,

and:
correlated:
witness:
damage.

PLAIN-SPEAK SUMMARY

The:
repair quorum
worked.

With:
four:
witnesses,

one:
bad:
witness
does not:
matter.

Three:
healthy:
witnesses
still:
agree
on:
the:
right:
repair.

If:
two:
witnesses
are:
damaged
in:
the:
same:
way,

the:
votes
split:

two:
correct,
two:
wrong.

The:
system
does:
the:
safe:
thing:

nothing.

It:
refuses:
to:
guess.

That:
fixed:
the:
exact:
failure
we:
found
with:
two-neighbor:
repair.

But:
if:
three:
witnesses
are:
all:
damaged
the:
same:
way,

the:
quorum
can:
still:
be:
fooled.

So:
we:
now:
know
the:
fault:
boundary
very:
cleanly.

The:
problem
is:
cost.

To:
get:
four:
witnesses
inside:
the:
same:
128:
bits,

we:
reduced:
usable:
logical:
state
to:
32:
bits.

That:
is:
too:
expensive
to:
accept
without:
trying:
to:
do:
better.

The:
next:
experiment
will:
ask:

can:
we:
wire:
the:
integrity:
network
more:
cleverly

so:
the:
same:
repair:
strength

uses:
fewer:
backup:
bits?

That:
moves:
the:
research
from:

"Can:
software tissue
self-repair?"

toward:

"How:
efficiently
can:
software tissue
self-repair?"

DG-1R-05:
canonical frozen primary remains:

UNSPENT.

DG-1R-05E remains:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
