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


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P4 DICT8 CAPACITY STRESS HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P4 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p4_dict8_capacity_stress_v1.py

Harness commit:

ecd511281c425072102f84ae51ad8798265fa4cb.

Git blob SHA:

00824eb329fe329f44821a60a2175f1dd0a8b65f.

Source SHA-256:

f81abefdc5dd40670d107968d6c03d7272eb8654eb56dcffa17df0ed31763e7f.

Source bytes:

4675.

DEPENDENCIES

H191-P3 multiscale dictionary harness Git blob:

1954ce689973f36d0a44d36271a0f002de0150d9.

H191-P2 shared-support harness Git blob:

689b1c9a20559e090c41763c9174da7a43590fad.

H191-P0 base harness Git blob:

6ac31f5cc3e091be7ef24ea74879903dd21cc2fa.

FROZEN CONDITIONS

SRC4:
20260924500000..20260924500009.

SRC6:
20260924510000..20260924510009.

SRC8:
20260924520000..20260924520009.

SRC12:
20260924530000..20260924530009.

10 worlds per condition.
40 worlds total.

Only:
shared Gaussian source-factor count
changes.

All:
DICT8 architecture,
PROXY8 comparator,
context geometry,
remainder amplitude,
source distributions,
ridge,
metrics,
and:
classification thresholds
remain frozen.

REPRODUCIBILITY

Execute:
two complete 40-world sweeps.

Canonical output SHA-256
must:
match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL H191-P4 NON-EVIDENCE PILOT CLOSURE — DICT8 CAPACITY STRESS

DATE:
2026-09-20.

STATUS:
COMPLETE / POSITIVE CAPACITY-STRESS RESULT /
DICT8 ROBUST THROUGH SRC12 /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

f81abefdc5dd40670d107968d6c03d7272eb8654eb56dcffa17df0ed31763e7f.

CANONICAL OUTPUT

RUN 1 SHA-256:

4c215735ac5d28d1697266b1058684b940723eb97927edd340472860010412ef.

RUN 2 SHA-256:

4c215735ac5d28d1697266b1058684b940723eb97927edd340472860010412ef.

Byte-identical:

PASS.

PRIMARY MECHANICAL QUESTION

Does:
fixed:
eight-factor:
shared multiscale DICT8

lose:
its advantage over:
separate PROXY8

as:
the hidden shared residual source
grows from:

4
to:
6
to:
8
to:
12

Gaussian generating factors?

RESULT

No:
capacity cliff
was observed
through:
SRC12.

All four:
preregistered conditions
classify:

ROBUST.

SRC4

PROXY8 median world mean NMSE:

0.02322961247261152.

DICT8:

0.0069478247811130805.

DICT8 - PROXY8
median paired delta:

-0.007184637062129084.

Win rate:

70%.

All A/B/C <=0.01:

PROXY8:
10%.

DICT8:
40%.

All A/B/C <=0.02:

PROXY8:
30%.

DICT8:
60%.

SRC6

PROXY8 median world mean NMSE:

0.02375066610732246.

DICT8:

0.013811613793575133.

Median paired delta:

-0.008559794867874646.

Win rate:

80%.

SRC8

PROXY8 median world mean NMSE:

0.029815087927511447.

DICT8:

0.021302490560160505.

Median paired delta:

-0.011500244811178457.

Win rate:

100%.

SRC12

PROXY8 median world mean NMSE:

0.04954405073759835.

DICT8:

0.021530002367270915.

Median paired delta:

-0.026431925265883074.

Win rate:

80%.

P90 DICT8 world mean NMSE:

0.046486227819219336.

P90 PROXY8:

0.10445927436180616.

Thus:

even at:
12 hidden shared generating factors,

the fixed:
eight-factor:
multiscale shared dictionary

remains:
mechanically competitive
and:
usually superior

to:
three separate:
eight-site sparse caches.

CAPABILITY MEDIANS AT SRC12

DICT8:

A:
0.018149861133043507.

B:
0.01642088836839559.

C:
0.022129012704616702.

PROXY8:

A:
0.03303576121608823.

B:
0.02514360371501266.

C:
0.06763012384960546.

All three:
DICT8 capability medians
are:
lower.

GENERALIZATION

Median:
distillation-to-held-out
mean NMSE gap:

