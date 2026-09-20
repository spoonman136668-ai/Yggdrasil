TITLE: DG-1R-05I — Local-Max Syndrome Message-Passing Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE DISTRIBUTED-DECODER PILOT
TRACK: DG-1R / SOFTWARE TISSUE / LOCAL REPAIR / MESSAGE PASSING
BRANCH: dg1a-ar
PARENT: DG-1R-05H

PURPOSE

DG-1R-05H established:

- HYPER20 representation contains enough information to repair two simultaneous damaged logical regions;
- global minimum-weight decoding repairs that distributed lesion exactly;
- bounded iterative GREEDY_SYNDROME also repairs it exactly;
- one syndrome-reduction decision per bit plane is insufficient;
- iterative repair is therefore a real mechanism;
- the remaining architectural weakness is centralized winner selection across all 12 logical regions.

DG-1R-05I asks:

CAN:
THE:
SAME:
SYNDROME-REDUCTION:
PRINCIPLE

BE:
IMPLEMENTED:

THROUGH:
LOCAL:
COMPETITION /
MESSAGE PASSING

WITHOUT:

A:
GLOBAL:
BEST-FAULT:
CONTROLLER?

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
DG-1R-05H:
HYPER20.

48:
logical bits.

80:
integrity bits.

128:
total:
persistent bits.

Exact:
20:
four-region:
hyperchecks.

Exact:
input mapping,
MIXED5 dynamics,
world split,
and:
damage families.

SYNDROME-REDUCTION SCORE

For:
logical:
block j
and:
bit plane k:

current:
syndrome weight:

W.

Hypothetical:
syndrome weight
after:
flipping:
logical:
bit:
(j,k):

W_j.

Local:
repair score:

R_j
=
W - W_j.

Because:

flipping:
logical block j

changes:
only:
its:
incident:
hyperchecks,

R_j

can:
be:
computed

from:
local:
incident:
syndrome messages.

Candidate:

R_j > 0.

METHOD 1 — GLOBAL_GREEDY

Exact:
DG-1R-05H:
GREEDY_SYNDROME.

For:
each:
bit plane:

choose:
the:
single:
unused:
logical:
location

with:
largest:
positive:
R_j.

Tie:

smallest:
block ID.

Apply:
one:
flip.

Recompute:
syndrome.

Maximum:

4:
flips:
per:
bit plane.

Purpose:

positive:
reference.

METHOD 2 — LOCAL_MAX

For:
each:
bit plane
and:
repair round:

1.
Each:
logical:
region
computes:
R_j
from:
its:
incident:
syndrome checks.

2.
Candidate:
if:
R_j >0
and:
the:
region
has:
not:
already:
flipped
during:
this:
repair:
episode.

3.
Define:
competitors:

candidate:
regions

that:
share:

at least:
one:
currently:
UNSATISFIED:
hypercheck

with:
region j.

4.
Region j
wins:
locally
if:

for:
every:
competitor c:

R_j > R_c

OR:

R_j == R_c
AND:
j < c.

Thus:

fixed:
lower:
block ID

breaks:
local:
ties.

5.
All:
local:
winners

flip:

IN PARALLEL.

6.
Recompute:
syndrome.

7.
Repeat:

maximum:
4:
rounds.

A:
logical:
location

may:
flip:

at most:
once
per:
repair:
episode /
bit plane.

Purpose:

distributed:
local:
approximation
to:
global:
greedy.

METHOD 3 — SYNCHRONOUS_THRESHOLD

At:
each:
round:

all:
unused:
logical:
regions

with:

R_j >0

flip:
simultaneously.

No:
competition /
inhibition.

Maximum:

4:
rounds.

Purpose:

test:
whether:
competition

is:
necessary
to:
prevent:
repair:
avalanches.

METHOD 4 — LOCAL_MAX_ONE_ROUND

Exact:
LOCAL_MAX:

but:

one:
repair:
round
maximum.

Purpose:

test:
the:
value
of:
iterative:
local:
re-evaluation.

DYNAMICS

Exact:
DG-1R-05H.

Repair episode:

before:
current:
input.

Then:

input overwrite.

Then:

one:
MIXED5:
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

20260926059000
through:
20260926059007.

No:
prior:
DG-1R:
seed reuse.

DAMAGE FAMILIES

Exact:
DG-1R-05H.

LOCAL_DATA2_D6.

CHECK2_CORRELATED_D6.

CHECK3_CORRELATED_D6.

CHECK4_CORRELATED_D6.

DATA2_PLUS_CHECK2_D6.

DATA2_PLUS_CHECK3_D7.

CHECK4_CORRELATED_D7.

DISTRIBUTED_LOCAL_DATA2.

No:
damage:
geometry:
change.

PRIMARY METRICS

At:

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
- decoder rounds;
- total local winners;
- maximum simultaneous winners;
- residual syndrome weight;
- competition suppressions.

FALSE LOGICAL FLIP

Same:
DG-1R-05H:
counterfactual:
definition.

A:
local:
repair:
flip

is:
false

if:

its:
post-flip:
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

Repair logic:

never:
sees:
this:
label.

DISTRIBUTED LOCAL-TISSUE SIGNAL

TRUE
if:

LOCAL_MAX

on:
DISTRIBUTED_LOCAL_DATA2

has:

1.
median:
h1 logical divergence
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

