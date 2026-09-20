TITLE: DG-1R-05G — Compressed Hypergraph Integrity / Multi-Region Witness Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE COMPRESSED-INTEGRITY PILOT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / REPAIR CAPACITY
BRANCH: dg1a-ar
PARENT: DG-1R-05F

RATIONALE

DG-1R-05F established:

- 48 logical bits can coexist with strong sparse integrity under a 128-bit total state budget;
- pairwise SPARSE20 uses 20 four-bit edge-check slots = 80 integrity bits;
- pairwise checks provide 40 total graph-degree / witness-incidence units;
- degree 3 tolerates one bad witness but fails under two correlated bad witnesses;
- selected degree 4 regions safely abstain under two correct versus two wrong witnesses;
- uniform degree 4 is impossible with only 20 pairwise edges.

Before adding time-multiplexed topology, DG-1R-05G tests a lower-complexity question:

CAN:
ONE:
FOUR-BIT:
INTEGRITY SLOT

WITNESS:
MORE:
THAN:
TWO:
LOGICAL:
REGIONS

WITHOUT:
ADDING:
PERSISTENT:
STATE?

A four-region XOR check:

C_abcd
=
A XOR B XOR C XOR D

can reconstruct any one member if the other three logical regions and the check are intact.

Thus:

20:
four-bit:
hyperchecks

x:
4:
incident:
logical regions

=

80:
witness-incidence units

instead of:

40

for:
20:
pairwise:
edges.

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

STATE BUDGET

Logical data:

12:
blocks

x:
4 bits

=

48 bits.

Integrity:

20:
slots

x:
4 bits

=

80 bits.

Total:

128 persistent bits.

No:
hidden:
memory.

No:
task labels.

No:
external repair oracle.

REFERENCE METHOD

PAIR20_MAJORITY_48

Exact:
DG-1R-05F:
SPARSE20:
pairwise:
integrity graph.

Edges:

12-cycle.

6:
opposite-node:
matching:
edges.

2:
extra:
edges:

(0,3)
and:
(6,9).

Repair:

strict:
majority
of:
incident:
pairwise:
reconstruction candidates.

Purpose:

same-capacity:
pairwise:
reference.

HYPERGRAPH

HYPER20_MAJORITY_48.

Frozen:
20:
four-region:
hyperchecks:

(0,2,7,9)
(1,3,6,11)
(4,5,9,10)
(2,3,5,8)
(0,1,4,8)
(6,7,8,10)
(2,4,6,11)
(0,3,5,7)
(1,7,10,11)
(1,5,6,9)
(3,8,9,10)
(0,4,8,11)
(0,2,6,10)
(1,3,4,7)
(2,5,7,11)
(2,3,4,10)
(0,1,5,10)
(0,3,9,11)
(1,2,8,9)
(4,6,7,9)

Frozen properties:

logical-region degree:

block 0: 7
block 1: 7
block 2: 7
block 3: 7
block 4: 7
block 5: 6
block 6: 6
block 7: 7
block 8: 6
block 9: 7
block 10: 7
block 11: 6

Minimum degree:

6.

Maximum degree:

7.

Every:
pair:
of:
logical regions

co-occurs
in:
at most:

2:
hyperchecks.

Total:
witness incidence:

80.

HYPERCHECK ENCODING

For:
hypercheck:
H=(a,b,c,d):

stored:
four-bit:
check:

X_a
XOR:
X_b
XOR:
X_c
XOR:
X_d.

To reconstruct:
target:
b:

candidate
=
stored_check
XOR:
X_a
XOR:
X_c
XOR:
X_d.

Same:
for:
any:
member.

REPAIR RULE

For:
each:
logical:
block:

compute:
all:
incident:
candidate:
vectors.

Group:
identical:
four-bit:
candidates.

Require:

strict majority:

best_count
>
degree / 2.

If:
no:
strict:
majority:

ABSTAIN.

If:
strict:
majority
exists
and:
candidate
differs
from:
current:
logical:
block:

repair:
to:
candidate.

No:
task:
information.

No:
counterfactual:
information
is:
visible:
to:
repair logic.

METHODS

1.
PAIR20_MAJORITY_48.

2.
HYPER20_MAJORITY_48.

3.
HYPER20_UNANIMOUS_48.

Same:
hypergraph.

Repair only if:

all:
incident:
candidates
agree.

Purpose:

high-confidence:
negative /
conservative:
control.

4.
HYPER20_DETECT_ONLY.

Compute:
candidate:
groups
and:
majorities.

Perform:
no:
repair.

Purpose:

representation-only:
control.