SRC4 DICT8:
0.0014406941550340966.

SRC6:
0.006858730182313221.

SRC8:
0.005424429344096134.

SRC12:
0.006599758499044579.

No:
gross:
distillation overfit
appears.

SHARING

DICT8 decoder-concentration median:

SRC4:
0.6906783571323083.

SRC6:
0.679906464772672.

SRC8:
0.7064419914517026.

SRC12:
0.6771934040551979.

Thus:

increasing source complexity
does NOT:
cause:
the shared factors
to partition
into:
capability-local islands.

SCALE USE

All three:
fixed scale slots
remain:
materially recruited
at every condition.

SRC12 selections:

sigma 0.22:
38.

sigma 0.44:
29.

sigma 0.88:
13.

This supports:
the P3 conclusion
that:
multiscale geometry
is:
structurally useful.

PILOT CLASSIFICATION

SRC4:
ROBUST.

SRC6:
ROBUST.

SRC8:
ROBUST.

SRC12:
ROBUST.

No:
TRANSITION
or:
OVER-CAPACITY
regime
was reached.

TECHNICAL INTERPRETATION

P4 does NOT:
show:
that DICT8 has unlimited capacity.

It shows:

within:
this surrogate residual family,

raising:
the number of:
hidden shared Gaussian sources

from:
4
through:
12

does NOT:
erase:
the advantage
of:
eight shared:
fixed multiscale factors.

This is:
stronger
than:
a simple:
rank-equals-source-count
interpretation.

The likely reason is:

the selected DICT8 factors
are:
not:
trying to reconstruct:
the hidden generating basis
one-for-one.

Instead:

they approximate:
the residual function
over:
three bounded capability contexts

using:
a shared:
multiscale function basis.

Thus:

effective coordination dimension
can be:
lower
than:
the literal:
number of hidden source components.

IMPORTANT LIMIT

This remains:

NON-EVIDENCE.

The accepted:
H190 residual matrix
was not used.

H191 accepted-lineage primary remains:

NOT STARTED / PROVENANCE BLOCKED.

NEXT JUSTIFIED EXPERIMENT

The P4 preregistration stated:

if:
DICT8 remains ROBUST
through:
SRC12,

move to:

CAPABILITY-COUNT SCALING.

Next:

H191-P5 —
SHARED-DICTIONARY
CAPABILITY-COUNT
SCALING AUDIT.

Keep:

- DICT8 rank fixed;
- 24 learned scalars only for A/B/C is no longer possible as capability count rises,
  so report decoder-state growth explicitly;
- factor geometry fixed;
- factor support fixed-size;
- per-query factor compute fixed;
- add synthetic capability contexts progressively.

Primary question:

does:
shared factor geometry
remain:
compact

while:
capability-specific decoder memory
grows:
only linearly
and:
active factor compute
remains:
constant?

Also determine:

when:
a fixed 8-factor shared core
stops:
supporting:
additional capabilities
without:
factor expansion.

PLAIN-SPEAK SUMMARY

What did we try?

We made the hidden residual problem harder.
Instead of six underlying shared pieces,
we tested:
4,
6,
8,
and:
12.

We did NOT:
give DICT8
more factors,
more memory,
or:
more compute.

What happened?

It held up.

Even with:
12 hidden source factors,
DICT8
still beat:
the separate PROXY8 approach
in:
80% of the worlds.

Did it work?

Yes,
for this:
non-evidence mechanical stress test.

We did not find:
the point
where:
eight shared factors
break.

What did we actually learn?

The eight stored factors
do not seem to need:
a one-for-one match
with:
the hidden number of residual generators.

They can:
compress:
a more complicated residual field
into:
a smaller shared representation.

Why does it matter?

That is:
exactly the scaling behavior
Yggdrasil needs.

If:
coordination structure
had to grow:
one factor
for:
every underlying piece
of capability interaction,

the architecture
would eventually:
lose its advantage.

P4 did NOT:
show that behavior
through:
the tested range.

What should we try next?

Stop:
making the same three capabilities
internally harder.

Start:
adding:
more capabilities.

The next test should ask:

can:
the same:
eight-factor shared core

serve:
4,
5,
6,
and:
more capability contexts

without:
growing:
the shared factor geometry
or:
per-query active factor compute?

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
