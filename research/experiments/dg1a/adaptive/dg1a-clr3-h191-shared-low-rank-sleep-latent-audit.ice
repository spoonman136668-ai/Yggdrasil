TITLE: DG-1A-CLR3-H191 — Shared Low-Rank Sleep Latent Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED / PARENT-HARNESS PROVENANCE BLOCK
TRACK: DG-1 / CAPABILITY HIBERNATION / SHARED LOW-RANK RESIDUAL STATE
BRANCH: dg1a-ar
PARENT: dg1a-clr3-h190-sparse-sleep-proxy-basis-distillation-audit.ice
PARENT_CLOSURE: 8f22200ecd1d85b0ec3f656ed1f75e5726833e0c

PURPOSE

H190 established that eight separate reused parent-basis proxies per capability
can keep learned-scheduled A/B/C prediction mismatch inside 2% while retaining
very low B/C active compute, but the stricter 1% known-context fidelity target
remained unmet for B and C even when sparse proxy count increased to sixteen.

H191 asks:

CAN:
THE STRUCTURED
FULL-MINUS-ACTIVE-BRANCH
SLEEP RESIDUAL

BE:
COMPRESSED
INTO:
ONE SMALL
SHARED
LOW-RANK LATENT BASIS

USED BY:
A,
B,
AND:
C

RATHER THAN:
SEPARATE
PER-CAPABILITY
SPARSE PROXY CACHES?

BOUNDARY

Synthetic computational research only.

No living tissue.
No wetware.
No biological implementation claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT PHENOTYPE

Exact accepted H190/H188/H187
WARP48_ROLE48_C stored phenotype.

No:
A/B/C functional coefficient,
B warp parameter,
router parameter,
role coefficient,
physical center,
or:
physical-cell count
may change.

DISTILLATION INPUTS

Per capability context T in {A,B,C}:

128 deterministic unlabeled context coordinates.

Target:

r_T(x)
=
f_full(x)
-
f_T_branch(x).

No task target is read.

No old capability target replay.

No functional retraining.

SHARED LOW-RANK MODEL

For capability T:

r_hat_T(x)
=
sum_{k=1..r}
z_k(x) * d_{k,T}.

The latent functions z_k are SHARED across all capabilities.

Only the decoder coefficient d_{k,T} is capability-specific.

Therefore the learned residual family is explicitly separable across:

input coordinate x
and
capability identity T,

with rank <= r.

LATENT FACTOR FAMILY

Each latent factor is one virtual Gaussian residual factor:

z_k(x)
=
exp(
-||x - c_k||^2
/
(2 * sigma_k^2)
).

Learned state per shared factor:

- center_x;
- center_y;
- sigma;
- decoder_A;
- decoder_B;
- decoder_C.

Thus:

6 learned scalar values
per factor.

These are:
sleep-state latent parameters.

They are NOT:
physical cells.

They do NOT:
alter the parent morphology.

They do NOT:
replace stored A/B/C functional state.

LATENT RANKS

LATENT2.
LATENT4.
LATENT8.

Primary candidate:

LATENT4.

Memory:

LATENT2:
12 learned scalars.

LATENT4:
24 learned scalars.

LATENT8:
48 learned scalars.

H190 PROXY8 comparator:

24 learned coefficients.

Thus LATENT4 is the direct equal-learned-scalar comparator.

FACTOR RECRUITMENT

The factors are recruited greedily and jointly across A/B/C.

Frozen candidate center set:

the union of the 128 unlabeled distillation coordinates
from each of A, B, and C.

Total center candidates:
384.

No task target enters center selection.

Frozen candidate width set:

derive three geometry-only widths from the pooled 384 unlabeled coordinates:

W25:
25th percentile of each point's nearest-neighbor distance.

W50:
50th percentile.

W75:
75th percentile.

Clamp each width to:
>=1e-6.

The width candidate set is frozen after the unlabeled coordinates are generated
and before any held-out test evaluation.

At each recruitment step:

1.
For every not-yet-selected
(center, width)
candidate:

append its shared z_k factor.

2.
For each capability independently:

fit decoder coefficients
for all currently selected factors
by ridge alpha=0.001
to that capability's
128 self-distilled residual targets.

3.
Score the candidate by:

mean across A/B/C
of:

MSE(
latent residual reconstruction,
self-distilled residual
)
/
(
Var(self-distilled residual)
+
1e-12
).

4.
Select:
lowest score.

Tie order:

- lower pooled center index;
- then W25;
- then W50;
- then W75.

