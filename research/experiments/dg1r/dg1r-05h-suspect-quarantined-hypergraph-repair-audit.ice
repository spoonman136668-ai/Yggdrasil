TITLE: DG-1R-05H — Suspect-Quarantined Hypergraph Repair Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE QUARANTINED-INTEGRITY PILOT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / QUARANTINE
BRANCH: dg1a-ar
PARENT: DG-1R-05G

PURPOSE

DG-1R-05G established:

- 20 four-region hyperchecks double witness incidence from 40 to 80
  under the same 48 logical + 80 integrity = 128 persistent bits;
- degree-6 hypergraph repair tolerates two corrupted integrity witnesses;
- degree-7 hypergraph repair tolerates three corrupted integrity witnesses;
- strict-majority ties abstain safely;
- simultaneous damage in two logical regions causes catastrophic
  cross-contamination of reconstruction candidates.

The new bottleneck is:

WITNESS INDEPENDENCE.

DG-1R-05H asks:

CAN:
THE:
SAME:
128-BIT:
HYPERGRAPH:
TISSUE

REPAIR:
SIMULTANEOUS:
MULTI-REGION:
DAMAGE

IF:

SUSPECT:
LOGICAL:
REGIONS

ARE:
IDENTIFIED:
BEFORE:
REPAIR

AND:

CANDIDATE:
RELATIONS

THAT:
DEPEND:
ON:
OTHER:
SUSPECT:
REGIONS

ARE:
TEMPORARILY:
EXCLUDED?

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

Exact:
DG-1R-05G:
hypergraph representation.

48:
logical bits.

80:
integrity bits.

128:
persistent bits.

No:
new:
persistent:
state.

No:
hidden:
history.

No:
task labels.

No:
counterfactual information
is:
visible
to:
repair logic.

HYPERGRAPH

Exact:
DG-1R-05G:
20:
four-region:
hyperchecks.

Minimum:
region degree:

6.

Maximum:

7.

Maximum:
pair co-occurrence:

2.

EPHEMERAL INCONSISTENCY TEST

At:
the:
beginning
of:
each:
external:
step,

before:
repair,
input overwrite,
or:
logical evolution:

for:
each:
hypercheck:

compute:

residual
=
stored_check
XOR:
current_member_1
XOR:
current_member_2
XOR:
current_member_3
XOR:
current_member_4.

A:
hypercheck
is:

INCONSISTENT

if:

any:
of:
its:
four:
residual bits
is:
1.

For:
each:
logical:
region:

INCONSISTENCY_SCORE

=
number:
of:
incident:
hyperchecks
that:
are:
INCONSISTENT.

SUSPECT THRESHOLD

Frozen:

4.

A:
logical:
region
is:
SUSPECT

if:

INCONSISTENCY_SCORE
>=
4.

Reason:

For:
a:
single:
damaged:
logical:
region,

all:
incident:
healthy:
hyperchecks
become:
inconsistent.

For:
the:
DG-1R-05G:
distributed:
damage pair:

blocks:
2
and:
8

share:
at most:
2:
hyperchecks.

Same-pattern:
damage
can:
cancel
inside:
those:
shared:
checks,

but:
the:
remaining:
incident:
checks
still:
produce:

block 2:

at least:
5:
inconsistent:
relations.

block 8:

at least:
4.

Thus:

threshold 4

is:
frozen
to:
identify:
both:
distributed:
damaged:
regions.

At:
the:
same time:

2:
or:
3:
isolated:
corrupted:
integrity:
checks

do NOT:
by:
themselves

raise:
an:
otherwise:
healthy:
degree-6/7:
region

above:
the:
threshold.

EPHEMERAL ONLY

The:
SUSPECT:
mask

is:
recomputed:
from:
current:
persistent:
state

at:
every:
external:
step.

It is:

NOT:
stored:
persistently.

It:
consumes:
no:
additional:
persistent:
bits.

REPAIR CANDIDATE FILTER

For:
a:
SUSPECT:
target:
region:

consider:
an:
incident:
hypercheck
only if:

NONE:
of:
the:
other:
three:
logical:
members

are:
SUSPECT.

Thus:

a:
damaged:
region

cannot:
serve:
as:
a:
repair:
source

