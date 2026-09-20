TITLE: DG-1R-07 — Regional Interleaved SECDED / Burst-Damage Repair Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE BURST-SELF-REPAIR PILOT
TRACK: DG-1R / SOFTWARE CELLS / SPATIAL DEVELOPMENTAL REDUNDANCY
BRANCH: dg1a-ar
PARENT: DG-1R-06
PARENT_CLOSURE: 973e1e0f828b4a686cdc059d5cf32e71468ec171

PURPOSE

DG-1R-06 established:

- exact counterfactual reconstruction for correctable one-bit damage;
- local redundant information is sufficient to turn nanite containment
  into correct repair;
- contiguous multi-bit damage can overload one SECDED codeword;
- one-step quarantine does not solve that problem.

DG-1R-07 asks:

CAN:
THE:
SAME:
SECDED:
REDUNDANCY

REPAIR:
PHYSICALLY:
CLUSTERED:
DAMAGE

IF:

THE:
ORGANISM'S:
LOGICAL:
CODEWORDS

ARE:
SPATIALLY:
INTERLEAVED?

CORE HYPOTHESIS

A:
physical:
damage burst

is:
hard
when:

many:
adjacent:
damaged cells

belong:
to:
one:
logical:
codeword.

Interleaving:

reorders:
logical:
codeword:
bits

so:

adjacent:
physical:
cells

belong:
to:
different:
logical:
codewords.

Then:

one:
physical:
multi-cell:
injury

may become:

many:
independent:
single-bit:
codeword:
errors

that:

the:
existing:
SECDED:
nanites

can:
repair:
exactly.

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

TOTAL STATE BUDGET

128:
persistent:
bits.

Unchanged from:
DG-1R-06.

Logical structure:

16:
SECDED(8,4):
codewords.

Each:

4:
logical:
data bits.

3:
Hamming:
parity bits.

1:
overall-parity /
nanite:
check bit.

Total:

64:
logical:
data bits.

64:
redundancy /
nanite:
bits.

No:
additional:
persistent:
state.

LOGICAL CODE

Exact:
DG-1R-06:
extended:
Hamming:
SECDED:
equations
and:
decoder.

No:
decoder:
change.

No:
correction:
threshold:
change.

No:
new:
error:
code.

Only:

logical-to-physical:
placement
changes.

LAYOUT A — CONTIGUOUS

Logical:
codeword w

occupies:

physical:
positions:

8*w
through:
8*w+7.

Exact:
DG-1R-06:
placement.

LAYOUT B — INTERLEAVE8

Divide:
the:
128-cell:
organism

into:

two:
64-cell:
REGIONS.

Region 0:

logical:
codewords:
0..7.

Region 1:

logical:
codewords:
8..15.

Within:
each:
64-cell:
region:

for:
logical:
codeword:
c
in:
0..7

and:
codeword-bit:
j
in:
0..7:

physical_offset
=
8*j
+
c.

Thus:

the:
first:
8:
physical:
cells

contain:

bit 1
from:
8:
different:
codewords.

The:
next:
8
contain:

bit 2
from:
those:
same:
8:
codewords.

And so on.

BURST PROPERTY

Within:
one:
64-cell:
region,

any:
contiguous:
physical:
burst

of:
length:

<=8

that:
does NOT:
cross:
the:
64-cell:
region boundary

affects:

at most:

one:
bit

of:
each:
logical:
codeword.

Therefore:

under:
the:
frozen:
single-error:
SECDED:
repair model,

BURST3,
BURST5,
and:
BURST8

are:
structurally:
convertible

into:

separate:
single-bit:
codeword:
errors.

BURST9:

exceeds:
the:
interleave depth

and:
is:
included
as:
a:
stress-boundary:
case.

REGIONAL LOCALITY COST

CONTIGUOUS:
codeword:
repair span:

8:
physical:
cells.

INTERLEAVE8:
codeword:
bits
span:

up to:
57:
physical:
positions

inside:
one:
64-cell:
region.

Therefore:

DG-1R-07:

tests:
REGIONAL:
repair,
not:
strict:
8-cell:
local:
repair.

This:
cost
must:
be:
reported.

Future:
work
may:
trade:
burst:
capacity
against:
repair:
radius.

LOGICAL DATA DYNAMICS

The:
64:
logical:
data bits

form:
one:
periodic:
data ring.

Exact:
DG-1R-06:
world-specific:
MIXED5:
rules:

90,
150,
110,
22,
30.

The:
logical:
data:
trajectory

must:
be:
independent
of:
physical:
layout

in:
the:
absence:
of:
damage.

At:
each:
healthy:
external:
step:

1.
perform:
layout-specific:
SECDED:
pre-step:
repair
where:
enabled;

2.
overwrite:
the:
same:
8:
LOGICAL:
input-mapped:
data:
identities

with:
u_t;

3.
evolve:
the:
same:
64-bit:
logical:
data ring
once;

4.
encode:
the:
same:
16:
logical:
SECDED:
codewords;

