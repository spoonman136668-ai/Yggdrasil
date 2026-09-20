TITLE: DG-1A-CLR3-H191-P4 — Fixed DICT8 Shared-Residual Capacity Stress Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE CAPACITY PILOT / NOT H191 PRIMARY
TRACK: DG-1 / CAPABILITY HIBERNATION / SHARED COORDINATION CAPACITY
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p3-fixed-multiscale-parent-dictionary-audit.ice

PURPOSE

H191-P3 established a positive mechanical result for:

DICT8

using:

- 8 shared fixed multiscale parent-dictionary factors;
- 24 learned A/B/C decoder coefficients;
- fixed scales 0.22 / 0.44 / 0.88;
- PROXY8-equivalent sleep inference overhead.

P4 asks:

HOW MUCH:
SHARED RESIDUAL COMPLEXITY

CAN:
FIXED DICT8

ABSORB
BEFORE:
ITS ADVANTAGE
OVER:
SEPARATE PROXY8
DISAPPEARS?

BOUNDARY

NON-EVIDENCE synthetic capacity pilot only.

No:
accepted H190 parent.
No:
H191 acceptance claim.
No:
living tissue.
No:
wetware.
No:
biological implementation claim.
No:
production modification.
No:
canonical scientific execution.
No:
STAB-18-R1 execution.

FIXED ARCHITECTURE

DICT8 is frozen exactly as H191-P3:

- 3209 existing parent centers;
- scale slots:
  0.22,
  0.44,
  0.88;
- joint A/B/C recruitment;
- ridge alpha 0.001;
- 8 shared factors;
- 24 learned decoder scalars;
- 8 site IDs;
- 8 scale slots.

Do NOT:
increase rank,
add scales,
change ridge,
or:
change recruitment.

PROXY8 comparator:

exact frozen H191-P0/H190-style
separate per-capability OMP comparator.

SURROGATE COMPLEXITY SWEEP

The P0-P3 surrogate family used:
6 shared Gaussian generating factors
plus:
a 0.10 capability-specific sinusoidal remainder.

P4 varies ONLY:
the number of hidden shared Gaussian generating factors.

Conditions:

SRC4.
SRC6.
SRC8.
SRC12.

All other source parameter distributions remain:

source center:
uniform unit disk.

source sigma:
uniform [0.12,0.42].

decoder:
N(0,1).

capability-specific smooth remainder:
0.10 * a_T * sin(w_Tx*x + w_Ty*y + phase_T)

with:
the exact P0 distributions.

WORLD FAMILIES

10 disjoint worlds / condition.

SRC4:
20260924500000..20260924500009.

SRC6:
20260924510000..20260924510009.

SRC8:
20260924520000..20260924520009.

SRC12:
20260924530000..20260924530009.

Total:
40 worlds.

No:
P0,
P1,
P2,
or:
P3
seed reuse.

DATA

Per world / capability:

128 distillation coordinates.

512 held-out coordinates.

Same:
A/B/C context geometry.

METRICS PER CONDITION

For:
PROXY8
and:
DICT8

report:

- held-out A/B/C median NMSE;
- median world mean-capability NMSE;
- P90 world mean-capability NMSE;
- all-capability <=0.01 rate;
- all-capability <=0.02 rate;
- distillation-to-held-out gap.

Also report:

- paired DICT8 - PROXY8 median delta;
- paired DICT8 win rate;
- DICT8 decoder concentration;
- DICT8 scale-slot counts.

CAPACITY INTERPRETATION

This pilot does NOT use:
a pass/fail claim
for:
H191.

Instead classify:
the mechanical regime.

ROBUST:

DICT8 median paired delta <=0
and:
win rate >=50%.

TRANSITION:

median paired delta >0
but:
<=0.02

OR:
win rate:
25%..49.9%.

OVER-CAPACITY:

median paired delta >0.02
and:
win rate <25%.

These labels are:
pilot diagnostics only.

IMPORTANT

If:
DICT8 becomes:
over-capacity
at:
SRC12,

do NOT:
increase:
factor count
inside:
P4.

That boundary
is:
the result.

If:
DICT8 remains:
robust
through:
SRC12,

the next question
is:
capability-count scaling,
not:
more source-rank stress.

REPRODUCIBILITY

Two:
full:
40-world sweeps.

Canonical output bytes
must:
match exactly.

NO POST-RUN TUNING

No:
architecture,
source distribution,
seed family,
condition count,
or:
diagnostic
changes
after:
the first P4 world.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
