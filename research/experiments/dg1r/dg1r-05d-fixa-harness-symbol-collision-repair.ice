TITLE: DG-1R-05D-FIXA — Harness Symbol-Collision Repair
DATE: 2026-09-20
STATUS: PREREGISTERED / PRE-PRIMARY ARTIFACT REPAIR / NON-EVIDENCE
TRACK: DG-1R / SOFTWARE TISSUE / SYNDROME-BLIND REPAIR
BRANCH: dg1a-ar
PARENT: DG-1R-05D

DEFECT

The frozen DG-1R-05D harness defines:

encode(logical)

for:

tissue-state:
physical encoding.

Later:

the same:
global:
symbol name

is redefined as:

encode(o)

for:

canonical:
JSON:
serialization.

At runtime:

prefix()

calls:

encode(
np.zeros(...)
)

after:
the:
JSON:
definition
has:
replaced:
the:
tissue:
encoder.

Result:

TypeError:
ndarray
is not:
JSON serializable.

EXECUTION STATUS

The:
failure
occurred:

before:
the:
first:
DG-1R-05D:
scenario.

No:
world:
result
was:
produced.

No:
primary:
damage scenario
was:
executed.

Thus:

DG-1R-05D:
experimental:
budget

remains:

UNSPENT.

ALLOWED FIX

Rename:

the:
tissue-state:
encoder

from:

encode

to:

encode_tissue.

Update ONLY:

its:
tissue-state:
call sites:

- step();
- prefix().

Leave:

the:
JSON:
serializer:
encode(o)

unchanged.

NO OTHER:
semantic:
change
is:
allowed.

PRESERVE EXACTLY

- world seeds;
- damage families;
- damage geometry;
- trigger definitions;
- neighbor candidates;
- two-sided agreement;
- methods;
- metrics;
- thresholds;
- classifications;
- output schema.

PRE-RUN REQUIREMENT

After:
the:
symbol:
repair:

- Python:
  compile:
  PASS;
- exact:
  Git blob:
  identity:
  recorded;
- no:
  scenario:
  run
  before:
  FIXA:
  freeze.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Outputs:
must:
match
byte-for-byte.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05D-FIXA

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05D-FIXA:
SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05d_fixa_symbol_v1.py

Harness commit:

0ce4dd1b35f7c39a01fcb8dec37a7f229e78b5e6.

Git blob SHA:

c171336a4a9445c2c3269d85fbde3427bbd93bcf.

Source SHA-256:

2cd277dbdb77d8324b02710edd3c41725de25d498c95920c62e81462ebed3943.

Source bytes:

11032.

ALLOWED DELTA

Exactly:

- rename:
  tissue-state:
  encode(logical)
  to:
  encode_tissue(logical);

- update:
  step()
  tissue-state:
  call;

- update:
  prefix()
  initial-state:
  call.

No:
experimental:
semantic:
change.

LOCAL PRECHECK

Exact:
Git blob:
identity:

PASS.

Python:
compile:

PASS.

No:
DG-1R-05D:
scenario
was:
executed
before:
this:
freeze.

WORLD FAMILY

20260926054000..20260926054007.

8 worlds.

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
