TITLE: DG-1R-07 — Repair Redundancy Compression / Stripe-Count Floor Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE RESOURCE-PRESSURE PILOT
TRACK: DG-1R / SOFTWARE CELLS / DISTRIBUTED SELF-REPAIR / REDUNDANCY EFFICIENCY
BRANCH: dg1a-ar
PARENT: DG-1R-06
PARENT_CLOSURE: 5466b5f0e7ab1fa85d5a4dfb3539fe8751162d94

PURPOSE

DG-1R-06 achieved:

100%:
exact:
counterfactual:
recovery

for:
all:
tested:
SMALL3
and:
LARGE5:
burst lesions

using:

64:
dynamic:
worker bits

+
64:
maintenance:
bits.

The next question is:

HOW:
MUCH:
REDUNDANT:
MAINTENANCE:
STATE

IS:
ACTUALLY:
NECESSARY?

DG-1R-07 compresses:

the:
maintenance:
budget

while:

holding:
worker capacity
fixed
at:

64:
dynamic bits.

BOUNDARY

Synthetic software-only experiment.

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

TOTAL STATE ENVELOPE

128:
persistent:
bit:
maximum.

Every method:

64:
dynamic:
worker bits.

Unused:
state positions

remain:

zero /
inactive

and:
are:
reported
as:

RECLAIMABLE:
BUDGET.

WORKER DYNAMICS

Exact:
DG-1R-06:
64-cell:
MIXED5:
worker ring.

One:
CA update
per:
external:
input.

Input:

scalar:
binary.

Input mapping:

4:
world-specific:
positions

inside:
odd:
8-cell:
worker compartments:

1,
3,
5,
7.

Damage:

even:
8-cell:
worker compartments:

0,
2,
4,
6.

Thus:

input /
damage:
separation
remains:
frozen.

METHODS

1.
FULL16_SECDED64

Reference:
DG-1R-06:
striped:
extended-Hamming:
architecture.

16:
striped:
groups.

Group j workers:

j,
j+16,
j+32,
j+48.

4:
maintenance bits
per:
group.

64:
maintenance bits.

Total used:

128 bits.

Reclaimable:

0.

2.
G8_HAMMING32

8:
striped:
groups.

Group j:

all:
worker indices
where:

index mod 8
=
j.

8:
worker bits
per:
group.

Standard:
single-error-correcting:
Hamming:

4:
parity bits
per:
group.

Maintenance:

32 bits.

Total used:

96 bits.

Reclaimable:

32 bits.

3.
G5_HAMMING25

5:
striped:
groups.

Group j:

all:
worker indices
where:

index mod 5
=
j.

Group sizes:

13,
13,
13,
13,
12.

Use:

5:
Hamming:
parity bits
per:
group.

Maintenance:

25 bits.

Total used:

89 bits.

Reclaimable:

39 bits.

4.
G4_HAMMING20

4:
striped:
groups.

Group j:

all:
worker indices
where:

index mod 4
=
j.

16:
workers
per:
group.

Use:

5:
Hamming:
parity bits
per:
group.

Maintenance:

20 bits.

Total used:

84 bits.

Reclaimable:

44 bits.

5.
BASE64_INERT64

64:
workers.

0:
active:
maintenance bits.

64:
inert:
bits.

Purpose:

no-repair:
reference.

GENERAL HAMMING ENCODING

For:
G8,
G5,
G4:

parity positions
inside:
each:
codeword:

powers:
of:
two:

1,
2,
4,
8

and:
16
where:
required.

Worker data bits
occupy:

all:
non-power-of-two:
codeword positions.

Parity:

even.

Before:
each:
worker update:

compute:
the:
Hamming:
syndrome.

If:

syndrome = 0:

no correction.

If:

syndrome
points:
inside:
the:
codeword:

flip:
that:
single:
codeword:
position.

Then:

apply:
input overwrite.

Then:

evolve:
worker ring.

Then:

recompute:
all:
maintenance:
parity.

IMPORTANT

Standard Hamming:

corrects:
one:
bit:
per:
codeword

but:
does NOT:
reliably:
identify:
multi-bit:
errors.

Therefore:

G4
is:
a:
deliberate:
resource-floor:
stress case.

BURST GEOMETRY

SMALL3:

3:
consecutive:
worker flips.

LARGE5:

5:
consecutive:
worker flips.

Because:

G8:
uses:
index mod 8,

any:
tested:
length <=5:
burst

hits:
distinct:
groups.

Because:

G5:
uses:
index mod 5,

any:
tested:
length <=5:
burst

hits:
each:
group

at most:
once.

Because:

G4:
uses:
index mod 4,

a:
5-cell:
burst

must:
hit:
at least:
one:
group
twice.

Thus:

G5:

is:
the:
smallest:
tested:
stripe count

whose:
geometry
can:
convert:
a:
5-cell:
burst

into:
only:
single-error:
codewords.

This:
geometric fact

is:
pre-registered.

It is NOT:
a:
post-run:
interpretation.

DAMAGE PROTOCOL

Exact:
DG-1R-06.

