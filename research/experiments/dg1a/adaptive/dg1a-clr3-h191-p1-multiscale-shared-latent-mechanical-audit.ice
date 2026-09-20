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


FINAL H191-P1 NON-EVIDENCE PILOT CLOSURE — MULTISCALE SHARED LATENT

DATE:
2026-09-20.

STATUS:
COMPLETE / MAJOR MECHANICAL IMPROVEMENT /
MIXED-NEGATIVE FOR EQUAL-MEMORY LATENT4 /
POSITIVE FOR RANK-8 SHARED-LATENT EXPRESSIVITY /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

c49c4ed0c8a262db1d448c440e907648dce76f287b07f3263dd49d714447654f.

FROZEN BASE HARNESS SHA-256

da6643d35ae6bd5256d400d219702e37ed379ac867ea81583acd2986fa45eabb.

PILOT FAMILY

20260924290000..20260924290039.

40 disjoint surrogate worlds.

Two complete unchanged executions.

RUN 1 OUTPUT SHA-256

4afd099f466b3ea98bf2e5813b86c368ac8f71eea185ba4862c2d685a82f1bf2.

RUN 2 OUTPUT SHA-256

4afd099f466b3ea98bf2e5813b86c368ac8f71eea185ba4862c2d685a82f1bf2.

Byte-identical:
PASS.

HELD-OUT NMSE MEDIANS

PROXY8:

A:
0.03241502652003879.

B:
0.016835539393401516.

C:
0.028387585788391533.

Median world mean-capability:
0.044459672063039656.

P90:
0.08484080880226934.

LATENT2:

A:
0.23144076565337446.

B:
0.1486988166774938.

C:
0.33149698202110267.

Median mean:
0.28807459200432245.

LATENT4:

A:
0.0583747530645571.

B:
0.051993222349586324.

C:
0.05323692969063189.

Median mean:
0.07665749939478497.

P90:
0.2500971601257017.

LATENT8:

A:
0.01707470863008274.

B:
0.012893115338164434.

C:
0.010655719862411948.

Median mean:
0.021760770487428988.

P90:
0.0700951740800779.

PAIRED VALUE

LATENT4 minus PROXY8
median paired world mean-NMSE:

+0.02512589707836315.

LATENT4 win rate:

17.5%.

Thus:
equal-memory LATENT4
does NOT:
beat PROXY8.

LATENT8 minus PROXY8
median paired world mean-NMSE:

-0.01609527654969589.

LATENT8 win rate:

75%.

Thus:
rank 8
usually:
beats:
per-capability PROXY8
on:
the surrogate family.

STRICT THRESHOLD TELEMETRY

All A/B/C <=0.01:

PROXY8:
0%.

LATENT4:
0%.

LATENT8:
20%.

All A/B/C <=0.02:

PROXY8:
7.5%.

LATENT4:
0%.

LATENT8:
32.5%.

SHARING DIAGNOSTIC

P0 LATENT4
decoder concentration median:

0.9999995325750876.

P1 LATENT4:

0.6641544409680186.

This is:
a major reduction.

The multiscale widths
therefore:
convert:
the factors
from:
capability-local islands

into:
meaningfully shared:
cross-capability factors.

LATENT4
selected-center spread median:

approximately:
0.83523.

This is:
consistent with:
factors spanning:
the larger pooled geometry.

GENERALIZATION

Median mean:
distillation-to-held-out NMSE gap:

PROXY8:
0.023393433086399726.

LATENT4:
0.009602029826643727.

LATENT8:
0.006288384205812363.

Thus:
the corrected:
shared latent

does NOT:
show:
the P0 narrow-factor
generalization failure.

P1 PILOT CHECKS

1.
LATENT4 improves strongly over P0 LATENT4:

PASS.

P0:
approximately 2.906.

P1:
approximately 0.0767.

2.
Decoder concentration materially below P0:

PASS.

3.
LATENT4 <= PROXY8
or within 0.02 absolute mean NMSE:

FAIL.

Observed median paired delta:
approximately +0.0251.

4.
LATENT8 improves LATENT4:

PASS strongly.

5.
Median distillation-to-held-out gap <=0.05:

PASS.

6.
Byte-identical rerun:

PASS.

FINAL TECHNICAL INTERPRETATION

H191-P1 shows:

the low-rank/shared-latent idea
is mechanically viable

once:
candidate factor scale
matches:
functional / cross-context geometry.

The P0 failure
was:
primarily:
a width-generation defect.

However:

the equal-memory:
rank-4:
six-scalars-per-factor
representation

does NOT:
have enough capacity
on:
this surrogate family

to:
match:
separate PROXY8 caches.

Rank 8:

does:
beat:
PROXY8
on:
the median

and:
wins:
75%
of:
paired worlds.

But:

under:
the current H191 accounting,

rank 8
stores:
48 learned scalar values

versus:
24
for:
H190 PROXY8.

Therefore:

P1 suggests:
the next design problem
is NOT:
whether:
shared residual factors
can work.

They can.

The problem is:

HOW TO GET
RANK-8-LIKE
SHARED EXPRESSIVITY

AT:
APPROXIMATELY
24 LEARNED SCALARS.

NEXT JUSTIFIED MECHANICAL EXPERIMENT

Test:

SHARED-SUPPORT
PARENT-BASIS LATENT.

Use:

one jointly recruited
shared set
of:
existing fixed parent Gaussian basis sites

with:

capability-specific decoder coefficients.

At rank 8:

learned coefficients:
8 * 3
=
24.

Shared support indices:

8 structural metadata entries.

This directly compares against:
H190 PROXY8:

24 learned coefficients

but:
three separate:
8-site support sets

=
24 structural site indices.

The shared-support representation
therefore:
can provide:
rank-8 shared expressive capacity

without:
doubling:
learned scalar state.

PLAIN-SPEAK SUMMARY

What did we try?

We fixed the factor sizes
so the shared latent could actually span
the same kinds of spatial scales
used by Yggdrasil's cognitive body.

What happened?

Performance improved enormously.
The factors also started being genuinely shared
instead of each belonging to only one capability.

Did it work?

Partly.

Four shared factors were still not enough
to beat the old PROXY8 approach.

Eight shared factors were enough:
they beat PROXY8 in 75% of the surrogate worlds
and had better median error.

What did we learn?

The shared-latent idea is still alive.
Its problem is now memory efficiency,
not basic representational ability.

Why does it matter?

The goal is not merely to compress sleeping capabilities.
We need shared coordination state
that grows slower than capability count.
Rank 8 looks useful,
but paying 48 learned scalars for it
would miss the equal-memory target.

What should we try next?

Keep eight shared factors,
but anchor them to existing parent basis sites
so their geometry does not need three learned numbers per factor.

Then only the three A/B/C decoder weights per factor are learned:
8 factors times 3 capabilities = 24 learned scalars.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