5.
Refit all capability decoders jointly under the selected factor set.

Repeat until 8 factors are recruited.

LATENT2,
LATENT4,
and:
LATENT8

are nested prefixes
of the same frozen recruitment sequence.

No:
validation target,
held-out task target,
or:
post-primary tuning
enters recruitment.

COMPARATORS

NO_COMP

Exact H188 scheduled branch-only inference.

PROXY8

Exact accepted H190 practical comparator.

LATENT2

Shared rank-2 latent residual state.

LATENT4

Primary equal-memory comparator.

LATENT8

Higher-rank diagnostic.

INFERENCE

Known-context latent schedule:

selected capability branch
+
that capability's decoder
over:
the shared latent factors.

Learned-router latent schedule:

1.
evaluate the exact frozen H188/H190 B/C routers;

2.
select A, B, or C by the frozen routing rule;

3.
evaluate only the selected functional branch;

4.
evaluate shared latent factors once;

5.
apply only the selected capability decoder.

All non-selected full capability branches remain asleep.

COMPUTE ACCOUNTING

Frozen H188/H190 base:

full all-branch:
3322 proxy units / sample.

Learned scheduler before sleep residual state:

A:
3221.

B:
65.

C:
60.

For rank r:

count:
r latent-factor evaluations
+
r selected-decoder multiply-adds

=
2r
additional proxy units.

LATENT2:

A:
3225.

B:
69.

C:
64.

B-only ratio:
approximately 2.077%.

C-only:
approximately 1.927%.

Equal A/B/C:
approximately 33.695%.

LATENT4:

A:
3229.

B:
73.

C:
68.

B-only ratio:
approximately 2.197%.

C-only:
approximately 2.047%.

Equal A/B/C:
approximately 33.815%.

LATENT8:

A:
3237.

B:
81.

C:
76.

B-only ratio:
approximately 2.438%.

C-only:
approximately 2.288%.

Equal A/B/C:
approximately 34.056%.

This accounting intentionally uses
the same one-basis-response proxy convention
as H188/H190.

PRIMARY METRICS

Per capability:

- full phenotype held-out R^2;
- NO_COMP known-context R^2;
- PROXY8 known-context R^2;
- LATENT2 / LATENT4 / LATENT8 known-context R^2;
- learned-scheduled R^2 for each comparator;
- normalized MSE versus full phenotype;
- residual reconstruction NMSE;
- latent decoder RMS;
- selected factor center / width;
- factor reuse across A/B/C;
- compute;
- learned sleep memory.

Routing:

exact H188/H190.

Wake / switch:

exact 300-switch A->B->C sequence.

No:
refit,
learning,
or:
parameter mutation
during switching.

PRIMARY FACTORIAL

Held-out worlds:
20.

Contexts:
3.

Methods:

NO_COMP,
PROXY8,
LATENT2,
LATENT4,
LATENT8.

60 capability-context rows
with all comparator columns.

PRIMARY ACCEPTANCE SHAPE

H191 supports:
SHARED LOW-RANK SLEEP LATENT
if:

1.
Stored full phenotype:
median A/B/C R^2 >=0.90.

2.
Stored world-level joint competence:
>=90% of worlds have
A, B, and C all R^2 >=0.85.

3.
LATENT4 known-context prediction fidelity:

median normalized MSE
versus full phenotype
<=0.01
for:
A,
B,
C.

4.
LATENT4 learned-scheduled prediction fidelity:

median normalized MSE
<=0.02
for:
A,
B,
C.

5.
LATENT4 known-context task R^2:

median drop from full
<=0.01
for:
A,
B,
C.

6.
LATENT4 learned-scheduled task R^2:

median drop from full
<=0.02
for:
A,
B,
C.

7.
Routing accuracy:
median >=0.95.

8.
LATENT4 B-only compute:
<=3% of full.

9.
LATENT4 C-only compute:
<=3% of full.

10.
LATENT4 equal A/B/C compute:
<=35% of full.

11.
LATENT4 learned sleep memory:
<=24 learned scalar values.

12.
ZERO task-target replay.

13.
ZERO functional retraining.

14.
ZERO new physical cells.

15.
Wake learning cost:
0.

16.
Maximum normalized prediction drift
across the frozen 300-switch sequence:
<=1e-12.

17.
LATENT4 must beat or match PROXY8
on median known-context normalized MSE
for both B and C.

18.
LATENT8 diagnostic:

if LATENT4 fails the strict 1% known-context gate
but LATENT8 passes,
report rank 8 as:
a fidelity rescue
that FAILS the equal-memory objective.

Do not silently redefine this as full H191 success.

19.
LATENT2 diagnostic:

if LATENT2 passes all fidelity/task gates,
report rank 2 as:
the minimum tested sufficient shared rank.

STRONG SUPPORT

H191 receives STRONG support if:

all LATENT4 primary gates pass

AND:

LATENT4 learned-scheduled
B and C
prediction fidelity
are both <=0.01

AND:

LATENT4 uses no more learned sleep memory
than H190 PROXY8.

MIXED / NEGATIVE CONDITIONS

Treat H191 as mixed or negative if:

- LATENT4 cannot clear the strict B/C 1% fidelity gate;
- LATENT4 does not improve B/C over PROXY8;
- only LATENT8 succeeds, requiring doubled learned sleep memory;
- shared factors collapse into capability-specific behavior through decoder magnitude;
- recruitment overfits the 128-point distillation sets;
- active-compute savings materially erode;
- wake requires any refit;
- parent functional state must change.

DO NOT:

- increase rank beyond 8 inside H191;
- change factor family after primary starts;
- add hidden layers;
- add dense learned projections;
- add task labels;
- add physical cells;
- tune on held-out primary outcomes.

SANITY WORLD SEEDS

20260924090000
and:
20260924090001.

Sanity:
NON-EVIDENCE.

PRIMARY WORLD SEEDS

20260924000000
through:
20260924000019.

No:

parent phenotype,
distillation sample count,
factor family,
candidate center set,
width rule,
ridge,
rank set,
routing rule,
compute accounting,
or:
acceptance gate

may change
after:
the first held-out H191 primary world.

PROVENANCE BLOCK

The accepted H190 sandbox harness:

h190_sparse_sleep_proxy_v1.py

SHA-256:

518fb8b96d7118784e3bdd73d5e7d2c1b3395ab8e0be1b36dbb73a01fc3a7bba

is referenced by the accepted H190 closure
but its source is not present in the dg1a-ar repository tree
and was not recoverable from the currently available conversation/library files.

Therefore:

H191 primary execution MUST NOT begin
from a reconstructed parent implementation
while claiming exact H190 inheritance.

The next valid step is:

recover the exact accepted H190 harness bytes
or an exact parent snapshot
whose hash / predictions can be independently matched
to the accepted H190 evidence.

Until then:

H191 remains preregistered,
not executed,
and no result is claimed.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SHARED_LOW_RANK_SLEEP_LATENT

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY DESIGN REVISION 01 — FIXED MULTISCALE PARENT-DICTIONARY LATENT

DATE:
2026-09-20.

STATUS:
RECORDED BEFORE ANY H191 ACCEPTED-LINEAGE SANITY OR PRIMARY EXECUTION.

WHY THIS REVISION EXISTS

H191-P0,
H191-P1,
H191-P2,
and:
H191-P3

were:
explicit:
NON-EVIDENCE
mechanical pilots

performed while:
the accepted H190 parent remained:
provenance-blocked.

They do NOT:
count:
toward:
H191 acceptance.

They DO:
identify:
a mechanical defect
in:
the original:
nearest-neighbor-width
virtual Gaussian factor family.

P0 showed:

nearest-neighbor widths
approximately:
0.017 / 0.028 / 0.042

were:
far below:
the accepted parent RBF scale:
0.22,

causing:
capability-local factor collapse.

P1 showed:

multiscale geometry
restores:
genuine:
cross-capability sharing,

and:
rank-8-like capacity
can:
beat:
separate PROXY8.

P2 showed:

one:
shared:
sigma=0.22
support set

is:
too rigid.

P3 showed:

a fixed:
three-scale:
parent dictionary

can:
combine:

- genuine sharing;
- rank-8 expressive capacity;
- 24 learned decoder scalars;
- PROXY8-equivalent inference overhead.

Therefore:

the ORIGINAL H191 factor family
and:
LATENT4 primary candidate

are:
SUPERSEDED
BEFORE:
accepted-lineage execution.

No:
held-out H191 primary world
has:
been spent.

No:
accepted H191 sanity world
has:
been spent.

REVISED H191 SHARED LATENT FAMILY

Candidate factor dictionary:

for every:
existing:
3209 parent site j,

provide:

D[j,0]:
center = parent_site_j,
sigma = 0.22.

D[j,1]:
center = parent_site_j,
sigma = 0.44.

D[j,2]:
center = parent_site_j,
sigma = 0.88.