DYNAMICS

48:
logical:
data bits

under:

one:
MIXED5:
CA update

per:
external:
input.

Exact:
DG-1R-05F:
input /
dynamics:
style.

Input-mapped:
logical:
blocks:

1,
4,
7,
10.

Pre-damage:

1024:
external:
steps.

Post-damage:

32:
steps.

Repair occurs:

before:
current:
input overwrite
and:
logical:
CA:
update.

After:
logical:
update:

all:
20:
integrity:
slots

are:
recomputed
from:
the:
new:
logical:
state.

WORLD FAMILY

8:
worlds.

Seeds:

20260926057000
through:
20260926057007.

No:
prior:
DG-1R:
seed reuse.

DAMAGE TARGETS

Degree-6 hypergraph target:

block 5.

Degree-7 hypergraph target:

block 2.

Pairwise:
reference target for:
degree-3 comparison:

block 2.

Pairwise:
reference target for:
degree-4 comparison:

block 3.

Harness MUST:
assert:

method-specific:
target degree

before:
scenario:
execution.

DAMAGE FAMILIES

LOCAL_DATA2_D6

Hypergraph:

block 5.

Flip:
logical data bits:

0,
1.

Pair reference:

block 2.

Flip:
logical data bits:

0,
1.

Purpose:

ordinary:
local:
repair.

CHECK2_CORRELATED_D6

No:
logical data:
damage.

Flip:
bit 0

in:
two:
incident:
integrity slots

for:
the:
target:
block.

Hypergraph:

degree 6:
block 5.

Pair reference:

degree 3:
block 2.

Purpose:

can:
healthy:
logical state
resist:
two:
correlated:
bad:
witnesses?

CHECK3_CORRELATED_D6

No:
logical data:
damage.

Flip:
bit 0

in:
three:
incident:
hyperchecks

for:
degree-6:
block 5.

Hypergraph only.

Expected:
3 correct
versus:
3 wrong.

Strict majority:

NONE.

Purpose:

safe:
tie /
abstention:
boundary.

CHECK4_CORRELATED_D6

No:
logical:
damage.

Flip:
bit 0
in:
four:
incident:
hyperchecks

for:
degree-6:
block 5.

Hypergraph only.

Expected:

4 wrong
versus:
2 correct.

Purpose:

frozen:
correlated:
majority:
failure:
boundary.

DATA2_PLUS_CHECK2_D6

Flip:

logical:
data:
bits:
0,
1

in:
degree-6:
target

plus:

bit 0
in:
two:
incident:
integrity:
slots.

Hypergraph:

block 5.

Pair reference:

degree-3:
block 2.

Purpose:

can:
hypergraph:
majority
reconstruct:
damaged:
local:
state

despite:
two:
bad:
integrity:
witnesses?

DATA2_PLUS_CHECK3_D7

Flip:

logical:
data:
bits:
0,
1

in:
degree-7:
target:
block 2

plus:

bit 0
in:
three:
incident:
hyperchecks.

Pair reference:

degree-4:
block 3

with:

logical:
bits:
0,
1

plus:

bit 0
in:
three:
incident:
pairwise:
checks.

Purpose:

test:
4-correct:
versus:
3-wrong:
hypergraph:
majority

against:
the:
pairwise:
degree-4:
limit.

CHECK4_CORRELATED_D7

No:
logical:
data:
damage.

Flip:
bit 0

in:
four:
incident:
hyperchecks

for:
degree-7:
block 2.

Expected:

4 wrong
versus:
3 correct.

Purpose:

degree-7:
correlated-majority:
failure:
boundary.

DISTRIBUTED_LOCAL_DATA2

Flip:
logical:
bits:
0,
1

in:

block 2
and:
block 8.

No:
integrity:
slot:
damage.

Purpose:

parallel:
repair.

LESION ASSERTIONS

Every:
scenario

must:
assert:

- exact:
  logical-data:
  flip count;
- exact:
  integrity-bit:
  flip count;
- unique:
  physical:
  lesion:
  positions;
- no:
  lesion:
  position
  overlaps:
  an:
  input-mapped:
  physical:
  logical:
  bit.

COUNTERFACTUAL METRICS

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
- repairs;
- false repairs;
- abstentions;
- candidate-group size;
- winning-vote count.

FALSE REPAIR

A:
proposed:
logical:
repair

is:
FALSE

if:

the:
proposal

does NOT:
match:

the:
undamaged:
counterfactual:
logical:
block

immediately:
before:
repair.

Repair logic:

never:
sees:
this:
label.

PRIMARY SIGNALS