Pre-damage:

1024:
external:
steps.

Damage:

after:
step:
1023

before:
input:
1024.

Lesion compartments:

0,
2,
4,
6.

SMALL3 offsets:

2,
3,
4.

LARGE5 offsets:

1,
2,
3,
4,
5.

Damage:

workers only.

Maintenance bits:

not:
directly:
flipped.

Post-damage:

32:
external:
steps.

HORIZONS

1,
4,
8,
16,
32.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260926070000
through:
20260926070007.

No:
prior:
DG-1R:
seed reuse.

PRIMARY METRICS

Per:
method /
lesion size:

- h1:
  exact-worker:
  recovery rate;

- h1:
  exact-full-state:
  recovery rate;

- h32:
  exact-full-state:
  recovery rate;

- worker:
  divergence area;

- lesion:
  recovery;

- outside-lesion:
  worker divergence;

- syndrome:
  correction count;

- parity:
  bit:
  budget;

- total:
  used:
  state bits;

- reclaimable:
  state bits;

- maintenance:
  reduction
  versus:
  FULL16_SECDED64.

ORACLE DAMAGE-LOAD TELEMETRY

For:
each:
damage scenario:

compute:

number:
of:
damaged:
worker bits
belonging:
to:
each:
code group.

Report:

max:
damaged bits
in:
one:
code group.

This:
oracle:

is:
telemetry only.

It is:
NOT:
available
to:
the:
repair:
algorithm.

NO-DAMAGE CONTROL

Duplicate:
undamaged:
clones

must:
remain:
bit-exact.

ENCODING CONTROL

Before:
damage:

all:
active:
Hamming:
groups

must:
have:

syndrome:

0

at:
normal:
step boundaries.

PRIMARY CLASSIFICATIONS

G8_COMPRESSED_REPAIR

TRUE
if:

G8_HAMMING32

has:

SMALL3:
h1:
exact-full recovery
>=0.95

AND:

LARGE5:
h1:
exact-full recovery
>=0.95

AND:

combined:
h32:
exact-full recovery
>=0.95.

G5_COMPRESSED_REPAIR

same:
criteria
for:

G5_HAMMING25.

G4_COMPRESSED_REPAIR

same:
criteria
for:

G4_HAMMING20.

RESOURCE_FLOOR_SIGNAL

TRUE
if:

G5_COMPRESSED_REPAIR:

TRUE

AND:

G4_COMPRESSED_REPAIR:

FALSE.

STRONG REDUNDANCY COMPRESSION

TRUE
if:

G5_COMPRESSED_REPAIR:

TRUE

AND:

no-damage control:

PASS

AND:

encoding control:

PASS

AND:

G5:

reclaims:
at least:
35:
of:
the:
128:
state bits.

REFERENCE PRESERVATION

FULL16_SECDED64

must:
retain:

>=0.95:
h1:
exact-full:
recovery

for:
SMALL3
and:
LARGE5.

If:
reference:
fails:

experiment:

MECHANICALLY INVALID.

INTERPRETATION GUARDRAIL

A:
G5:
positive:
result

would NOT:
show:

emergent:
coding.

It would show:

the:
DG-1R-06:
self-repair:
principle

does NOT:
require:
50%:
permanent:
maintenance:
overhead

for:
this:
damage family.

It would:
bound:

the:
maintenance:
cost

much:
closer
to:
the:
burst:
geometry.

NEXT

If:
RESOURCE_FLOOR_SIGNAL:

proceed:
to:

DG-1R-08 —
RECLAIMED:
STATE:
REDEPLOYMENT.

Take:

the:
39:
bits
freed:
by:
G5

and:
test:

can:
they:
become:
additional:
workers /
specialized:
cells

without:
sacrificing:
the:
repair:
guarantee?

If:
G4:
also:
passes:

continue:
compressing:
stripe count.

If:
G5:
fails:

the:
simple:
geometric:
one-error-per-stripe:
argument

is:
insufficient
under:
the:
full:
dynamics

and:
the:
repair:
timing /
code:
implementation
must:
be:
audited.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
last:
experiment
proved:
we:
can:
make:
the:
software organism
repair:
a:
five-cell:
injury
perfectly.

But:
we:
used:
half:
the:
128-bit:
body
for:
repair:
information.

That:
is:
expensive.

So:
now:
we:
compress:
the:
repair:
system.

First:

64:
repair bits.

Then:

32.

Then:

25.

Then:

20.

The:
important:
idea
is:

a:
five-cell:
injury

needs:
at least:
five:
independent:
places
to:
spread:
those:
five:
errors

if:
each:
repair:
group
can:
fix:
only:
one.

Five:
stripes
should:
be:
enough.

Four:
should:
not.

If:
that:
holds,

we:
can:
free:

39:
of:
the:
original:
128:
state bits

while:
keeping:
perfect:
repair
for:
the:
damage
we:
tested.

Those:
39:
bits
could:
later:
go:
back
to:
computation,
memory,
or:
new:
cell roles.

canonical_scientific_execution = false.
stab18_r1_touched = false.
