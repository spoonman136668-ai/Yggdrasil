TITLE: DG-1A-CLR3-H191-P1 — Multi-Scale Shared Sleep Latent Mechanical Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE IMPLEMENTATION PILOT / NOT H191 PRIMARY
TRACK: DG-1 / CAPABILITY HIBERNATION / SHARED LOW-RANK RESIDUAL STATE
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p0-surrogate-mechanical-audit.ice

PURPOSE

H191-P0 demonstrated a mechanical defect in the original H191 width generator.

Nearest-neighbor width quantiles measured sample spacing:
approximately 0.017 / 0.028 / 0.042.

The accepted parent RBF width is:
0.22.

As a result:
the nominally shared factors became capability-local islands.

H191-P1 asks:

DOES A MODEL-SCALE + REGIONAL + GLOBAL
GEOMETRY-ONLY WIDTH SET
ALLOW THE SAME H191 GREEDY SHARED FACTOR RECRUITER
TO ACTUALLY SHARE RESIDUAL STRUCTURE ACROSS A/B/C?

THIS PILOT IS NON-EVIDENCE.

It cannot:
- pass/fail H191;
- replace H190;
- enter H191 primary statistics;
- authorize accepted-lineage execution.

BOUNDARY

Synthetic computational research only.
No living tissue.
No wetware.
No biological implementation claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT PILOT SEMANTICS

Reuse H191-P0 exactly for:

- 3209-site unit-disk parent geometry;
- sigma=0.22 parent RBF proxy basis;
- A/B/C context geometry;
- six shared Gaussian source factors;
- capability-specific 0.10 sinusoidal remainder;
- 128 distillation coordinates;
- 512 held-out coordinates;
- PROXY8 OMP comparator;
- H191 greedy shared-factor recruitment;
- ridge alpha=0.001;
- ranks 2/4/8;
- metrics and serialization.

Only the declared items below change.

DISJOINT PILOT WORLD FAMILY

20260924290000
through:
20260924290039.

40 worlds.

No P0 world is reused.

CORRECTED WIDTH CANDIDATES

For pooled 384 unlabeled distillation coordinates:

W0 — PARENT_SCALE:

0.22.

This is the exact accepted DG-1 parent Gaussian basis width.

W1 — REGIONAL:

25th percentile
of all unique off-diagonal pooled pairwise Euclidean distances.

W2 — GLOBAL:

50th percentile
of all unique off-diagonal pooled pairwise Euclidean distances.

No:
residual value,
task target,
held-out value,
or:
capability output
enters:
the width calculation.

RATIONALE

The latent must span:

- local parent functional scale;
- regional cross-site structure;
- global cross-context structure.

Nearest-neighbor spacing is not a functional scale.

The fixed 0.22 parent width is inherited model geometry,
not tuned from P0 residual outcomes.

Pairwise quartiles are:
unlabeled coordinate geometry only.

ALL OTHER H191 RECRUITMENT IS UNCHANGED

Candidate centers:

pooled 384 distillation coordinates.

Candidate ordering:

center-major,
then:
PARENT_SCALE,
REGIONAL,
GLOBAL.

At each step:

select the candidate minimizing
mean A/B/C normalized residual reconstruction MSE
after capability-specific ridge decoder refits.

Ranks:

2,
4,
8.

LATENT4 remains:
24 learned scalars
under H191 accounting.

PILOT DIAGNOSTICS

P1 is mechanically encouraging if:

1.
LATENT4 median mean-capability held-out NMSE
is lower than:
P0 LATENT4.

2.
LATENT4 decoder concentration median
is materially below:
P0 value 0.9999995.

3.
LATENT4 median mean held-out NMSE
is <= PROXY8
OR:
within 0.02 absolute NMSE
while using the equal learned-scalar budget.

4.
LATENT8 improves or matches LATENT4.

5.
Median distillation-to-held-out gap
does not exceed:
0.05.

6.
Two complete reruns
are byte-identical.

These are:
NON-EVIDENCE mechanical diagnostics,
not:
H191 acceptance gates.

NO POST-RUN TUNING

After the first P1 world executes,
do not change:

- source family;
- world family;
- width set;
- coordinate counts;
- recruitment;
- ranks;
- comparator;
- ridge;
- metrics.

If P1 remains strongly negative:

do NOT:
keep trying width quantiles.

Treat:
single-center Gaussian shared factors

as:
a likely wrong latent family

and:
move to:
a qualitatively different shared residual representation
before H191 accepted-lineage primary.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

PROVENANCE

evidence_class =
NON_EVIDENCE_SURROGATE_MECHANICAL_AUDIT

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P1 MULTISCALE LATENT HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P1 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p1_multiscale_shared_latent_v1.py

Harness commit:

6cfcbc20b1f4910dec8864ed160d95cbc548c536.

Git blob SHA:

67c5ba8d185a69e7f3fe9dfd0cb3d0053bd44029.

Source SHA-256:

c49c4ed0c8a262db1d448c440e907648dce76f287b07f3263dd49d714447654f.

Source bytes:

1458.

DEPENDENCY

Imports the frozen H191-P0 base harness:

research/experiments/dg1a/adaptive/harnesses/h191_p0_surrogate_mechanical_v1.py

Pinned base source SHA-256:

da6643d35ae6bd5256d400d219702e37ed379ac867ea81583acd2986fa45eabb.

Pinned base Git blob SHA:

6ac31f5cc3e091be7ef24ea74879903dd21cc2fa.

P1 overrides only:

- world start:
  20260924290000;
- world count:
  40;
- width generator:
  [0.22, pooled pairwise Q25, pooled pairwise Q50];
- output schema label.

All other generator,
comparator,
recruitment,
metric,
and serialization semantics
come from:
the frozen P0 base harness.

REPRODUCIBILITY

Run the complete P1 matrix twice.
Canonical JSON output SHA-256
must match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
