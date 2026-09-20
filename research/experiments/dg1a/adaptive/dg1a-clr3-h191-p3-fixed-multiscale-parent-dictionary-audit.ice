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


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P3 MULTISCALE DICTIONARY HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P3 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p3_multiscale_dictionary_v1.py

Harness commit:

e80720cf94d312e88b9599e1b505dcc080aab42f.

Git blob SHA:

1954ce689973f36d0a44d36271a0f002de0150d9.

Source SHA-256:

75770a9d05d09db8ab7cdc054e89d209402a5f7d8c3ae0dd83896985bf32fbd7.

Source bytes:

6271.

DEPENDENCIES

H191-P2 harness Git blob:
689b1c9a20559e090c41763c9174da7a43590fad.

H191-P0 base harness Git blob:
6ac31f5cc3e091be7ef24ea74879903dd21cc2fa.

P3 fixed scale family:

0.22,
0.44,
0.88.

P3 world family:

20260924490000..20260924490039.

REPRODUCIBILITY

Two complete unchanged executions required.
Canonical output SHA-256 must match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL H191-P3 NON-EVIDENCE PILOT CLOSURE — FIXED MULTISCALE PARENT DICTIONARY

DATE:
2026-09-20.

STATUS:
COMPLETE / POSITIVE MECHANICAL RESULT /
PREFERRED PRE-PRIMARY H191 ARCHITECTURE CANDIDATE /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

75770a9d05d09db8ab7cdc054e89d209402a5f7d8c3ae0dd83896985bf32fbd7.

WORLD FAMILY

20260924490000..20260924490039.

40 disjoint surrogate worlds.

RUN 1 OUTPUT SHA-256

31b4323d89bae07b18dc4b16e275e07f1e50155ba23de04b6f9f78e23b1fd6b8.

RUN 2 OUTPUT SHA-256

31b4323d89bae07b18dc4b16e275e07f1e50155ba23de04b6f9f78e23b1fd6b8.

Byte-identical:
PASS.

HELD-OUT NMSE MEDIANS

PROXY8:

A:
0.04646161866951014.

B:
0.016398062395223085.

C:
0.014705166690107557.

Median mean-capability:
0.04896006369034207.

P90:
0.08926711794611325.

DICT8:

A:
0.02051179172019153.

B:
0.00923586740080381.

C:
0.009137813307912388.

Median mean-capability:
0.014578474604598473.

P90:
0.043675095213733896.

PAIRED DICT8 VALUE

DICT8 minus PROXY8
median paired world mean NMSE:

-0.02506070006548636.

P90 paired delta:

+0.005839538729099265.

DICT8 paired win rate:

77.5%.

Thus:

DICT8:
usually:
outperforms:
three separate:
PROXY8 sparse caches

despite:
using:
the same:
24 learned decoder scalars.

STRICT THRESHOLD TELEMETRY

All A/B/C <=0.01:

PROXY8:
0%.

DICT8:
22.5%.

All A/B/C <=0.02:

PROXY8:
10%.

DICT8:
32.5%.

GENERALIZATION

Median mean distillation-to-held-out NMSE gap:

PROXY8:
0.018783871375324605.

DICT8:
0.0062777152226424875.

PASS:
no gross distillation overfit.

SHARING

DICT8 decoder concentration median:

0.7031486024701217.

Frozen pilot threshold:
<0.90.

PASS.

DICT8 center spread median:

0.8963925930612806.

Thus:
selected factors
span:
the organism-scale geometry.

SCALE USE

Across:
40 worlds
*
8 selected factors
=
320 selections.

Scale-slot counts:

sigma 0.22:
178.

sigma 0.44:
104.

sigma 0.88:
38.

All three:
are materially used.

The architecture does NOT:
collapse:
to:
one scale.

MEMORY

DICT8 learned scalar state:

8 factors
*
3 decoders

=
24 learned scalars.

Same as:
H190 PROXY8.

Structural metadata:

DICT8:
8 site IDs
+
8 scale slots.

H190 PROXY8:
24 site IDs
across:
three separate capability caches.

COMPUTE

DICT8 sleep-residual overhead:

8 factor evaluations
+
8 selected decoder multiply-adds

=
16 proxy operations.

Same:
as:
H190 PROXY8.

Inherited scheduled ratios:

B-only:
approximately:
2.438%.

C-only:
approximately:
2.288%.

Equal A/B/C:
approximately:
34.056%.

PILOT GATE REVIEW

1.
DICT8 median mean <= PROXY8:

PASS.

2.
DICT8 paired win rate >=50%:

PASS:
77.5%.

3.
No capability median worse by >0.01:

PASS.

All three capability medians:
improve.

4.
Generalization gap <=0.05:

PASS.

5.
Decoder concentration <0.90:

PASS.

6.
At least two scale slots materially recruited:

PASS:
all three.

7.
Byte-identical rerun:

PASS.

FINAL TECHNICAL INTERPRETATION

P3 provides:
a clean:
mechanical proof-of-design

for:
a small:
shared sleep residual representation

with:

- eight:
  shared factors;
- fixed:
  pre-existing:
  parent centers;
- fixed:
  architectural:
  1x / 2x / 4x scales;
- 24:
  learned decoder scalars;
- one:
  shared support;
- same:
  sleep-inference overhead
  as:
  H190 PROXY8.

This resolves:
the P1 memory problem

without:
returning:
to:
P2's single-scale rigidity.

IMPORTANT LIMIT

This is:
NOT:
accepted H191 evidence.

The real:
H190 residual matrix
was not used.

Therefore:

do NOT:
claim:
that:
DICT8
has:
passed:
H191.

What P3 justifies is:

PRE-PRIMARY ARCHITECTURE SELECTION.

The accepted-lineage H191 primary,
if exact H190 parent evidence becomes available,
should test:

DICT2,
DICT4,
DICT8

using:
the fixed:
parent-center
sigma:
0.22 / 0.44 / 0.88
dictionary

instead of:
the original:
nearest-neighbor-width
virtual-factor family.

NEXT RESEARCH QUESTION

Before:
accepted-lineage recovery,

stress:
DICT8
against:
increasing:
shared residual complexity.

Question:

does:
eight-factor:
shared coordination

remain:
stable

when:
the latent residual source
contains:
4,
6,
8,
or:
12
shared generating factors

and:
increasing:
capability-specific remainder?

This tests:
whether:
P3 success
is:
a narrow:
six-source
surrogate coincidence

or:
a useful:
capacity regime.

PLAIN-SPEAK SUMMARY

What did we try?

We gave Yggdrasil eight shared sleep factors
anchored to existing parent-cell locations,
but let each factor choose one of three fixed sizes:
normal,
2x,
or:
4x.

What happened?

It worked much better than the old separate PROXY8 caches
on this controlled surrogate test.

Did it work?

Yes,
for the mechanical pilot.

It beat PROXY8 in:
77.5%
of worlds,
improved the median error for:
A,
B,
and:
C,
and:
used exactly:
24 learned decoder numbers.

What did we actually learn?

The useful combination is:

shared support
+
multiple fixed spatial scales.

Shared support alone was too rigid.
Learned multiscale factors worked
but cost too much memory.

The fixed multiscale dictionary
gets both benefits at once.

Why does it matter?

This is the first tested design in this H191 line
that gives us:
rank-8-like shared expressive power

without:
paying more learned scalar memory
or:
more inference compute
than H190 PROXY8.

What should we try next?

Stress it.

Make the synthetic residual structure harder
and determine where eight shared factors stop being enough.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