5.
residual syndrome weight median
=
0.

LOCAL ROBUSTNESS PRESERVATION

TRUE
if:

LOCAL_MAX

also:
preserves:
exact:
repair
on:

DATA2_PLUS_CHECK2_D6

and:

DATA2_PLUS_CHECK3_D7.

LOCALITY GAP

TRUE
if:

GLOBAL_GREEDY
passes:
distributed:
repair

but:

LOCAL_MAX
fails.

Interpretation:

global:
arbitration
contains:
repair:
value
not:
captured
by:
local:
competition.

COMPETITION VALUE SIGNAL

TRUE
if:

LOCAL_MAX

outperforms:

SYNCHRONOUS_THRESHOLD

on:
DISTRIBUTED_LOCAL_DATA2

by:

lower:
logical divergence area

OR:

lower:
false logical flip fraction

while:
not:
degrading:
local:
robustness.

ROUND VALUE SIGNAL

TRUE
if:

LOCAL_MAX

outperforms:

LOCAL_MAX_ONE_ROUND

on:
DISTRIBUTED_LOCAL_DATA2

with:

no:
increase:
in:
false logical flip fraction.

CORRELATED-FAULT BOUNDARY

CHECK4_CORRELATED_D6.
CHECK4_CORRELATED_D7.

No:
positive:
safety:
claim
is:
pre-registered.

Report:

false:
local:
repair
and:
residual:
syndrome.

IMPORTANT

LOCAL_MAX
is:
still:
a:
synchronous:
software:
simulation.

A:
positive:
result
does NOT:
claim:
a:
biological:
mechanism.

It shows:

the:
repair:
decision

can:
be:
decomposed

into:

local:
syndrome:
messages

plus:

local:
competition

plus:

bounded:
rounds

without:
needing:
one:
global:
winner:
selection.

This:
is:
the:
architectural:
property
under:
test.

NEXT

If:
DISTRIBUTED_LOCAL_TISSUE_SIGNAL
and:
LOCAL_ROBUSTNESS_PRESERVATION:

proceed to:

DG-1R-05J —
ASYNCHRONOUS /
DELAYED:
LOCAL:
REPAIR
under:
message:
latency
and:
partial:
update:
order.

Purpose:

test:
whether:
local:
repair
remains:
stable

without:
a:
perfect:
global:
round:
barrier.

If:
LOCALITY GAP:

investigate:

- local:
  confidence:
  fields;
- inhibitory:
  repair:
  signals;
- repair:
  leader:
  election;
- temporary:
  quarantine.

If:
SYNCHRONOUS_THRESHOLD
matches:
LOCAL_MAX:

competition
is:
unnecessary
and:
the:
simpler:
local:
rule
should:
be:
preferred.

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
DG-1R-05I:
scenario:

do not alter:

- score definition;
- competitor definition;
- local tie rule;
- round cap;
- location reuse rule;
- damage families;
- thresholds;
- world family;
- metrics.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
last:
repairer
worked,

but:
it:
still:
had:
one:
central:
job:

look:
across:
the:
whole:
organism

and:
pick:
the:
single:
best:
place
to:
repair
next.

This:
test
removes:
that.

Every:
region
only:
looks:
at:

its:
nearby:
broken:
integrity:
checks.

It:
asks:

"Would:
changing:
my:
state
make:
my:
local:
integrity:
pattern
better?"

If:
yes,

it:
can:
become:
a:
repair:
candidate.

Nearby:
candidates
then:
compete.

The:
stronger:
local:
candidate
acts.

Non-conflicting:
repairs
can:
happen:
at:
the:
same:
time.

Then:
the:
organism
checks:
itself:
again.

If:
that:
still:
repairs:
two:
damaged:
regions
perfectly,

we:
will:
have:
removed:
another:
piece
of:
central:
control.

The:
healing:
process
would:
come:
from:

local:
damage:
signals

plus:

local:
competition

plus:

repeated:
self-checking.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN LINEAGE NOTE — DEFERRED IDENTIFIER COLLISION

DATE:
2026-09-20.

STATUS:
PREREGISTERED /
NOT EXECUTED /
DEFERRED BEFORE HARNESS CREATION.

A:
later:
same-branch:
preregistration

at:

374302bf08564a2c3328bc908f73d525460f7fc7

also:
used:
the:
DG-1R-05I:
identifier

for:

Cross-Bit-Plane Fault-Type Confidence Audit.

Commit order:

this:
LOCAL_MAX:
preregistration:

6fc8b82d3616eb00ed86a1393c4fae1811377286.

later:
CROSS-BIT-PLANE:
preregistration:

374302bf08564a2c3328bc908f73d525460f7fc7.

Therefore:

the:
later:
cross-bit-plane:
experiment

is:
the:
authoritative:
DG-1R-05I:
frontier.

This:
local-max:
message-passing:
experiment

is:
DEFERRED.

It:
has:
NO:
committed:
harness.

NO:
freeze.

NO:
executed:
world.

NO:
result.

Its:
design
may:
be:
renumbered
and:
revisited
after:
the:
authoritative:
05I:
confidence:
audit.

Its:
seed family
must NOT:
be:
used
by:
this:
deferred:
version
while:
05I:
is:
active.

canonical_scientific_execution = false.
stab18_r1_touched = false.