5.
place:
those:
codeword bits
according:
to:
the:
method's:
physical:
layout.

INPUT MAPPING

Choose:

8:
logical:
data:
indices.

The:
64:
logical:
data:
ring

is:
partitioned
into:

8:
8-data:
input compartments.

Choose:
one:
world-specific:
logical:
data index
from:
each:
compartment.

The:
same:
logical:
input identities

are:
used
for:

CONTIGUOUS
and:
INTERLEAVE8.

Only:
their:
physical:
positions
differ.

METHODS

1.
CONTIG_PASSIVE

CONTIGUOUS:
layout.

No:
pre-step:
SECDED:
correction.

Healthy:
re-encoding:
still:
occurs.

2.
CONTIG_SECDED

CONTIGUOUS:
layout.

Frozen:
DG-1R-06:
SECDED:
single-error:
correction.

3.
INTERLEAVE8_PASSIVE

INTERLEAVE8:
layout.

No:
pre-step:
SECDED:
correction.

4.
INTERLEAVE8_SECDED

INTERLEAVE8:
layout.

Frozen:
DG-1R-06:
SECDED:
single-error:
correction.

No:
quarantine.

Reason:

DG-1R-06:
quarantine
did:
not:
receive:
support.

HEALTHY CROSS-LAYOUT CONTROL

After:

1024:
healthy:
external:
steps,

extract:

the:
64:
logical:
data bits

from:

CONTIG_SECDED
and:
INTERLEAVE8_SECDED.

Required:

exact:
logical:
data equality.

Also:

decode:
all:
codewords.

Required:

all:
healthy:
syndromes:
zero.

This proves:

layout:
placement

does NOT:
change:
healthy:
logical:
dynamics.

DAMAGE TIME

After:

1024:
healthy:
external:
steps.

Clone:

REFERENCE:
undamaged.

DAMAGED:
burst-lesioned.

Continue:

32:
future:
external:
inputs

identically.

PHYSICAL BURST FAMILIES

BURST3:
3:
physically:
adjacent:
bits.

BURST5:
5:
physically:
adjacent:
bits.

BURST8:
8:
physically:
adjacent:
bits.

BURST9:
9:
physically:
adjacent:
bits.

No:
wrap:
across:
a:
64-cell:
region:
boundary.

BURST LOCATION SELECTION

For:
each:
world /
burst:
length:

consider:
all:
possible:
contiguous:
burst starts

inside:
each:
64-cell:
region

that:

1.
do NOT:
cross:
the:
region:
boundary;

2.
do NOT:
overlap:
ANY:
physical:
input-mapped:
cell

under:

CONTIGUOUS
OR:
INTERLEAVE8:
layout.

From:
the:
valid:
starts:

select:
two:
starts
per:
64-cell:
region

using:
a:
dedicated:
world-specific:
damage RNG.

Thus:

4:
physical:
burst locations

per:
burst:
length /
world.

The:
same:
physical:
burst positions

are:
applied
to:
all:
four:
methods.

SCENARIOS

4:
burst:
families

x:

4:
physical:
locations

=

16:
damage:
scenarios
per:
method /
world.

Across:
8:
worlds:

128:
scenarios
per:
method.

PRIMARY METRICS

At:

h1,
h4,
h8,
h16,
h32:

WHOLE_PHYSICAL_DIVERGENCE.

LOGICAL_DATA_DIVERGENCE.

OUTSIDE_PHYSICAL_BURST_DIVERGENCE.

DAMAGED_CODEWORD_COUNT.

MISCORRECTED_CODEWORD_COUNT.

EXACT_FULL_STATE_MATCH.

EXACT_LOGICAL_DATA_MATCH.

Also:

EXCESS_LOGICAL_DATA_DIVERGENCE_AREA.

EXCESS_WHOLE_DIVERGENCE_AREA.

SUSTAINED_FULL_RECOVERY.

SUSTAINED_LOGICAL_DATA_RECOVERY.

RECOVERY_TIME_FULL.

RECOVERY_TIME_DATA.

ECC TELEMETRY

Per:
scenario:

- single-error:
  corrections;
- corrections:
  on:
  originally:
  damaged:
  physical:
  cells;
- corrections:
  outside:
  original:
  burst;
- double-error:
  detections;
- nonzero:
  syndrome:
  events.

LAYOUT LOAD TELEMETRY

At:
damage time,
before:
repair:

report:

number:
of:
damaged:
logical:
codewords.

For:
each:
damaged:
codeword:

report:
error count.

Summaries:

- max:
  errors:
  in:
  any:
  one:
  codeword;
- number:
  of:
  codewords
  with:
  exactly:
  one:
  error;
- number:
  of:
  codewords
  with:
  two-or-more:
  errors.

This:
directly:
tests:
whether:
interleaving
performed:
the:
intended:
burst-to-single-error:
transformation.

FROZEN PRIMARY SIGNALS

BURST5_EXACT_REPAIR

TRUE
if:

INTERLEAVE8_SECDED
on:
BURST5:

