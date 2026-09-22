TITLE: YGGDRASIL A43 POST-CLOSURE DIAGNOSIS — 6:2 VS 5:3 RESIDUAL FAILURE
DATE: 2026-09-22
STATUS: POST-CLOSURE DIAGNOSTIC / NO THRESHOLD OR MECHANISM CHANGE
PARENT CLOSURE: acff6603ffb599a5115f521d5ade066189d28264
BRANCH: dg1a-ar

PURPOSE

Explain why A43 MARGIN_REINFORCE
nearly solves biased-periodic contexts 44/45
but remains oscillatory in contexts 46/47.

This analysis uses only
the frozen F43 primary output.

It does not change:

A43 outcomes;
qualification;
information-gain status;
thresholds;
arms;
or implementation.

ENVIRONMENTAL DIFFERENCE

All four contexts belong
to FAMILY 5 biased periodic worlds.

Context 44:

C-favored 6:2 cycle.

base sequence:
C C C C C C S S.

Context 45:

S-favored 6:2 cycle.

base sequence:
S S C C C C C C.

Context 46:

C-favored 5:3 cycle.

base sequence:
C C C C C S S S.

Context 47:

S-favored 5:3 cycle.

base sequence:
S S S C C C C C.

Therefore 46/47 differ from 44/45
in two linked ways:

the support interval is shorter;

the adverse interval is longer.

The long-run bias is also weaker:

6:2 = 75% favored;

5:3 = 62.5% favored.

MARGIN-REINFORCE BURST SURVIVAL

D2 context 44:

mean favored fraction at pulse onset 92.19%;
burst-end favored fraction 78.73%.

Onset-cohort survival:

after adverse epoch 1:
100.00%.

after adverse epoch 2:
83.93%.

D2 context 45:

pulse onset 86.41%;
burst end 72.55%.

cohort survival:

epoch 1:
99.92%.

epoch 2:
80.60%.

D2 context 46:

pulse onset 66.84%;
burst end 14.84%.

cohort survival:

epoch 1:
98.81%.

epoch 2:
67.65%.

epoch 3:
19.30%.

D2 context 47:

pulse onset 53.02%;
burst end 11.51%.

cohort survival:

epoch 1:
95.67%.

epoch 2:
59.33%.

epoch 3:
17.59%.

D3 context 44:

pulse onset 90.10%;
burst end 77.13%.

cohort survival:

epoch 1:
100.00%.

epoch 2:
82.64%.

D3 context 45:

pulse onset 81.30%;
burst end 68.80%.

cohort survival:

epoch 1:
99.57%.

epoch 2:
80.84%.

D3 context 46:

pulse onset 61.20%;
burst end 13.45%.

cohort survival:

epoch 1:
98.71%.

epoch 2:
64.33%.

epoch 3:
17.86%.

D3 context 47:

pulse onset 45.57%;
burst end 8.80%.

cohort survival:

epoch 1:
94.58%.

epoch 2:
51.61%.

epoch 3:
13.68%.

SUPPORT-DEPTH DIFFERENCE

D2 MARGIN_REINFORCE:

context 44:
mean pre-pulse M 0.5545;
mean applied cooperative Q 0.5133.

context 45:
mean M 0.5422;
mean Q 0.4795.

context 46:
mean M 0.4799;
mean Q 0.3269.

context 47:
mean M 0.4631;
mean Q 0.2647.

D3 MARGIN_REINFORCE:

context 44:
mean M 0.5542;
mean Q 0.5007.

context 45:
mean M 0.5438;
mean Q 0.4667.

context 46:
mean M 0.4791;
mean Q 0.2946.

context 47:
mean M 0.4633;
mean Q 0.2295.

DIAGNOSIS

A43 does not fail
because its cooperative mechanism
is absent in 46/47.

The first adverse epoch
is survived almost completely.

The failure begins
during repeated challenge.

By the second adverse epoch,
the 5:3 worlds have already lost
roughly one third to one half
of the onset core.

The third adverse epoch
then collapses the remaining core
to roughly 14-19%.

The 6:2 worlds end
before that third challenge arrives.

They therefore preserve
roughly 81-84%
of the onset core
through the complete adverse interval.

The 5:3 worlds also enter challenge
with:

a smaller favored committed population;

lower accumulated own margin M;

and a weaker cooperative Q field.

Thus the residual oscillator
is a compound boundary:

weaker pre-challenge core formation;

plus one additional adverse epoch.

NO GAIN-TUNING CONCLUSION

This result does not justify
increasing the A43 reinforcement coefficient.

There is no coefficient to tune
in the frozen A43 mechanism.

The OCCUPANCY upper-bound arm already shows
what stronger undifferentiated reinforcement does:

it nearly stops oscillation
but destroys reversal and balanced uncertainty.

The next experiment should therefore
change when or how
already-demonstrated local behaviors are used,
not simply strengthen them.

A44 JUSTIFICATION

A phase-dependent local strategy
is now causally justified.

During locally supportive evidence:

use the previously demonstrated
active recruitment behavior
to build a larger and deeper-margin core
before challenge begins.

During locally opposing evidence:

use the A43 MARGIN_REINFORCE mechanism
to preserve that core.

This directly targets
both measured components
of the 5:3 failure:

insufficient pre-pulse core depth;

and collapse during repeated opposition.

The phase decision must be local.

No cell may read:

context ID;
family ID;
future evidence;
or a hidden global environment phase.

PLAIN-SPEAK INTERPRETATION

We now know where the remaining failure lives.

A43 can survive
a two-step attack.

It usually cannot survive
a three-step attack.

And the three-step worlds
start the attack in worse shape:

fewer allies;

less accumulated evidence;

and weaker neighbor reinforcement.

The first hit is not the problem.

The core almost always survives it.

The second hit weakens the structure.

The third hit breaks it.

That means the next experiment
should not simply build
a thicker wall.

It should let the core
use quiet/supportive periods
to grow stronger before the attack,

then switch into
cooperative defense
when the attack arrives.

In plain terms:

build while the weather is good;

hold together when the weather turns.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
