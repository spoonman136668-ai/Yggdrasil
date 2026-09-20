TITLE: DG-1R-05A-FIXA — DOUBLE2 Local Lesion Control Repair
DATE: 2026-09-20
STATUS: PREREGISTERED / MECHANICAL CONTROL REPAIR ONLY / NON-EVIDENCE
TRACK: DG-1R / SOFTWARE CELLS / LOCAL REDUNDANCY / CONTROL REPAIR
BRANCH: dg1a-ar
PARENT: DG-1R-05A

DEFECT

The frozen DG-1R-05A harness encoded DOUBLE2_LOCAL as:

blocks = (b,)
offsets = (2, 4)

and lesion construction used:

zip(blocks, offsets).

Therefore:

only:
the:
first:
offset

was:
used.

DOUBLE2_LOCAL
was:
mechanically:
a:
single-bit:
lesion.

AFFECTED SURFACE

ONLY:

DOUBLE2_LOCAL.

UNAFFECTED:

- SINGLE1_LOCAL;
- DISTRIBUTED3;
- DISTRIBUTED5;
- world seeds;
- input mappings;
- logical rules;
- uncoded rules;
- Hamming encoding;
- repair policies;
- classification thresholds
  not dependent on DOUBLE2.

VALID RESULTS PRESERVED

The original DG-1R-05A:

SINGLE1_LOCAL
and:
DISTRIBUTED:
results

remain:

valid:
frozen:
non-evidence:
pilot outputs.

FIXA PURPOSE

Repair:
ONLY:
the:
DOUBLE2_LOCAL:
lesion generator

so:
each:
local:
DOUBLE2:
scenario

flips:

physical:
offset:
2

AND:

physical:
offset:
4

inside:
the:
same:
8-cell:
block.

ALLOWED CHANGE

In:
lesion_scenarios():

replace:

("DOUBLE2_LOCAL", (b,), (2, 4))

with:

("DOUBLE2_LOCAL", (b, b), (2, 4)).

NO OTHER:
semantic:
change
is:
allowed.

REPRODUCIBILITY

Run:
the:
full:
8-world:
harness
twice

after:
the:
single:
mechanical:
repair.

Required:

- byte-identical:
  canonical:
  output;
- SINGLE1_LOCAL:
  summary
  unchanged
  from:
  original:
  DG-1R-05A;
- DISTRIBUTED3:
  summary
  unchanged;
- DISTRIBUTED5:
  summary
  unchanged.

DOUBLE2 PRIMARY QUESTION

Does:
standard:
Hamming(7,4):
single-error:
repair

mis-correct:
two-bit:
local:
damage

as:
expected?

OVER-CORRECTION FAILURE

Retain:
the:
frozen:
threshold:

false corrections
>
10%:
of:
all:
corrections
on:
DOUBLE2_LOCAL.

INTERPRETATION

If:
the:
corrected:
DOUBLE2:
control
shows:
high:
false correction:

the:
pilot:
correctly:
identifies:
the:
repair-information:
boundary.

If:
it:
does NOT:

investigate:
the:
double-error:
telemetry
before:
any:
next:
architectural:
claim.

NO POST-RUN TUNING

After:
the:
first:
FIXA:
world,

do not alter:

- lesion positions;
- Hamming code;
- repair policy;
- seeds;
- metrics;
- thresholds.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05A-FIXA DOUBLE2 CONTROL

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
FIXA:
WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05a_fixa_double2_v1.py

Harness commit:

5efb76a745de950f528ac5790e3495a98b3f5c62.

Git blob SHA:

cabd2574625378b7f6a8cf7f30cc9f30a0a58f2a.

Source SHA-256:

cfc93793426168dfa02a68be90d4bde14b6ed7c0b3209a171a666f6cefe6b64c.

Source bytes:

19106.

ALLOWED DELTA

Exactly:

DOUBLE2_LOCAL:
block tuple

changed from:

(b,)

to:

(b, b).

No:
other:
semantic:
change.

LOCAL PRECHECK

Git blob identity:

PASS.

Python syntax:

PASS.

No:
FIXA:
world
was:
executed
before:
this:
freeze.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Required:

- byte-identical:
  output;
- SINGLE1_LOCAL:
  unchanged;