1.
h1:
median:
LOGICAL_DATA_DIVERGENCE
=
0;

2.
h1:
median:
WHOLE_PHYSICAL_DIVERGENCE
=
0;

3.
SUSTAINED_FULL_RECOVERY rate
>=0.95;

4.
median:
max errors per codeword
at:
damage time
=
1;

5.
median:
corrections outside original burst
=
0.

BURST8_EXACT_REPAIR

Same:
criteria

for:
BURST8.

INTERLEAVING_ADVANTAGE

TRUE
if:

for:
BURST5:

INTERLEAVE8_SECDED

versus:

CONTIG_SECDED

has:

1.
at least:
90%:
lower:
median:
EXCESS_LOGICAL_DATA_DIVERGENCE_AREA;

AND:

2.
at least:
0.75:
higher:
SUSTAINED_FULL_RECOVERY rate.

PASSIVE_LAYOUT_CONTROL

INTERLEAVE8_PASSIVE

must NOT:
be:
classified
as:
repair

merely:
because:
physical:
placement
changed.

Report:

its:
burst:
metrics
separately.

If:

INTERLEAVE8_PASSIVE
also:
improves:

that:
is:
a:
placement /
damage-propagation:
effect

distinct:
from:

SECDED:
reconstruction.

BURST9 BOUNDARY

BURST9:

is:
outside:
the:
8-way:
single-error-per-codeword:
guarantee.

No:
exact:
repair
is:
required.

Report:

- exact:
  recovery rate;
- max:
  errors per codeword;
- miscorrection:
  rate;
- divergence:
  area.

BURST9_SAFE

TRUE
if:

INTERLEAVE8_SECDED
does NOT:

increase:
median:
EXCESS_LOGICAL_DATA_DIVERGENCE_AREA

by:
more than:
10%

relative:
to:

INTERLEAVE8_PASSIVE.

FULL_INTERLEAVED_BURST_REPAIR_SIGNAL

TRUE
if:

BURST5_EXACT_REPAIR

AND:

BURST8_EXACT_REPAIR

AND:

INTERLEAVING_ADVANTAGE.

IMPORTANT

A:
positive:
DG-1R-07

would NOT:
mean:

arbitrary:
large:
injury
is:
solved.

It would mean:

DEVELOPMENTAL:
PHYSICAL:
ORGANIZATION

can:
transform:
a:
local:
burst:
fault

into:

a:
set:
of:
small:
independent:
faults

that:
existing:
local:
repair:
logic
can:
solve.

This is:

the:
first:
direct:
test

that:

WHERE:
the:
organism
places:
redundant:
state

can:
matter
as much
as:

HOW MUCH:
redundancy
it:
stores.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-07:
primary:
burst:

do not alter:

- SECDED equations;
- interleave depth;
- 64-cell regional boundaries;
- logical data dynamics;
- logical input mapping;
- burst lengths;
- burst-location selection;
- future-input protocol;
- metrics;
- thresholds;
- world family.

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

REPRODUCIBILITY

Two:
complete:
8-world:
canonical:
sweeps.

Canonical:
SHA-256
must:
match:
exactly.

Runtime:
sidecar:
non-canonical.

NEXT

If:
FULL_INTERLEAVED_BURST_REPAIR_SIGNAL:

test:

smaller:
interleave:
depths /
repair:
radii

to:
find:

the:
minimum:
regional:
communication
required
for:
robust:
burst:
repair.

If:
BURST5 works
but:
BURST8 fails:

characterize:
the:
practical:
burst:
radius
below:
the:
theoretical:
placement:
bound.

If:
interleaving:
does NOT:
improve:
burst:
repair:

the:
logical-to-physical:
placement
or:
repair:
timing

is:
not:
providing:
the:
expected:
fault:
dispersion

and:
must:
be:
audited.

PLAIN-SPEAK PRE-REGISTERED QUESTION

We:
proved:
the:
nanite
can:
perfectly:
repair:
one:
broken:
bit

when:
its:
local:
blueprint
has:
enough:
information.

The:
problem
is:
that:
a:
physical:
injury
usually:
breaks:
several:
neighboring:
cells.

Right now:

neighboring:
cells
also:
belong
to:
the:
same:
blueprint.

So:

one:
small:
injury
can:
overwhelm:
one:
nanite's:
repair:
code.

This:
experiment
rearranges:
the:
organism.

We:
spread:
the:
pieces
of:
each:
blueprint
through:
a:
64-cell:
region.

Now:

five:
adjacent:
physical:
breaks

should:
hit:

five:
different:
logical:
blueprints

once:
each,

instead:
of:

one:
blueprint
five:
times.

That:
turns:
one:
hard:
five-bit:
repair

into:

five:
easy:
one-bit:
repairs

running:
in:
parallel.

We:
are:
not:
adding:
cells.

We:
are:
not:
adding:
memory.

We:
are:
changing:

WHERE:
the:
redundant:
information
lives.

canonical_scientific_execution = false.
stab18_r1_touched = false.