These are:

1x,
2x,
4x

the accepted parent RBF scale.

No:
factor center
is learned.

No:
factor width
is learned.

No:
new physical cell
is created.

No:
new morphological coordinate
is created.

Candidate count:

3209 * 3
=
9627.

REVISED JOINT RECRUITMENT

Use:
the same:
128 unlabeled:
full-minus-selected-branch
residual distillation targets
per:
A/B/C context.

Jointly recruit:
one:
shared:
factor sequence

by:
the already-declared:
mean A/B/C
normalized residual reconstruction MSE

with:
ridge alpha:
0.001.

Candidate tie:

lower parent-site index,
then:
0.22,
0.44,
0.88.

Nested candidates:

DICT2.
DICT4.
DICT8.

REVISED PRIMARY CANDIDATE

DICT8.

LEARNED SLEEP MEMORY

DICT8:

8 factors
*
3 capability decoder coefficients

=
24:
learned scalar values.

This exactly matches:
H190 PROXY8
learned coefficient count.

Structural metadata:

DICT8:

8:
shared parent-site indices

+
8:
scale-slot IDs.

H190 PROXY8:

24:
parent-site indices
across:
three:
separate:
8-site caches.

Report:
both:
learned scalar state
and:
structural metadata.

Do NOT:
hide:
the scale-slot metadata.

REVISED COMPUTE

DICT8:

8:
factor evaluations

+
8:
selected capability decoder
multiply-adds

=
16:
sleep-residual proxy operations.

Thus:

learned-scheduled:

A:
3237.

B:
81.

C:
76.

B-only:
approximately:
2.438%.

C-only:
approximately:
2.288%.

Equal A/B/C:
approximately:
34.056%.

Same:
as:
H190 PROXY8.

REVISED COMPARATORS

NO_COMP.

PROXY8.

DICT2.

DICT4.

DICT8.

The old:

LATENT2,
LATENT4,
LATENT8

nearest-neighbor-width
virtual factor family

is:
retained in:
the historical preregistration

but:
is NOT:
an accepted-lineage H191 comparator
after:
this:
pre-primary revision.

REVISED ACCEPTANCE SHAPE

All original:
stored phenotype,
routing,
task performance,
wake,
drift,
physical-cell,
task-replay,
and:
functional-retraining
requirements

remain:
unchanged.

Where:
the original acceptance gates
say:
LATENT4,

substitute:

DICT8.

Specifically:

DICT8:
known-context prediction fidelity

median normalized MSE
<=0.01
for:
A,
B,
C.

DICT8:
learned-scheduled prediction fidelity

median normalized MSE
<=0.02
for:
A,
B,
C.

DICT8:
known-context task R^2
median drop
<=0.01
for:
A/B/C.

DICT8:
learned-scheduled task R^2
median drop
<=0.02.

DICT8:
B-only compute
<=3%.

DICT8:
C-only compute
<=3%.

DICT8:
equal A/B/C compute
<=35%.

DICT8:
learned sleep memory
<=24 learned scalars.

DICT8:
must:
beat or match:
PROXY8

on:
median:
known-context
normalized MSE

for:
both:
B
and:
C.

DICT4 DIAGNOSTIC

If:
DICT4
passes:
all:
fidelity/task gates,

report:
rank 4
as:
the minimum tested
sufficient shared dictionary rank.

DICT2 DIAGNOSTIC

If:
DICT2
passes,
report:
rank 2.

STRONG SUPPORT

H191 strong support now requires:

all:
DICT8 primary gates

AND:

DICT8:
learned-scheduled:
B and C
prediction fidelity

both:
<=0.01

AND:

learned sleep scalar memory
<=24.

MIXED / NEGATIVE

Treat:
H191
as:
mixed / negative
if:

- DICT8 cannot:
  clear:
  strict B/C fidelity;
- DICT8 does not:
  improve:
  B/C
  relative to:
  PROXY8;
- shared support:
  degenerates:
  into:
  capability-local factors;
- all useful factors:
  collapse:
  to:
  one scale
  and:
  cross-capability value
  disappears;
- parent functional state
  must:
  change;
- wake:
  requires:
  refit.

PROVENANCE STATUS

UNCHANGED.

The accepted H190 transient harness
and:
accepted H190 primary matrix bytes

remain:
unrecovered.

Therefore:

H191 accepted-lineage
sanity and:
primary

remain:

NOT STARTED.

This design revision
does NOT:
authorize:
a reconstructed-parent
primary claim.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