- DISTRIBUTED3:
  unchanged;
- DISTRIBUTED5:
  unchanged.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05A-FIXA CLOSURE — CORRECTED DOUBLE2 CONTROL

DATE:
2026-09-20.

STATUS:
COMPLETE /
MECHANICAL CONTROL REPAIRED /
EXPECTED OVER-CORRECTION BOUNDARY CONFIRMED /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

cfc93793426168dfa02a68be90d4bde14b6ed7c0b3209a171a666f6cefe6b64c.

CANONICAL NON-EVIDENCE OUTPUT

RUN 1 SHA-256:

49f5975834c10ddf1a216cc1088b7a57dca7d1e29d3c297e23f1ffbab01330e8.

RUN 2 SHA-256:

49f5975834c10ddf1a216cc1088b7a57dca7d1e29d3c297e23f1ffbab01330e8.

Byte-identical:

PASS.

UNAFFECTED FAMILY CHECK

SINGLE1_LOCAL:

exact summary match
to:
original:
DG-1R-05A:

PASS.

DISTRIBUTED3:

PASS.

DISTRIBUTED5:

PASS.

Thus:

the:
mechanical:
repair

changed:
ONLY:

DOUBLE2_LOCAL.

CORRECTED DOUBLE2 — HAM74_REPAIR_ALWAYS

Median:
excess divergence area:

2.28515625.

Full recovery rate:

0.1875.

Median:
damaged-site recovery:

h1:

0.5.

h4:

0.5.

Total:
corrections:

32.

False corrections:

32.

False correction fraction:

1.0.

OVER-CORRECTION FAILURE:

CONFIRMED.

CORRECTED DOUBLE2 — HAM74_REPAIR_H6

Median:
excess divergence area:

2.15625.

Full recovery rate:

0.25.

Median:
damaged-site recovery:

h1:

0.5.

h4:

0.5.

Total:
corrections:

17.

False corrections:

17.

False correction fraction:

1.0.

OVER-CORRECTION FAILURE:

CONFIRMED.

DOUBLE2 DETECT-ONLY CONTROL

Median:
excess divergence area:

2.13671875.

Full recovery rate:

0.25.

Thus:

attempting:
single-error:
Hamming correction

on:
two-bit:
local:
damage

does NOT:
improve:
the:
counterfactual:
trajectory

and:

every:
performed:
correction
is:
wrong
under:
the:
frozen:
counterfactual:
telemetry.

TECHNICAL INTERPRETATION

The:
repair-information:
hypothesis

is:
supported

but:
strictly:
capacity-bounded.

Hamming(7,4):

contains:
enough:
local:
redundancy

to:
reconstruct:
one:
damaged:
physical:
bit
per:
codeword.

It does NOT:
contain:
enough:
information

to:
uniquely:
reconstruct:
arbitrary:
two-bit:
damage.

The:
nanite:

must therefore:
know:

WHEN:
ITS:
LOCAL:
REPAIR:
INFORMATION

IS:
SUFFICIENT

and:

WHEN:
TO:
ABSTAIN.

This introduces:

REPAIR:
CONFIDENCE /
UNCERTAINTY

as:
a:
new:
architectural:
requirement.

PLAIN-SPEAK SUMMARY

The:
backup:
information
worked.

When:
one:
bit
inside:
a:
local:
group
was:
damaged,

the:
system
could:
figure out:
exactly:
which:
bit
was:
wrong

and:
put:
the:
organism
back:
onto:
the:
exact:
undamaged:
path.

But:

when:
two:
bits
inside:
the:
same:
group
were:
damaged,

the:
same:
repair:
rule
became:
overconfident.

It:
thought:
a:
third:
bit
was:
wrong

and:
changed:
the:
wrong:
cell.

So:
we learned:
two:
important:
things.

1.

The:
nanites
really:
were:
missing:
repair:
information.

Local:
redundancy
can:
supply:
that:
information.

2.

Repair:
must:
know:
its:
limits.

A:
self-healing:
system
cannot:
blindly:
repair
every:
error
it:
detects.

Sometimes:
the:
correct:
action
must:
be:

CONTAIN:
THE:
DAMAGE

and:

DO:
NOT:
GUESS.

canonical_scientific_execution = false.
stab18_r1_touched = false.