HYPERGRAPH_CAPACITY_SIGNAL

TRUE
if:

HYPER20_MAJORITY_48

on:
DATA2_PLUS_CHECK2_D6:

1.
median:
logical divergence
at:
h1
=
0;

2.
logical divergence area median
=
0;

3.
sustained exact logical recovery
>=0.90;

4.
false repair fraction
<=0.01;

AND:

PAIR20_MAJORITY_48

fails:
at least:
one:
of:
those:
criteria

on:
its:
paired:
degree-3:
scenario.

THREE-WITNESS-TOLERANCE SIGNAL

TRUE
if:

HYPER20_MAJORITY_48

on:
DATA2_PLUS_CHECK3_D7:

median:
logical divergence
at:
h1
=
0

AND:

sustained:
exact:
logical:
recovery
>=0.90

AND:

false repair fraction
<=0.01.

TIE-SAFETY SIGNAL

TRUE
if:

HYPER20_MAJORITY_48

on:
CHECK3_CORRELATED_D6:

repairs
=
0

AND:

false repairs
=
0

AND:

median:
logical divergence
at:
h4
=
0.

CORRELATED-FAULT BOUNDARY

Expected:

CHECK4_CORRELATED_D6

and/or:

CHECK4_CORRELATED_D7

may:
create:
a:
wrong:
strict:
majority.

Report:

false-repair:
fraction

and:
logical:
divergence.

No:
positive:
safety:
claim
may:
be:
made
if:
the:
frozen:
result:
fails.

DISTRIBUTED HYPERGRAPH REPAIR SIGNAL

TRUE
if:

DISTRIBUTED_LOCAL_DATA2:

median:
logical divergence
at:
h4
=
0

AND:

sustained:
exact:
logical:
recovery
>=0.90

AND:

false repair fraction
<=0.01.

COMPRESSION ADVANTAGE

TRUE
if:

HYPER20_MAJORITY_48

shows:

HYPERGRAPH_CAPACITY_SIGNAL
=
TRUE

while:

using:

48:
logical bits.

80:
integrity bits.

128:
total:
persistent bits.

Same:
as:
PAIR20_MAJORITY_48.

IMPORTANT

A:
positive:
result

would NOT:
mean:

hypergraph:
majority
is:
the:
final:
Yggdrasil:
repair:
architecture.

It would show:

PAIRWISE:
INTEGRITY

is:
not:
the:
most:
capacity-efficient:
use

of:
the:
80:
integrity:
bits.

One:
integrity:
cell group

can:
serve:
multiple:
regions

simultaneously.

This:
is:
closer:
to:

compressed:
tissue-wide:
consistency

than:
isolated:
backup:
links.

RELATION TO TIME-MULTIPLEXING

DG-1R-05F proposed:

time-multiplexed:
integrity.

DG-1R-05G deliberately:
tests:
compressed:
static:
integrity
first

because:

if:
the:
same:
persistent:
80:
integrity bits

can:
provide:
substantially:
more:
simultaneous:
witness:
coverage

through:
higher-order:
checks,

then:

temporal:
rotation
may:
not:
be:
the:
next:
necessary:
complexity.

If:
hypergraph:
compression
still:
hits:
an:
insufficient:
correlated-fault:
boundary,

time /
adaptation
remains:
the:
next:
resource axis.

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
DG-1R-05G:
scenario:

do not alter:

- hyperedge set;
- pair reference;
- target blocks;
- repair rule;
- lesion geometry;
- thresholds;
- world family;
- metrics.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
last:
experiment
used:
80:
backup:
bits

as:
20:
links
between:
pairs:
of:
regions.

That:
means:
each:
backup:
link
helped:
two:
regions.

But:
one:
XOR:
check
does not:
have:
to:
cover:
only:
two:
regions.

This:
test
lets:
one:
backup:
slot
tie:
four:
regions
together.

Any:
one:
of:
those:
four
can:
be:
reconstructed

if:
the:
other:
three
and:
the:
check
are:
healthy.

So:

without:
adding:
a:
single:
persistent:
bit,

we:
double:
the:
total:
number:
of:
region-to-check:
relationships

from:
40
to:
80.

If:
that:
lets:
a:
region
survive:

two
or:
three:
bad:
witnesses

where:
the:
pairwise:
network
could not,

we:
learn:
that:
the:
important:
resource
is:
not:
just:
how:
many:
backup:
bits
we:
have.

It:
is:
how:
much:
independent:
integrity:
information
each:
backup:
bit
carries.

canonical_scientific_execution = false.
stab18_r1_touched = false.
