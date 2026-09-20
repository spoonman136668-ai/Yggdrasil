TITLE: DG-1R-05B — Confidence-Aware SECDED Repair / Abstention Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE CONFIDENCE-REPAIR PILOT
TRACK: DG-1R / SOFTWARE CELLS / LOCAL REDUNDANCY / REPAIR CONFIDENCE
BRANCH: dg1a-ar
PARENT: DG-1R-05A + DG-1R-05A-FIXA

PURPOSE

DG-1R-05A established:

- local redundancy can restore correctable single-bit damage
  to the exact undamaged counterfactual trajectory;
- distributed one-bit-per-block damage can also be repaired exactly;
- one-bit H6 gating is not a reliable repair-confidence signal.

DG-1R-05A-FIXA established:

- arbitrary two-bit damage inside one Hamming(7,4) codeword
  causes blind single-error correction to mis-correct;
- both primary Hamming(7,4) repair policies showed
  100% false-correction fraction on the corrected DOUBLE2 control.

DG-1R-05B asks:

CAN:
THE:
SAME:
128-BIT:
ORGANISM

ENCODE:
LOCAL:
REPAIR:
CONFIDENCE

SO:
THE:
MAINTENANCE:
CELL

CAN:

REPAIR
WHEN:
THE:
LOCAL:
STATE
IS:
UNIQUELY:
RECOVERABLE

AND:

ABSTAIN
WHEN:
THE:
LOCAL:
STATE
IS:
AMBIGUOUS?

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

TOTAL STATE BUDGET

128 persistent bits.

16 local blocks.

Each block:

8 physical bits.

No:
hidden memory.

No:
external history buffer.

No:
task target.

No:
counterfactual oracle
is visible
to:
the:
repair policy.

CONFIDENCE CODE

Use:

extended Hamming(8,4)
SECDED-style local encoding.

Physical positions:

1:
p1.

2:
p2.

3:
d1.

4:
p4.

5:
d2.

6:
d3.

7:
d4.

8:
overall parity q.

The eighth bit:

occupies:
the:
same:
physical:
slot
previously used
as:
the:
one-bit:
nanite controller.

Interpretation:

the:
maintenance cell
now:
stores:

LOCAL:
CONFIDENCE /
CONSISTENCY
INFORMATION

instead of:
hysteretic:
state.

Thus:

64:
logical:
data bits

+
64:
redundancy /
confidence bits

=

128:
persistent bits.

EVOLUTION

The 64 logical data bits:

form:
one:
periodic:
logical:
MIXED5:
CA ring.

Per external input:

1.
inspect:
the:
persistent:
8-bit:
local:
codewords;

2.
apply:
the:
method's:
frozen:
repair /
abstention:
policy;

3.
decode:
the:
64:
logical:
data bits;

4.
apply:
the:
current:
input overwrite
to:
8:
fixed:
logical:
positions;

5.
apply:
one:
logical:
MIXED5:
CA update;

6.
re-encode:
all:
16:
local:
8-bit:
codewords.

INPUT MAPPING

Use:
the:
same:
mapped-block:
family
as:
DG-1R-05A.

Input-mapped blocks:

1,
2,
5,
7,
10,
11,
13,
14.

Damage blocks:

exclude:
direct:
input-mapped:
physical:
sites.

SECDED CLASSIFICATION

For each:
8-bit:
codeword:

Compute:

Hamming(7,4):
syndrome S
from:
positions:
1..7.

Compute:

overall parity P
across:
all:
8:
bits.

Interpretation:

S = 0
and:
P = 0:

NO ERROR.

S != 0
and:
P = 1:

SINGLE-BIT ERROR
inside:
positions:
1..7.

Correct:
position:
S.

S = 0
and:
P = 1:

SINGLE-BIT ERROR
in:
overall-parity:
position:
8.

Correct:
position:
8.

S != 0
and:
P = 0:

AMBIGUOUS:
DOUBLE-BIT:
ERROR.

DO NOT:
CORRECT.

ABSTAIN.

This:
is:
the:
primary:
confidence-aware:
policy.

METHODS