for:
another:
simultaneously:
suspect:
region.

For:
each:
remaining:
trusted:
hypercheck:

reconstruct:
the:
target:
candidate

using:

stored_check
XOR:
the:
other:
three:
current:
logical:
regions.

Vote:

strict:
majority
among:
remaining:
candidate:
vectors.

If:
no:
strict:
majority:

ABSTAIN.

SIMULTANEOUS PROPOSALS

All:

SUSPECT:
scores,
trusted:
candidate:
sets,
and:
repair:
proposals

are:
computed

from:
ONE:
frozen:
pre-repair:
snapshot.

Only:
after:
all:
proposals
are:
resolved

are:
accepted:
repairs
applied:

SIMULTANEOUSLY.

Purpose:

avoid:
repair-order:
artifacts.

METHODS

1.
HYPER20_BASE_MAJORITY_48.

Exact:
DG-1R-05G:
majority:
reference.

No:
quarantine.

2.
HYPER20_QUARANTINE4_48.

Frozen:
threshold:
4.

Exclude:
hyperchecks
touching:
other:
suspect:
regions.

Strict:
majority:
over:
remaining:
trusted:
candidates.

3.
HYPER20_QUARANTINE4_DETECT_ONLY.

Compute:

- residuals;
- suspicion mask;
- trusted candidate sets;
- proposed winner.

Perform:
no:
repair.

Purpose:

separate:
quarantine:
representation /
detection

from:
actual:
reconstruction.

DYNAMICS

Exact:
DG-1R-05G:

48:
logical:
MIXED5:
state.

Input-mapped:
logical:
blocks:

1,
4,
7,
10.

Repair:
before:
current:
input overwrite.

One:
logical:
CA update
per:
external:
step.

All:
20:
hyperchecks
recomputed
after:
logical:
evolution.

Pre-damage:

1024:
external:
steps.

Post-damage:

32:
external:
steps.

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

A.
SINGLE_DATA2_D6

Target:

block 5.

Flip:

logical:
data bits:
0,
1.

Purpose:

ordinary:
single-region:
repair.

B.
DATA2_PLUS_CHECK2_D6

Target:

block 5.

Flip:

logical:
bits:
0,
1

plus:

bit 0
in:
two:
incident:
hyperchecks.

Purpose:

preserve:
DG-1R-05G:
two-bad-witness:
tolerance.

C.
DATA2_PLUS_CHECK3_D7

Target:

block 2.

Flip:

logical:
bits:
0,
1

plus:

bit 0
in:
three:
incident:
hyperchecks.

Purpose:

preserve:
DG-1R-05G:
three-bad-witness:
tolerance.

D.
DISTRIBUTED_DATA2_2_8

Flip:

logical:
bits:
0,
1

in:
block 2

and:

logical:
bits:
0,
1

in:
block 8.

Purpose:

exact:
DG-1R-05G:
distributed:
failure:
retest.

E.
DISTRIBUTED_DATA2_2_8_PLUS_CHECKS

Same:
logical:
damage
as:
D.

Additionally:

flip:
bit 0

in:
one:
incident:
hypercheck
for:
block 2

that:
does NOT:
contain:
block 8,

and:

bit 0

in:
one:
incident:
hypercheck
for:
block 8

that:
does NOT:
contain:
block 2.

Purpose:

test:
distributed:
logical:
damage
plus:
independent:
integrity:
damage.

F.
CHECK3_ONLY_D6

No:
logical:
damage.

Flip:

bit 0
in:
three:
incident:
hyperchecks
for:
block 5.

Purpose:

false-suspect:
safety.

Expected:

inconsistency score:

3.

Below:
threshold 4.

G.
CHECK4_ONLY_D6

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
block 5.

Purpose:

threshold:
boundary.

The:
healthy:
logical:
region

will:
be:
marked:
SUSPECT.

Question:

does:
trusted-candidate:
filtering

repair:
it:
incorrectly

or:
abstain /
retain:
healthy:
state?

LESION ASSERTIONS

Harness MUST assert:

- exact:
  logical:
  flip count;
- exact:
  integrity:
  flip count;
- physical:
  lesion:
  uniqueness;
- no:
  logical:
  lesion
  overlaps:
  current:
  input-mapped:
  logical:
  position.

