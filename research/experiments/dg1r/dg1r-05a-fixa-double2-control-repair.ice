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
