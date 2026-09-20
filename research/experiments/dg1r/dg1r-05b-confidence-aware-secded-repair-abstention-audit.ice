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