1.
HAM74_REPAIR_ALWAYS_REFERENCE

Exact:
DG-1R-05A:
Hamming(7,4):
always-repair:
logic
using:

7:
code bits
+
1:
unused /
non-confidence:
eighth bit.

Purpose:

known:
single-error:
positive
and:
two-error:
mis-correction:
reference.

2.
SECDED84_DETECT_ONLY

Use:
8-bit:
SECDED:
encoding.

Classify:
error type.

Never:
correct.

Purpose:

separate:
confidence:
information
from:
actual:
repair.

3.
SECDED84_REPAIR_ABSTAIN

Primary candidate.

Correct:

unique:
single-bit:
errors.

Abstain:

S !=0
and:
P =0:
ambiguous:
two-bit:
pattern.

4.
SECDED84_BLIND_SYNDROME

Use:
8-bit:
SECDED:
encoding

but:
ignore:
overall:
parity
when:
S !=0.

Always:
correct:
syndrome:
position.

Purpose:

show:
that:
the:
extra:
confidence bit
only:
helps
if:
the:
policy
uses it.

DAMAGE FAMILY

A.
SINGLE1_LOCAL

Four:
local:
scenarios
per world.

Blocks:

0,
4,
8,
12.

Flip:

physical:
position:
3
inside:
the:
block.

B.
PARITY1_LOCAL

Same:
four:
blocks.

Flip:

physical:
position:
8
only.

Purpose:

verify:
the:
confidence bit
itself
is:
repairable.

C.
DOUBLE2_LOCAL

Same:
four:
blocks.

Flip:

physical:
positions:

3
and:
5.

D.
TRIPLE3_LOCAL

Same:
four:
blocks.

Flip:

physical:
positions:

3,
5,
6.

Purpose:

adversarial:
beyond-SECDED:
boundary.

E.
DISTRIBUTED3

Blocks:

0,
4,
8.

Flip:

one:
physical:
position:
3
in:
each.

F.
DISTRIBUTED5

Blocks:

0,
3,
6,
9,
12.

Flip:

one:
physical:
position:
3
in:
each.

COUNTERFACTUAL FRAMEWORK

Exact:
DG-1R-05A:
style.

Pre-damage:

1024:
external:
steps.

Clone:

undamaged:
reference

and:
damaged:
organism.

Post-damage:

32:
identical:
future:
inputs.

Measure:
at:

1,
4,
8,
16,
32:
steps.

METRICS

- whole-state divergence;
- damaged-site recovery;
- outside-lesion divergence;
- damage-spread count;
- excess divergence area;
- sustained full-recovery rate;
- recovery time.

CONFIDENCE TELEMETRY

Per:
method /
damage family:

- no-error classifications;
- single-data classifications;
- single-parity classifications;
- ambiguous-double classifications;
- corrections;
- abstentions;
- false corrections;
- missed correctable errors.

Evaluation:

may:
compare:
the:
repair decision
against:
the:
undamaged:
counterfactual
ONLY:
for:
telemetry.

The:
repair policy
never:
sees:
the:
counterfactual.

PRIMARY SIGNALS

SAFE_SINGLE_REPAIR

TRUE
for:
SECDED84_REPAIR_ABSTAIN
if:

SINGLE1_LOCAL:

1.
median:
damaged-site recovery
at:
h1
=
1.0;

2.
median:
whole-state divergence
at:
h1
=
0;

3.
full-recovery rate
=
1.0;

4.
false corrections
=
0.

PARITY_SELF_REPAIR

TRUE
if:

PARITY1_LOCAL:

full-recovery rate
=
1.0

and:
false corrections
=
0.

DOUBLE_ABSTENTION

TRUE
if:

DOUBLE2_LOCAL:

1.
ambiguous-double classification rate
=
1.0;

2.
correction count
=
0;

3.
abstention count
>
0;

4.
false corrections
=
0.

DISTRIBUTED_SAFE_REPAIR

TRUE
if:

DISTRIBUTED3
and:
DISTRIBUTED5:

- full-recovery rate
=
1.0;
- median:
  excess divergence area
