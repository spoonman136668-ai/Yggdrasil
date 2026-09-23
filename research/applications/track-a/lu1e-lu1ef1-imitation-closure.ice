TITLE: LU-1E LU1EF1 IMITATION CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / IMITATION NOT QUALIFIED / STATE-CONDITIONED ROUTING DOES NOT REPAIR STAY TAIL
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
1adbbfc33514fc3143f98a5d85ffb4d5b99ae3eb

MECHANICAL GATE:
4551c390302c57fc4cc1e91c629db3842fb5f01c

LU1EF1:
f459273c897a7bd889b6de2ec2d9720374215327

SEED BINDING:
cdad7f1577313160a419fcec07b27c222ebd6879

DUPLICATE TRAINING GATE:
2ce6a39af7b69211efd78d6cd5f2e884bc247495

FAILED GITHUB-HOSTED EXECUTION REQUEST:
dd7a015956dc2e8a49bf46fc7c57964feb2dc16f

EXECUTION ENVIRONMENT

The GitHub-hosted isolated workflow failed before step 1.
Job steps were null.
That event is infrastructure failure, not scientific evidence.

Canonical training was reproduced in the isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

CANONICAL TRAINING REPRODUCTION

Accepted canonical weight SHA256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

Reproduced weight SHA256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

MATCH:
TRUE.

Accepted training-metrics SHA256:
e5a54d75e37b475653a3bb3384fa27c791f928c0d50953a105a80144dd3d0c8e

Reproduced training-metrics SHA256:
e5a54d75e37b475653a3bb3384fa27c791f928c0d50953a105a80144dd3d0c8e

MATCH:
TRUE.

Validation total equal-head loss:
1.2430675029754639

Thus the held-out test was opened against the exact accepted canonical LU-1E weights.

HELD-OUT TEST

examples:
12000

held-out artifact SHA256:
6b3fe72591eb2a3bf151c328a24c185eaa0879b429e2b8b6cb20173a6c2dadbc

SCIENTIFIC STATUS

LU1E_IMITATION_QUALIFIED:
FALSE.

H RELEASE

mean absolute error:
0.0138821314

required:
<= 0.02

PASS.

p99:
0.0378843547

required:
<= 0.08

PASS.

U RECRUITMENT

mean TV:
0.0149092892

required:
<= 0.03

PASS.

p95 TV:
0.0454820026

required:
<= 0.08

PASS.

p99 TV:
0.0693288447

required:
<= 0.12

PASS.

C/S STAY-DEFECT

mean absolute error:
0.0230781152

required:
<= 0.02

FAIL.

p95:
0.0990227163

p99:
0.2420497854

required p99:
<= 0.08

FAIL.

maximum:
0.5921896696

COMPARISON TO LU-1D

LU-1D stay mean:
0.0231283040

LU-1E stay mean:
0.0230781152

The mean changes only marginally.

LU-1D stay p99:
0.2005912924

LU-1E stay p99:
0.2420497854

The high-error tail worsens.

Therefore exact categorical state-conditioned relation routing
does not repair the remaining stay-defect approximation failure.

SYMMETRY

student symmetry mean:
0.0050850211

required:
<= 0.02

PASS.

student symmetry p99:
0.0327598100

required:
<= 0.08

PASS.

The held-out committed canonical-input identity field reported:
0.075.

This identity measurement is INVALID AS A TEST OF THE CANONICAL TRANSFORM.

Reason:

the LU-1E held-out symmetry implementation inherits
LU-1A swap_input through a=b.a.

That historical helper does not perform
the full preregistered committed mirror,
specifically including FC <-> FS.

The same harness defect was already identified
and corrected observation-only after LU-1B.

The LU-1E pre-freeze mechanical gate proved
the exact full committed mirror canonicalizes identically.

Do not patch LU1EF1.

Do not reinterpret the 0.075 value as a failure
of the focal-side canonical transform.

This harness defect does not affect the scientific verdict:

STAY mean and STAY p99 fail independently and decisively.

QUIESCENCE

mean U:
0.9967157245

required:
>= 0.98

PASS.

p01 U:
0.9935615063

required:
>= 0.90

PASS.

PERMUTATION

maximum output-logit difference:
3.814697265625e-06

required:
<= 1e-05

PASS.

OUTPUT / BOUNDARY SAFETY

parameter count:
13694

<= 18000:
PASS.

no global / task / future / position feature:
PASS.

all outputs finite:
PASS.

probabilities bounded / normalized:
PASS.

CAUSAL INTERPRETATION

The learned-updater sequence is now:

LU-1A:
flat raw representation.

LU-1B:
focal-side canonicalization produced large improvement.

LU-1C:
shared-neighbor mean aggregation produced modest mean improvement
but did not repair the tail.

LU-1D:
explicit multiplicative gating produced further improvement.

LU-1E:
exact categorical state-conditioned relation routing
plus the learned gate does not materially lower the remaining mean
and worsens the p99 tail relative to LU-1D.

Therefore the remaining failure is not explained simply by:

missing global information;

C/S coordinate symmetry;

generic neighbor ordering;

lack of an explicit multiplicative gate;

or failure to expose categorical state identity structurally.

Do not promote LU-1E.

Do not run it closed-loop.

Do not relax the imitation bars.

Do not widen automatically.

NEXT AUTHORIZED STEP

Per the preregistration:

run one observation-only residual audit
on the already-open LU-1E held-out test set
against the exact canonical weights.

Stratify the remaining STAY error
around the already-identified conditional-ECHO / mode family
and compare directly with LU-1D.

No retraining.

No weight change.

No new threshold.

No alternate model size.

If the same conditional-ECHO tail remains,
the next research decision should consider
whether pure black-box approximation of the hand-designed stay law
is the right learning target,
rather than continuing a sequence of increasingly explicit
architectural encodings of known teacher algebra.

PLAIN-SPEAK INTERPRETATION

We gave the neural cell another structural advantage.

It was allowed to treat
SELF,
OPPONENT,
uncertain,
and refractory neighbors
with different learned transforms.

That did not solve the hard commitment decision.

The easy parts remain good:

uncertainty release;

recruitment;

symmetry;

quiescence;

locality;

and permutation behavior.

But the hard stay/defect rule
is still outside the same bars.

Average error barely changed from LU-1D,
and the worst one percent got worse.

So we should not keep adding structure blindly.

The next step is to inspect
the exact remaining failures one more time.

If they are still the same
ECHO-only-when-challenged problem,
then the evidence is starting to say
that imitating this hand-written algebra
may be the wrong first learning target.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
