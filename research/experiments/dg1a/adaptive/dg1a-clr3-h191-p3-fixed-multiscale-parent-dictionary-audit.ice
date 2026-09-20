TITLE: DG-1A-CLR3-H191-P3 — Fixed Multiscale Parent-Dictionary Shared Latent Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE IMPLEMENTATION PILOT / NOT H191 PRIMARY
TRACK: DG-1 / CAPABILITY HIBERNATION / SHARED MULTISCALE RESIDUAL DICTIONARY
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p2-shared-support-parent-basis-mechanical-audit.ice

PURPOSE

P1 showed:
multiscale rank-8 shared factors can beat PROXY8,
but learned factor geometry costs too much.

P2 showed:
one shared fixed sigma=0.22 parent support set is near-competitive,
but too rigid for B/C.

P3 combines both findings.

QUESTION

CAN:
EIGHT SHARED FACTORS
FROM:
A FIXED MULTISCALE PARENT DICTIONARY

MATCH OR BEAT:
SEPARATE PROXY8

WHILE USING:

24 learned decoder coefficients

and:
NO learned factor geometry?

BOUNDARY

NON-EVIDENCE surrogate mechanical pilot only.
No living tissue.
No wetware.
No biological implementation claim.
No production modification.
No canonical scientific execution.
No STAB-18-R1 execution.

DISJOINT WORLD FAMILY

20260924490000
through:
20260924490039.

40 worlds.

No P0/P1/P2 world reuse.

BASE SEMANTICS

Reuse frozen H191-P0 for:

- 3209 parent sites;
- context geometry;
- surrogate residual family;
- 128 distillation + 512 held-out points / capability;
- separate PROXY8 comparator;
- ridge alpha=0.001;
- metrics;
- canonical serialization.

FIXED MULTISCALE DICTIONARY

For every existing parent site j,
provide three VIRTUAL residual factors:

S0:
sigma = 0.22.

S1:
sigma = 0.44.

S2:
sigma = 0.88.

These are exactly:

1x,
2x,
4x

the accepted parent RBF width.

The scale family is:
hard-coded architecture,
not learned state.

No:
new center,
new physical cell,
learned center,
or:
learned sigma.

CANDIDATE COUNT

3209 parent centers
*
3 fixed scales

=
9627 candidate factors.

Candidate order:

lower parent-site index first,
then:
S0,
S1,
S2.

SHARED RECRUITMENT

Jointly recruit ONE shared sequence
across A/B/C.

At each step:

- append candidate factor;
- independently ridge-refit capability decoders;
- score mean A/B/C normalized distillation MSE;
- choose lowest score;
- tie by candidate order.

Nested prefixes:

DICT2.
DICT4.
DICT8.

MEMORY

DICT8 learned state:

8 factors
*
3 capability decoders

=
24 learned scalars.

Structural metadata:

8 parent-site indices
+
8 scale slots.

Scale slot:
2 bits sufficient conceptually.

Comparator PROXY8:

24 learned coefficients
+
24 parent-site indices.

Thus:

DICT8 matches:
PROXY8
learned scalar count

while:
using:
one-third
as many:
site IDs,

plus:
8 small:
scale-slot IDs.

COMPUTE

DICT8:

8 shared factor evaluations
+
8 selected-capability decoder multiply-adds

=
16 sleep-residual proxy operations.

Same:
as H190 PROXY8.

Therefore inherited ratios:

B-only:
approximately 2.438%.

C-only:
approximately 2.288%.

Equal A/B/C:
approximately 34.056%.

MECHANICAL ENCOURAGEMENT

P3 is encouraging if:

1.
DICT8 median mean-capability held-out NMSE
<= PROXY8.

2.
DICT8 paired win rate
>=50%.

3.
No capability median
is worse than PROXY8
by:
>0.01.

4.
Median distillation-to-held-out mean gap
<=0.05.

5.
Decoder concentration median
<0.90.

6.
At least two scale slots
are recruited materially
across the 40 worlds.

7.
Two reruns
are byte-identical.

If P3 succeeds:

this becomes:
the preferred pre-primary H191 factor architecture candidate.

If P3 fails:

do NOT:
add more scale slots
or:
increase rank.

Move to:
a distributed fixed low-rank factor family
rather than:
more sparse dictionary expansion.

NO POST-RUN TUNING

No design change after:
first P3 world.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