=
0;
- false corrections
=
0.

CONFIDENCE_AWARE_REPAIR_SIGNAL

TRUE
if:

SAFE_SINGLE_REPAIR
and:
PARITY_SELF_REPAIR
and:
DOUBLE_ABSTENTION
and:
DISTRIBUTED_SAFE_REPAIR.

TRIPLE DAMAGE

TRIPLE3_LOCAL:

is:
a:
boundary:
telemetry
family.

No:
positive:
gate
is:
required.

Report:

- classification;
- correction;
- abstention;
- false correction;
- divergence.

Reason:

SECDED
cannot:
guarantee:
correct:
classification
of:
arbitrary:
three-bit:
errors.

BLIND-SYNDROME CONTROL

Expected:

SECDED84_BLIND_SYNDROME

should:
mis-correct:
DOUBLE2_LOCAL

similarly:
to:
HAM74_REPAIR_ALWAYS_REFERENCE.

If:
it:
does not:

investigate:
mechanical:
implementation
before:
accepting:
the:
confidence:
result.

REDUNDANCY COST

Report:

logical:
data:
capacity:

64 bits.

Persistent:
physical:
capacity:

128 bits.

Redundancy /
confidence:

64 bits.

No:
state-budget:
increase.

INTERPRETATION

A:
positive:
DG-1R-05B

would show:

self-repair:
requires:

not only:
repair information

but:

information:
about:
WHEN:
repair:
information
is:
sufficient.

This creates:
a:
three-mode:
maintenance:
policy:

1.
healthy:
continue;

2.
correctable:
repair;

3.
ambiguous:
abstain /
hand off
to:
containment.

NEXT

If:
CONFIDENCE_AWARE_REPAIR_SIGNAL:

DG-1R-05C:

COUPLE:
SECDED:
confidence

to:
the:
previous:
H6:
damage-containment:
mechanism.

Goal:

correct:
single-bit:
damage

and:

quarantine:
ambiguous:
multi-bit:
damage

without:
global:
freezing.

If:
the:
confidence bit
fails:

investigate:
larger:
local:
codes
or:
neighbor:
consensus

under:
the:
same:
128-bit:
budget.

Long-term:

replace:
human-designed:
SECDED

with:

developmentally:
emergent:
redundancy /
confidence.

WORLD FAMILY

8 worlds.

Seeds:

20260926052000
through:
20260926052007.

No:
prior:
DG-1R:
seed reuse.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Outputs:
must:
match
byte-for-byte.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
last:
experiment
showed:

backup:
information
can:
tell:
a:
nanite
exactly:
how:
to:
fix:
one:
bad:
bit.

But:
with:
two:
bad:
bits,

the:
same:
repair:
rule
can:
confidently:
make:
the:
wrong:
change.

So:
this:
experiment
uses:
the:
eighth:
bit
inside:
each:
local:
group

as:
a:
confidence:
check.

That:
bit
does:
not:
tell:
the:
system
the:
answer.

It:
tells:
the:
system
whether:
the:
local:
evidence
is:
consistent
with:

ONE:
repairable:
error

or:

AN:
AMBIGUOUS:
error
that:
should:
not:
be:
guessed at.

The:
goal
is:

FIX:
WHAT:
YOU:
KNOW:
HOW:
TO:
FIX.

QUARANTINE:
WHAT:
YOU:
DO:
NOT:
KNOW:
HOW:
TO:
FIX.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05B CONFIDENCE-AWARE SECDED REPAIR

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05B:
WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05b_confidence_secded_v1.py

Harness commit:

7b1caac463f839dede7ecf4eda572551d8f4d0ac.

Git blob SHA:

841e1336cd57abb853689b49ad664be8644e201b.

Source SHA-256:

3fb2fe2e67a83a46b10eedfa978d47f7b130dc245568faf4afe13759aef35179.

Source bytes:

16033.

LOCAL PRECHECK

Git blob identity:

PASS.

Python syntax:

PASS.

No:
DG-1R-05B:
world
was:
executed
before:
this:
freeze.

FROZEN WORLD FAMILY

20260926052000..20260926052007.

