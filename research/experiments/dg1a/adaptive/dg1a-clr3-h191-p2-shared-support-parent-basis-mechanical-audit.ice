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


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P2 SHARED-SUPPORT HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P2 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p2_shared_support_v1.py

Harness commit:

3307f18d3fb6b9ce70f09da88d5cc9191f960441.

Git blob SHA:

689b1c9a20559e090c41763c9174da7a43590fad.

Source SHA-256:

17d84f5115a202e20b71bd43c3781342c0a0fe19825b947229f62f8b246ec6f9.

Source bytes:

6865.

DEPENDENCY

Frozen H191-P0 base harness:

source SHA-256:

da6643d35ae6bd5256d400d219702e37ed379ac867ea81583acd2986fa45eabb.

Git blob SHA:

6ac31f5cc3e091be7ef24ea74879903dd21cc2fa.

P2 override:

- world family 20260924390000..20260924390039;
- latent recruiter replaced by:
  joint shared support over:
  all 3209 fixed parent sigma=0.22 basis sites;
- nested shared support:
  2 / 4 / 8;
- reporting labels:
  SUPPORT2 / SUPPORT4 / SUPPORT8.

Everything else:

frozen P0 semantics.

REPRODUCIBILITY

Execute:
two complete runs.

Canonical JSON SHA-256
must:
match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL H191-P2 NON-EVIDENCE PILOT CLOSURE — SHARED PARENT SUPPORT

DATE:
2026-09-20.

STATUS:
COMPLETE / NEAR-COMPETITIVE BUT NEGATIVE FOR SHARED SUPPORT8 /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

17d84f5115a202e20b71bd43c3781342c0a0fe19825b947229f62f8b246ec6f9.

WORLD FAMILY

20260924390000..20260924390039.

40 disjoint surrogate worlds.

RUN 1 OUTPUT SHA-256

bc46cd5cfbf9889e956bad54cbe9757be84f0ac819d3b3dbf5b256ed86b69913.

RUN 2 OUTPUT SHA-256

bc46cd5cfbf9889e956bad54cbe9757be84f0ac819d3b3dbf5b256ed86b69913.

Byte-identical:
PASS.

HELD-OUT NMSE MEDIANS

PROXY8:

A:
0.06776780083329029.

B:
0.016735485499554493.

C:
0.015851036931113737.

Median mean:
0.038650130315266734.

SUPPORT8:

A:
0.061747735732558984.

B:
0.029794173298771.

C:
0.028154303455178664.

Median mean:
0.04276866840107872.

SUPPORT8 - PROXY8
paired world mean NMSE:

median:
+0.01567850683483796.

P90:
+0.054757894223958894.

SUPPORT8 win rate:

25%.

THRESHOLD TELEMETRY

All A/B/C <=0.02:

PROXY8:
12.5%.

SUPPORT8:
5%.

GENERALIZATION

Median mean distillation-to-held-out gap:

PROXY8:
0.022530772815077003.

SUPPORT8:
0.016225066562361452.

SUPPORT8 generalization
is:
not:
the problem.

SHARING

SUPPORT8 decoder concentration median:

0.7112631609028746.

Support spatial spread median:

0.9297723959404396.

Thus:

the shared support
does:
span:
the full geometry

and:
does:
carry:
multi-capability decoder state.

PILOT GATES

1.
SUPPORT8 median mean <= PROXY8:

FAIL narrowly.

2.
Paired win rate >=50%:

FAIL.
Observed:
25%.

3.
No capability median worse by >0.01:

FAIL.

B penalty:
approximately +0.0131.

C penalty:
approximately +0.0123.

A:
slightly better.

4.
Generalization gap <=0.05:

PASS.

5.
Decoder concentration materially below 1:

PASS.

6.
Byte-identical rerun:

PASS.

TECHNICAL INTERPRETATION

A single:
shared:
sigma=0.22
support set

is:
too rigid.

It must compromise
between:
three:
different residual geometries.

The result is:
near:
PROXY8 overall

and:
slightly better for A,

but:
loses:
B/C precision.

This is useful because:

P1 showed:
multi-scale rank 8
CAN:
beat PROXY8.

P2 shows:
fixed parent-scale rank 8
cannot:
reliably do so.

Therefore:

the missing ingredient is:
SCALE FLEXIBILITY,

not:
more learned decoder coefficients.

NEXT JUSTIFIED PILOT

Use:
the existing 3209 parent centers

with:
a FIXED:
three-scale dictionary:

sigma:
0.22,
0.44,
0.88.

These are:
1x,
2x,
4x
the accepted parent basis width.

Jointly recruit:
8 shared:
(center, scale)
dictionary entries.

Store:

24 learned decoder coefficients

plus:

8 shared parent-site indices

and:
8 tiny scale-slot identifiers.

No:
new learned center.
No:
new learned sigma.
No:
new physical cell.

This combines:

P1's successful:
multi-scale shared geometry

with:

P2's:
equal-learned-scalar
fixed-dictionary accounting.

PLAIN-SPEAK SUMMARY

What did we try?

We forced A, B, and C
to share the same eight existing parent basis locations.

What happened?

It came close to PROXY8,
but not close enough.
A improved slightly,
while B and C got worse.

Did it work?

No,
not by the frozen pilot criteria.

What did we learn?

Sharing the support locations is possible,
but forcing every shared factor
to have the same narrow parent width
removes too much flexibility.

Why does it matter?

P1 already showed that eight shared factors can work.
P2 shows we do not need more factors;
we need those eight factors
to operate at more than one spatial scale.

What next?

Keep the factor centers on existing parent sites,
but allow each selected factor
to use one of three fixed,
pre-existing scale choices:
1x,
2x,
or:
4x
the parent width.

That preserves:
24 learned decoder scalars
while restoring:
multi-scale geometry.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