PRIMARY TELEMETRY

Per:
scenario:

- suspect region IDs
  at:
  first:
  repair step;
- suspect count;
- target inconsistency score;
- trusted candidate count;
- excluded candidate count;
- winning vote count;
- repairs;
- false repairs;
- abstentions.

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
- logical recovery time.

FALSE REPAIR

A:
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
target

immediately:
before:
repair.

Repair logic:

never:
sees:
this:
label.

FROZEN SIGNALS

DISTRIBUTED_QUARANTINE_RECOVERY

TRUE
if:

HYPER20_QUARANTINE4_48

on:
DISTRIBUTED_DATA2_2_8:

1.
first-step:
suspect set
contains:
blocks:
2
and:
8;

2.
median:
h1 logical divergence
=
0;

3.
logical divergence area median
=
0;

4.
sustained exact logical recovery
>=0.90;

5.
false repair fraction
<=0.01;

AND:

HYPER20_BASE_MAJORITY_48

fails:
at least:
one:
of:
criteria:
2-5.

ROBUST_DISTRIBUTED_QUARANTINE

TRUE
if:

HYPER20_QUARANTINE4_48

on:
DISTRIBUTED_DATA2_2_8_PLUS_CHECKS:

median:
h4 logical divergence
=
0

AND:

sustained exact logical recovery
>=0.90

AND:

false repair fraction
<=0.01.

SINGLE_REGION_PRESERVATION

TRUE
if:

quarantine method

preserves:
zero:
median:
logical divergence area

and:
zero:
false:
repairs

for:

SINGLE_DATA2_D6.

DATA2_PLUS_CHECK2_D6.

DATA2_PLUS_CHECK3_D7.

FALSE_SUSPECT_SAFETY

TRUE
if:

CHECK3_ONLY_D6:

block 5
is:
NOT:
suspect

and:
false repairs
=
0;

AND:

CHECK4_ONLY_D6:

false repairs
=
0.

QUARANTINE_VALUE_SIGNAL

TRUE
if:

DISTRIBUTED_QUARANTINE_RECOVERY
=
TRUE

AND:

SINGLE_REGION_PRESERVATION
=
TRUE

AND:

FALSE_SUSPECT_SAFETY
=
TRUE.

IMPORTANT

A:
positive:
result

would show:

higher-order:
integrity
does NOT:
need:
to:
give up:
its:
capacity:
advantage

under:
multi-region:
damage

if:

the:
repair:
system
first:
separates:

TRUSTED:
regions

from:

SUSPECT:
regions.

The:
key:
new:
resource

would:
not:
be:

more:
persistent:
memory.

It:
would:
be:

EPHEMERAL:
FAULT:
LOCALIZATION.

A:
negative:
result

would:
show:

static:
hypergraph:
consistency

does:
not:
contain:
enough:
information

to:
localize:
multiple:
damaged:
regions
reliably

and:

time /
iterative:
evidence
would:
remain:
the:
next:
resource:
axis.

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
- suspicion metric;
- threshold 4;
- candidate exclusion;
- simultaneous proposal rule;
- lesions;
- metrics;
- world family.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
hypergraph
gave:
us:
many:
more:
witnesses
for:
the:
same:
number:
of:
bits.

But:

when:
two:
real:
data:
regions
were:
damaged,

they:
started:
lying
to:
each:
other's:
repair:
votes.

This:
test
adds:
no:
memory.

Before:
repairing:

the:
tissue
asks:

"Which:
regions
are:
showing:
lots:
of:
broken:
consistency:
relationships?"

Any:
region
with:
four:
or:
more:
broken:
hyperchecks

is:
temporarily:
marked:
suspect.

Then:

when:
repairing:
one:
suspect:
region,

we:
throw:
away:
any:
repair:
vote
that:
depends:
on:
another:
suspect:
region.

In:
plain terms:

do not:
ask:
one:
sick:
part
of:
the:
tissue

to:
testify
about:
another:
sick:
part.

If:
that:
works,

we:
keep:
the:
hypergraph's:
big:
coverage:
advantage

and:
gain:
multi-region:
repair

without:
adding:
a:
single:
persistent:
bit.

canonical_scientific_execution = false.
stab18_r1_touched = false.