8 worlds.

FROZEN METHODS

HAM74_REPAIR_ALWAYS_REFERENCE.

SECDED84_DETECT_ONLY.

SECDED84_REPAIR_ABSTAIN.

SECDED84_BLIND_SYNDROME.

FROZEN DAMAGE FAMILIES

SINGLE1_LOCAL.

PARITY1_LOCAL.

DOUBLE2_LOCAL.

TRIPLE3_LOCAL.

DISTRIBUTED3.

DISTRIBUTED5.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output:
SHA-256
must:
match exactly.

DG-1R-05:
canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05B NON-EVIDENCE PILOT CLOSURE — CONFIDENCE-AWARE SECDED REPAIR / ABSTENTION

DATE:
2026-09-20.

STATUS:
COMPLETE /
CONFIDENCE-AWARE REPAIR SIGNAL PASS /
DOUBLE-ERROR ABSTENTION PASS /
TRIPLE-ERROR BOUNDARY EXPOSED /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

3fb2fe2e67a83a46b10eedfa978d47f7b130dc245568faf4afe13759aef35179.

OUTPUT

RUN 1 SHA-256:

35873fb35f17417c1721820de03a2ef8c076015e4ba05b24325ea596414192de.

RUN 2 SHA-256:

35873fb35f17417c1721820de03a2ef8c076015e4ba05b24325ea596414192de.

Byte-identical:

PASS.

MECHANICAL VALIDITY

PASS.

FROZEN SIGNALS

SAFE_SINGLE_REPAIR:

TRUE.

PARITY_SELF_REPAIR:

TRUE.

DOUBLE_ABSTENTION:

TRUE.

DISTRIBUTED_SAFE_REPAIR:

TRUE.

BLIND_DOUBLE_MISCORRECTION_SIGNAL:

TRUE.

CONFIDENCE_AWARE_REPAIR_SIGNAL:

TRUE.

SECDED84_REPAIR_ABSTAIN — SINGLE1_LOCAL

Median:
excess divergence area:

0.

Full recovery rate:

1.0.

h1:
damaged-site recovery:

1.0.

h1:
whole-state divergence:

0.

Corrections:

32.

False corrections:

0.

Abstentions:

0.

Thus:

all:
32:
single-bit:
local:
damage scenarios

returned:

immediately

to:

the:
exact:
undamaged:
counterfactual:
trajectory.

SECDED84_REPAIR_ABSTAIN — PARITY1_LOCAL

Median:
excess divergence area:

0.

Full recovery rate:

1.0.

Corrections:

32.

False corrections:

0.

Thus:

the:
confidence /
overall-parity:
bit

is:
itself:
repairable.

SECDED84_REPAIR_ABSTAIN — DOUBLE2_LOCAL

Scenario count:

32.

Ambiguous-double classifications:

32.

Abstentions:

32.

Corrections:

0.

False corrections:

0.

Median:
excess divergence area:

2.359375.

Full recovery rate:

0.25.

Interpretation:

the:
system
cannot:
reconstruct:
the:
two-bit:
damage,

but:

it:
correctly:
recognizes:

I:
DO:
NOT:
HAVE:
ENOUGH:
INFORMATION

and:

does:
NOT:
make:
a:
false:
repair.

This:
directly:
fixes:
the:
failure:
seen:
in:
DG-1R-05A-FIXA.

BLIND CONTROL — DOUBLE2_LOCAL

SECDED84_BLIND_SYNDROME:

Corrections:

32.

False corrections:

32.

False correction fraction:

1.0.

Thus:

the:
eighth:
confidence bit

only:
helps

when:

the:
maintenance:
policy

actually:
uses:
the:
confidence:
classification.

HAM74_REPAIR_ALWAYS_REFERENCE — DOUBLE2_LOCAL

Corrections:

32.

False corrections:

32.

False correction fraction:

1.0.

This:
reproduces:
the:
known:
Hamming(7,4):
over-correction:
boundary.

DISTRIBUTED3

SECDED84_REPAIR_ABSTAIN:

Median:
excess divergence area:

0.

Full recovery rate:

