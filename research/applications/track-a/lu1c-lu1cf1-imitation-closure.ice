TITLE: LU-1C LU1CF1 IMITATION CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / IMITATION NOT QUALIFIED / STRUCTURED MEAN AGGREGATION INSUFFICIENT
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
c77e622a08d6bd15c74c75ff61ddc5aefb9ade2d

MECHANICAL GATE:
c7909617581b676d0e244ce2a1af86222c2867e6

LU1CF1:
10f4a6d4cd012dd200d6df8e0e1e56f38e2606ec

SEED BINDING:
bb3ff579a66004334f969e5a337d69ed3e5cfc58

DUPLICATE TRAINING GATE:
715b4e36d1881539e656fd258726ab6b25859235

FROZEN SOURCE SHA256:
e4abb65ac7abf2909cb8df5ceb7f3bfd8bcf142bf5a7c6453e90fbd4e828f7c1

CANONICAL WEIGHT SHA256:
c3cb57e6ac6da729a045bc4866c5020b404f3713c9bd03fced60e64757e7112b

HELD-OUT TEST ARTIFACT

bytes:
1589.

SHA256:
ebb8f916f009c1f277676501974c222fc0db35debace1c09f29309799e9ef708.

SCIENTIFIC STATUS

LU1C_IMITATION_QUALIFIED:
FALSE.

MODEL

shared cell encoder:
9 -> 32 -> 32.

six-neighbor aggregate:
arithmetic mean.

focal-extra encoder:
7 -> 16.

trunk:
80 -> 64 -> 32 -> 6.

trainable parameters:
8966.

This is approximately half the trainable parameter count
of LU-1A / LU-1B.

DUPLICATE TRAINING

canonical weight bytes:
36213.

weight identity:
PASS.

training metrics identity:
PASS.

H RELEASE

mean absolute error:
0.0101828245.

required:
<=0.02.

PASS.

p99:
0.0409458219.

required:
<=0.08.

PASS.

U RECRUITMENT

mean TV:
0.0176813159.

required:
<=0.03.

PASS.

p95 TV:
0.0486120634.

required:
<=0.08.

PASS.

p99 TV:
0.0708016691.

required:
<=0.12.

PASS.

C/S STAY-DEFECT

mean absolute error:
0.0253735475.

required:
<=0.02.

FAIL.

p95:
0.1059142917.

p99:
0.2891320121.

required p99:
<=0.08.

FAIL.

maximum:
0.6110932231.

COMPARISON TO LU-1B

LU-1B stay mean:
0.0275619427.

LU-1C stay mean:
0.0253735475.

relative mean-error reduction:
7.94%.

LU-1B stay p99:
0.2435178667.

LU-1C stay p99:
0.2891320121.

The high-error tail therefore worsened
despite a modest mean improvement.

COMPARISON TO LU-1A

LU-1A stay mean:
0.0427632498.

LU-1C stay mean:
0.0253735475.

relative mean-error reduction:
40.67%.

Thus the learned-updater lineage has made
substantial progress from the original flat raw representation,
but the stay law is still not inside the frozen envelope.

SYMMETRY

corrected committed C/S canonical identity:
1000 / 1000.

identity rate:
1.0.

student symmetry mean:
0.0071110506.

required:
<=0.02.

PASS.

student symmetry p99:
0.0559851903.

required:
<=0.08.

PASS.

Therefore focal-side symmetry remains repaired.

QUIESCENCE

mean U:
0.9939010143.

required:
>=0.98.

PASS.

p01 U:
0.9924244881.

required:
>=0.90.

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

NEIGHBOR PERMUTATION PROBE

maximum trained-model logit difference
under a permutation of the six nonfocal neighbors:

3.814697265625e-06.

The frozen implementation probe used tolerance:

1e-06.

Therefore the frozen runtime probe:
FAIL.

The architecture itself uses one shared cell encoder
and an arithmetic mean,
so it is algebraically permutation-invariant.

The observed difference is consistent with
floating-point reduction-order sensitivity.

Do not change the frozen tolerance
after seeing this result.

This probe failure is not needed
to decide LU-1C qualification:

the stay mean and stay p99
already fail independently.

CAUSAL INTERPRETATION

LU-1C tested the hypothesis
that a generic flat-vector representation
was the main remaining obstacle.

That hypothesis receives only partial support.

The structured relational model:

uses fewer parameters;

preserves H release;

preserves U recruitment;

preserves focal-side symmetry;

and modestly improves mean stay error.

But it does not solve the committed-cell law.

Its stay tail is worse than LU-1B.

Therefore symmetric neighbor encoding plus mean aggregation
is not sufficient to learn
the exact conditional challenge / ECHO / pressure relation
inside the frozen error bars.

The result argues against
simple parameter inflation
and against merely changing neighborhood ordering.

NEXT AUTHORIZED STEP

Run an observation-only residual audit
on the already-open LU-1C test set
and canonical weights.

Compare directly with LU-1B on:

SUPPORT / CHALLENGE / NEUTRAL;

ECHO-active versus no-ECHO;

ECHO-dominant challenge;

teacher stay range;

pressure;

opposition;

own aligned evidence;

qraw;

qecho;

qeff.

The diagnostic should determine
whether the residual still has
the same conditional-ECHO signature
or whether mean aggregation introduced
a different information-compression failure.

No retraining.

No new hyperparameter.

No changed threshold.

If the conditional-ECHO signature remains,
the next narrow experiment should test
an explicit multiplicative / gated local interaction operator
while preserving the same OBS-V1 information boundary
and <=18000 parameter ceiling.

PLAIN-SPEAK INTERPRETATION

Giving every neighbor
the same little neural encoder
was a sensible idea,
but it was not enough.

The smaller network still learned
uncertainty release
and recruitment well.

It also kept the corrected
"me versus the other side" symmetry.

But the hardest decision remains:

when a committed cell
should hold its ground under local pressure.

The average stay error improved a little.

The worst cases did not.

In fact the tail got worse.

So the problem is not simply
that the old network saw its neighbors
in an awkward list order.

The next step is to inspect
whether the neural cell is still mishandling
the rule that ECHO memory matters
only under challenge.

If that signature remains,
we should test a network with an explicit
learned gating/multiplicative interaction shape,
not a bigger network
and not more information.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
