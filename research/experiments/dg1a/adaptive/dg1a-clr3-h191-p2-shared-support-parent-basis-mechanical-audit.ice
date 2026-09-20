TITLE: DG-1A-CLR3-H191-P2 — Shared-Support Parent-Basis Sleep Latent Mechanical Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE IMPLEMENTATION PILOT / NOT H191 PRIMARY
TRACK: DG-1 / CAPABILITY HIBERNATION / SHARED RESIDUAL SUPPORT
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p1-multiscale-shared-latent-mechanical-audit.ice

PURPOSE

H191-P1 showed:

- multiscale shared Gaussian factors can genuinely share across A/B/C;
- rank 8 can beat separate PROXY8 on the surrogate family;
- but the six-scalars-per-factor accounting makes rank 8 cost 48 learned scalars.

H191-P2 asks:

CAN RANK-8-LIKE SHARED EXPRESSIVITY
BE RETAINED
AT:
24 LEARNED SCALARS

BY:
RECRUITING
ONE SHARED SUPPORT SET
FROM:
THE EXISTING 3209 PARENT BASIS FUNCTIONS?

BOUNDARY

Synthetic computational research only.
NON-EVIDENCE.
No living tissue.
No wetware.
No biological implementation claim.
No production modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT PILOT SEMANTICS

Reuse frozen H191-P0 for:

- unit-disk 3209-site parent geometry;
- parent Gaussian sigma=0.22;
- A/B/C context geometry;
- surrogate residual family;
- 128 distillation coordinates / capability;
- 512 held-out coordinates / capability;
- separate per-capability PROXY8 comparator;
- ridge alpha=0.001;
- metrics and canonical serialization.

DISJOINT WORLD FAMILY

20260924390000
through:
20260924390039.

40 worlds.

No P0 or P1 world is reused.

SHARED-SUPPORT LATENT

Candidate factors:

all:
3209 existing parent Gaussian basis functions.

Factor k:

z_k(x)
=
exp(
-||x-parent_site_k||^2
/
(2*0.22^2)
).

Factor geometry is:
already-existing fixed model structure.

No:
new center,
new width,
or:
new physical cell
is learned or created.

SHARED SUPPORT RECRUITMENT

Recruit ONE common support sequence
jointly across:
A/B/C.

At each step:

for every unselected parent site candidate:

1.
append that site to:
the shared support set;

2.
for each capability independently,
fit all decoder coefficients
on:
that capability's
128 distillation residual values
by:
ridge alpha=0.001;

3.
score:
mean across A/B/C
of:
normalized residual reconstruction MSE;

4.
select:
lowest score;

5.
tie:
lower parent-site index.

Repeat to:
8 sites.

Nested prefixes:

SUPPORT2.
SUPPORT4.
SUPPORT8.

LEARNED MEMORY

Only decoder coefficients are learned.

SUPPORT2:

2 factors * 3 capability decoders
=
6 learned scalars.

SUPPORT4:

12 learned scalars.

SUPPORT8:

24 learned scalars.

Structural metadata:

one shared parent-site index per factor.

SUPPORT8:

8 site indices.

H190 PROXY8 comparator:

24 learned coefficients

plus:

three separate:
8-site support lists

=
24 site indices.

Therefore:

SUPPORT8 matches:
H190 PROXY8
learned-scalar count

while:
reducing:
support metadata
from:
24 site IDs
to:
8.

COMPUTE ACCOUNTING

At inference:

evaluate:
the shared support basis
once

+
selected capability decoder.

Rank 8:

8 factor evaluations
+
8 decoder multiply-adds.

This equals:
the H190 PROXY8
16-operation sleep-residual overhead.

Thus:

B-only:
approximately 2.438% of full.

C-only:
approximately 2.288%.

Equal A/B/C:
approximately 34.056%.

PILOT METRICS

Report:

- held-out NMSE per capability;
- mean / worst capability NMSE;
- SUPPORT2/4/8;
- PROXY8;
- paired SUPPORT8 - PROXY8 world delta;
- SUPPORT8 win rate;
- all-capability <=0.01 / <=0.02 rates;
- distillation-to-held-out gap;
- decoder concentration;
- support spatial spread;
- reproducibility.

MECHANICAL ENCOURAGEMENT

P2 is mechanically encouraging if:

1.
SUPPORT8 median mean-capability held-out NMSE
<= PROXY8.

2.
SUPPORT8 paired win rate
>=50%.

3.
SUPPORT8 median per-capability NMSE
is not worse than PROXY8
by:
>0.01
for:
A,
B,
or:
C.

4.
SUPPORT8 median distillation-to-held-out
mean NMSE gap
<=0.05.

5.
SUPPORT8 decoder concentration
is materially below:
1.0,
showing:
the common support is not merely partitioned
into capability-local sites.

6.
Two complete reruns
produce:
byte-identical canonical output.

These are:
NON-EVIDENCE diagnostics.

NO POST-RUN TUNING

After the first P2 world executes,
do not alter:

- support candidate set;
- sigma;
- recruitment;
- rank set;
- ridge;
- world family;
- comparator;
- metrics.

If SUPPORT8 succeeds mechanically:

it becomes:
the preferred pre-primary H191 architecture candidate

because:
it preserves:
rank-8 shared capacity
at:
the 24-learned-scalar budget.

If SUPPORT8 fails:

do NOT:
increase support count inside P2.

Move to:
a genuinely distributed fixed-basis factorization
rather than:
more sparse sites.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
