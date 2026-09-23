TITLE: LU-1B LU1BF1 IMITATION CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / IMITATION NOT QUALIFIED / STAY HEAD IMPROVED BUT STILL OUTSIDE BARS
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
a5524c912c67c861be4590a28d0e9f43a5243773

MECHANICAL GATE:
7f3ec3df2fe24fd75be359efd7738f0681e12347

LU1BF1:
bdda0fab372187f71b889065698a7b0bf953f95a

SEED BINDING:
3ba742168d1724336ecc9269a73485ee56f0d79e

DUPLICATE TRAINING GATE:
a322493aa452495b00bba9b17722c0cca395f4cb

FROZEN SOURCE SHA256:
ecc52037e85ac684722e2a0ed2e01641e45e3d239134a5b4b104dc8dbfdd883c

CANONICAL WEIGHT SHA256:
387a6348704e381046e4d0cd05f6a32b2e5da00864e9a9c718f61e2190cd4387

HELD-OUT TEST ARTIFACT

bytes:
1634

SHA256:
0571fb2c2c61deac686de28a5c33381b910b048eea72622bf3b295ed0066cbf4

SCIENTIFIC STATUS

LU1B_IMITATION_QUALIFIED:
FALSE.

DUPLICATE TRAINING

canonical weight bytes:
71105.

weight identity:
PASS.

training metrics identity:
PASS.

H RELEASE

mean absolute error:
0.0114910957.

required:
<=0.02.

PASS.

p99:
0.0510364938.

required:
<=0.08.

PASS.

U RECRUITMENT

mean TV:
0.0196576388.

required:
<=0.03.

PASS.

p95 TV:
0.0498227702.

required:
<=0.08.

PASS.

p99 TV:
0.0685763794.

required:
<=0.12.

PASS.

C/S STAY-DEFECT

mean absolute error:
0.0275619427.

required:
<=0.02.

FAIL.

p95:
0.1192661330.

p99:
0.2435178667.

required p99:
<=0.08.

FAIL.

maximum:
0.6803559661.

COMPARISON TO LU-1A

LU-1A stay mean:
0.0427632498.

LU-1B stay mean:
0.0275619427.

relative mean-error reduction:
35.55%.

LU-1A stay p99:
0.3573133560.

LU-1B stay p99:
0.2435178667.

relative p99-error reduction:
31.85%.

Thus focal-side canonicalization
produced substantial information gain
on the failed stay head,
but did not repair it sufficiently
to cross the frozen qualification bars.

QUIESCENCE

mean U:
0.9987537861.

p01 U:
0.9976257086.

PASS.

OUTPUT SAFETY

finite outputs:
PASS.

bounded / normalized probabilities:
PASS.

parameter ceiling:
PASS.

no global / task / future / position feature:
PASS.

SYMMETRY METRIC

aggregate student symmetry mean:
0.0071733035.

aggregate p99:
0.0385414153.

Both are inside the LU-1A bars.

However:

the additional LU-1B exact committed-pair
canonical-input identity audit
is INVALID AS EXECUTED.

Reason:

the inherited LU-1A swap_input helper
used by the held-out symmetry audit swaps:

C <-> S;
B sign;
LC/LS;
Q-side;
LC3/LS3;

but historically leaves:

FC and FS

unswapped.

LU-1B preregistration required the symmetry-pair generator
to apply the exact full focal-side mirror including:

FC <-> FS.

Therefore the observed:

committed canonical input identity rate = 0.086

must NOT be interpreted as evidence
that the LU-1B canonical transform itself failed.

The pre-freeze mechanical gate directly proved
the exact full mirror canonicalizes byte-identically.

The held-out audit instantiated the wrong mirror family.

This evaluation-harness defect does not rescue LU-1B:

the independently measured held-out stay mean and p99
already fail the frozen qualification bars decisively.

HISTORICAL RESULT

Do not patch LU1BF1.

Do not rerun training.

Do not relax stay thresholds.

Do not increase capacity based only on this result.

Do not reinterpret LU-1B as qualified
even if a corrected observation-only symmetry audit
later proves exact committed-pair identity.

CAUSAL INTERPRETATION

The LU-1A diagnosis was partly correct.

A substantial share of the stay-head error
came from forcing a generic flat MLP
to rediscover an exact C/S focal symmetry.

Canonicalizing SELF versus OPPONENT
removes roughly one third of the error.

But a large residual remains.

Therefore the remaining problem is narrower:

not missing global information;

not H release;

not U recruitment;

not merely C/S coordinate symmetry;

but approximation of the committed-cell
challenge / ECHO / pressure relation
from the still-raw local observation geometry.

NEXT AUTHORIZED STEP

Run an observation-only residual stay-head audit
using:

the already-frozen LU-1B canonical weights;

the already-open held-out LU-1B test set;

and, separately,
a corrected exact full C/S mirror-pair generator
for representation verification only.

The diagnostic may stratify residual stay error by:

CHALLENGE / SUPPORT / NEUTRAL;

ECHO-dominant versus non-ECHO challenge;

teacher stay range;

pressure range;

opposition;

own aligned B;

qraw;

qecho;

qeff;

and distance to the teacher's pressure=0 hinge.

It may not:

retrain;

change weights;

change model size;

change inputs;

change thresholds;

or evaluate alternative hyperparameters.

Use the residual structure
to preregister one narrow LU-1C experiment.

PLAIN-SPEAK INTERPRETATION

Changing the cell's point of view helped a lot.

The neural cell no longer had to learn
"C means me over here,
but S means me over there."

That removed about a third
of the error in the hard commitment decision.

But it did not solve the whole problem.

The remaining hard case is still:

a committed cell is being challenged,
its short-term echo memory is protecting it,
and the network has to understand
how several local quantities cancel each other.

So we learned two things.

First:
the coordinate system really was part of the problem.

Second:
it was not the whole problem.

We still do not put the neural updater
inside the organism.

Next we inspect the remaining stay errors
without retraining
and isolate the next single representational problem.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
