TITLE: LU-1E POST-CLOSURE CONDITIONAL-ECHO RESIDUAL AUDIT
DATE: 2026-09-23
STATUS: OBSERVATION-ONLY / CANONICAL WEIGHTS / NO RETRAINING
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1EF1:
f459273c897a7bd889b6de2ec2d9720374215327

LU-1E CLOSURE:
6681d1abdbfc30a3d8e8171fa5ec6b006426d25f

CANONICAL WEIGHT SHA256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

AUDIT ARTIFACT

bytes:
6252

SHA256:
c58da3798f35fc0ca0b62b92158c345a6a70dc0aabdab3cb1a3bdfc170324dbd

PURPOSE

Determine whether LU-1E changes the residual stay-defect failure family
or merely redistributes error inside the same conditional-ECHO problem.

No retraining.

No weight change.

No threshold change.

No alternative architecture.

No new teacher-derived input.

OVERALL STAY ERROR

n:
6000

mean absolute error:
0.0230781151

p95:
0.0990227163

p99:
0.2420497854

maximum:
0.5921896696

MODE STRATIFICATION

CHALLENGE

n:
2594

mean absolute error:
0.0327488128

p99:
0.2669896740

SUPPORT

n:
2666

mean absolute error:
0.0146100034

p99:
0.1656124897

NEUTRAL

n:
740

mean absolute error:
0.0196864882

p99:
0.3108222151

CONDITIONAL ECHO

CHALLENGE / ECHO DOMINANT

n:
854

mean absolute error:
0.0463718588

p99:
0.4206226736

mean signed bias:
-0.0114398911

The student under-predicts stay
when matching-side ECHO should protect
a challenged committed cell.

CHALLENGE / NO ECHO

n:
1696

mean absolute error:
0.0253605597

p99:
0.1180259585

NEUTRAL / ECHO DOMINANT

n:
219

mean absolute error:
0.0471487306

p99:
0.3714222948

mean signed bias:
+0.0470173478

The student over-predicts stay
when ECHO is present
but the exact teacher does not use ECHO protection.

NEUTRAL / NO ECHO

n:
509

mean absolute error:
0.0080806919

p99:
0.0791844559

SUPPORT / ECHO DOMINANT

n:
811

mean absolute error:
0.0245567788

p99:
0.2440346405

mean signed bias:
+0.0098887748

SUPPORT / NO ECHO

n:
1820

mean absolute error:
0.0101618174

p99:
0.0971892452

COMPARISON TO LU-1D REPRODUCTION-SENSITIVITY AUDIT

LU-1D approximate CHALLENGE / ECHO DOMINANT mean:
0.037378

LU-1E:
0.046372

WORSE.

LU-1D approximate CHALLENGE / NO ECHO mean:
0.030438

LU-1E:
0.025361

BETTER.

LU-1D approximate NEUTRAL / ECHO DOMINANT mean:
0.037614

LU-1E:
0.047149

WORSE.

LU-1D approximate NEUTRAL / NO ECHO mean:
0.005964

LU-1E:
0.008081

WORSE.

LU-1D approximate SUPPORT / ECHO DOMINANT mean:
0.020219

LU-1E:
0.024557

WORSE.

LU-1D approximate SUPPORT / NO ECHO mean:
0.013255

LU-1E:
0.010162

BETTER.

Thus the state-conditioned relation bank
helps several no-ECHO regimes
but worsens the high-error ECHO-dominant regimes.

The unresolved problem is not generic category recognition.

It is the exact conditional use of short-term memory.

PRESSURE

pressure = 0

n:
2811

mean absolute error:
0.0019405310

p99:
0.0374316454

The zero-pressure region remains learned very well.

Therefore the dominant problem is not
the pressure-zero hinge itself.

REPRESENTATIVE WORST CASE

mode:
CHALLENGE

opposition:
1.0

own aligned evidence:
0.0

qraw:
0.0

matching-side qecho:
0.8670120239

pressure:
0.1329879761

teacher stay:
0.9815315008

student stay:
0.3893418312

absolute error:
0.5921896696

The model sees the required local information
but substantially underuses valid ECHO protection.

REPRESENTATIVE OFF-MODE ECHO LEAK

mode:
NEUTRAL

opposition:
0.7200000286

own aligned evidence:
0.0

qraw:
0.0

matching-side qecho:
0.6012623310

teacher stay:
0.2508790791

student stay:
0.6838768125

absolute error:
0.4329977334

The model allows memory to protect commitment
when the exact teacher says memory should not participate.

CORRECTED FULL-MIRROR REPRESENTATION AUDIT

committed symmetry pairs:
1000

canonical input identity:
1000 / 1000

identity rate:
1.0

Therefore the LU-1E closure's 0.075 identity field
is confirmed to be an inherited swap-helper artifact,
not a canonicalization failure.

This does not alter LU-1E qualification.

DIAGNOSIS

LU-1A through LU-1E have now tested:

flat approximation;

focal-side canonicalization;

shared neighbor encoding;

explicit multiplicative gating;

and exact categorical relation routing.

Across those changes:

H release is learnable inside the frozen bars.

U recruitment is learnable inside the frozen bars.

The C/S stay law remains outside the frozen bars.

The remaining error repeatedly concentrates
on the exact rule:

matching-side ECHO may affect commitment
only under the correct local challenge condition.

LU-1E provides evidence against continuing
to expose progressively more of the known teacher algebra
through architecture-specific representation tricks.

Doing so risks turning learned-updater research
into reconstruction of the hand-written law
rather than testing whether a compact learned cell
can acquire useful developmental behavior.

NEXT RESEARCH DIRECTION

Do not immediately run LU-1F
as another full-law imitation architecture.

Instead test partial learned substitution in closed loop.

Freeze the difficult C/S stay-defect law
as the exact trusted V0.2 deterministic/stochastic teacher mechanism.

Substitute only the two learned output families
that have repeatedly passed imitation:

H release;

U recruitment.

Use a frozen canonical learned model
without retraining.

Compare fresh-world closed-loop Task-1 behavior against
the exact V0.2 teacher organism.

This asks whether learned local control
can participate causally in the organism
before every hand-designed transition family
has been replaced.

The experiment must preserve:

V0.2 topology;

LOCAL_HEDGE;

ECHO_PHASE;

NO_POOL;

D2;

G5_FULL OFF;

request-bound handoff;

Task-1 workload;

scheduler;

expiry;

phase schedule;

anchor relocation;

lesion;

common randomness;

and all safety/integrity probes.

The learned model may control only H and U transition probabilities.

C/S stay-defect remains exact V0.2.

No global information.

No learned closed-loop promotion from imitation alone.

PLAIN-SPEAK INTERPRETATION

We have pushed the same hard imitation problem far enough.

The neural cell can already learn two important jobs:

when an uncertain cell should release;

and what an uncommitted cell should become.

It still does not reproduce
the old commitment-memory rule precisely enough.

More architecture did not solve that.

The mistake is still very specific:

sometimes memory is ignored when it should protect the cell;

sometimes memory protects the cell when it should not.

Instead of teaching the network
more and more pieces of the hand-written formula,
the better question now is:

can the parts it already learned
actually run inside the organism?

So the next experiment should let the neural model
control uncertainty and recruitment in closed loop,
while the proven commitment rule remains in charge
of committed cells.

That gets us closer to a genuinely learned organism
without weakening the part we have not learned safely yet.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