1.0.

Corrections:

24.

False corrections:

0.

DISTRIBUTED5

Median:
excess divergence area:

0.

Full recovery rate:

1.0.

Corrections:

40.

False corrections:

0.

Thus:

confidence-aware:
repair

preserves:
the:
strong:
distributed:
correctable-damage:
result.

TRIPLE3_LOCAL

SECDED84_REPAIR_ABSTAIN:

Median:
excess divergence area:

2.578125.

Full recovery rate:

0.25.

Corrections:

32.

False corrections:

32.

False correction fraction:

1.0.

Interpretation:

arbitrary:
three-bit:
local:
damage

can:
masquerade:

as:
a:
single-bit:
SECDED:
pattern.

Therefore:

SECDED:

solves:
the:
single-versus-double:
confidence:
problem,

but:

does NOT:
provide:
unbounded:
repair:
certainty.

TECHNICAL INTERPRETATION

The:
Yggdrasil:
repair stack

now has:
three:
mechanically:
supported:
layers.

1.
CONTAINMENT

DG-1R-05:
mirror:

H6 /
H6_REPAIR:

can:
reduce:
damage spread.

2.
RECONSTRUCTION INFORMATION

DG-1R-05A:

local:
redundancy:

can:
reconstruct:
correctable:
damage
exactly.

3.
REPAIR CONFIDENCE

DG-1R-05B:

extended:
local:
consistency:

can:
distinguish:

safe:
single-bit:
repair

from:

ambiguous:
two-bit:
damage

and:

ABSTAIN.

The:
remaining:
problem

is:
how:
to:
handle:
damage
that:
exceeds:
the:
local:
confidence:
model.

The:
next:
architecture

should:
NOT:
attempt:
larger:
blind:
repair.

Instead:

when:
the:
local:
repair system

reports:

AMBIGUOUS,

route:
the:
block
into:

CONTAINMENT /
QUARANTINE

so:
uncertain:
state

does:
not:
spread.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05C —
CONFIDENCE-GATED:
LOCAL:
QUARANTINE /
CONTAINMENT:
AUDIT.

Goal:

combine:

SECDED:
repair confidence

with:

the:
damage-spread:
containment:
behavior
seen:
in:
H6:
nanites.

Policy:

HEALTHY:

evolve normally.

CORRECTABLE:

repair,
then:
evolve.

AMBIGUOUS:

do NOT:
guess.

Quarantine:
the:
local:
block

and:
limit:
its:
influence
on:
neighboring:
logical:
state

until:
confidence:
returns.

Primary target:

preserve:

perfect:
single /
distributed:
correctable:
repair

while:

reducing:
outside-lesion:
divergence

for:
DOUBLE2

relative:
to:
plain:
SECDED84_REPAIR_ABSTAIN.

TRIPLE3:

remain:
an:
adversarial:
boundary.

PLAIN-SPEAK SUMMARY

We:
gave:
the:
repair system

one:
extra:
kind:
of:
local:
information:

not:
the:
answer,

but:

whether:
the:
answer
is:
safe
to:
infer.

That:
worked.

With:
one:
bad:
bit:

it:
repairs:
perfectly.

With:
several:
one-bit:
damages
in:
different:
local:
areas:

it:
repairs:
all:
of:
them
perfectly.

With:
two:
bad:
bits
inside:
the:
same:
local:
area:

it:
now:
recognizes:

THIS:
IS:
AMBIGUOUS.

It:
does:
not:
guess.

It:
does:
not:
make:
the:
wrong:
repair.

That:
is:
a:
major:
improvement.

But:

three:
bad:
bits

can:
still:
look:
like:
one:
repairable:
error.

So:

we:
still:
need:
a:
larger:
safety:
architecture

around:
local:
repair.

The:
next:
step
is:

if:
the:
nanite
is:
not:
sure,

do:
not:
repair.

ISOLATE:
THE:
AREA.

STOP:
THE:
DAMAGE
FROM:
SPREADING.

Then:
let:
a:
higher:
level:
repair:
mechanism
decide:
what:
to:
do.

DG-1R-05:
canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
