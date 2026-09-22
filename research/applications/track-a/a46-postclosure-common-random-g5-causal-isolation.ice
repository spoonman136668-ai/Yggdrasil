TITLE: YGGDRASIL A46 POST-CLOSURE DIAGNOSTIC — COMMON-RANDOM G5 CAUSAL ISOLATION
DATE: 2026-09-22
STATUS: POST-CLOSURE CAUSAL DIAGNOSTIC / NO A46 VERDICT CHANGE
PARENT CLOSURE: 2f8ebeeeef2ad0987b7f18f371533b65c9c48a5c
F46: 80c1673f5fccfe55e98e85a2dad8453b6ad3291e
PRIMARY SEED: A46-F46-80c1673f5fccfe55e98e85a2dad8453b6ad3291e-PRIMARY
BRANCH: dg1a-ar

PURPOSE

Separate the deterministic G5 re-entry effect
from treatment-versus-control stochastic-stream differences.

The frozen A46 primary remains authoritative
for qualification and information gain.

This diagnostic does not alter:

A46_RECOVERY_INFORMATION_GAIN = FALSE;

D2_G5_REENTRY NOT QUALIFIED;

D3_G5_REENTRY NOT QUALIFIED.

METHOD

Replay all 384 frozen A46 worlds.

For each D value,
force G5_REENTRY to consume
the exact same stateless action-random draws
as its paired A45 ECHO_PHASE control.

No world,
sensor,
heterogeneity,
state equation,
G5 equation,
or diagnostic equation changes.

Only stochastic treatment/control pairing changes.

Because action draws are keyed
by epoch,
cell,
event salt,
and control-arm identity,
state divergence does not shift
a sequential RNG cursor.

This is therefore
a common-random-number causal diagnostic.

RESULT

A46_RECOVERY_INFORMATION_GAIN
under the diagnostic comparison:

FALSE.

No 5:3 parent oscillator
is broken by G5.

D2 COMMON-RANDOM RESULT

ECHO_PHASE:

overall oscillation 5.99%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
aggregate service 237801;
balanced false-majority 3.12%;
reversal acquisition 89.06%;
5:3 epoch-3 core persistence 33.76%;
mean unresolved episode duration 3.616 epochs;
mean favored-majority recovery latency 3.487 epochs;
median recovery latency 3 epochs.

G5_REENTRY:

overall oscillation 6.25%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
aggregate service 238598;
balanced false-majority 3.12%;
reversal acquisition 89.06%;
5:3 epoch-3 core persistence 34.50%;
mean unresolved episode duration 3.190 epochs;
mean favored-majority recovery latency 2.962 epochs;
median recovery latency 3 epochs.

D2 causal deltas:

unresolved duration:
-11.78%.

mean recovery latency:
-0.526 epoch.

aggregate service:
+797.

5:3 epoch-3 core persistence:
+0.74 percentage point.

5:3 oscillators broken:
0 of 16.

D3 COMMON-RANDOM RESULT

ECHO_PHASE:

overall oscillation 7.03%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
aggregate service 234093;
balanced false-majority 0.00%;
reversal acquisition 87.50%;
5:3 epoch-3 core persistence 31.73%;
mean unresolved episode duration 4.795 epochs;
mean favored-majority recovery latency 4.268 epochs;
median recovery latency 4 epochs.

G5_REENTRY:

overall oscillation 8.07%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
aggregate service 235332;
balanced false-majority 0.00%;
reversal acquisition 87.50%;
5:3 epoch-3 core persistence 33.17%;
mean unresolved episode duration 3.711 epochs;
mean favored-majority recovery latency 3.250 epochs;
median recovery latency 3 epochs.

D3 causal deltas:

unresolved duration:
-22.61%.

mean recovery latency:
-1.018 epochs.

aggregate service:
+1239.

5:3 epoch-3 core persistence:
+1.44 percentage points.

5:3 oscillators broken:
0 of 16.

SAFETY

Common-random G5 produces:

zero 5:3 adverse-majority entries;

zero direct favored-to-adverse majority flips;

zero old-side G5 fires
during the true-reversal window.

Balanced false-majority
does not increase.

CHATTER COST

D2 short same-side four-epoch cycles:

632 -> 839.

D3:

0 -> 256.

Inherited chatter events also rise:

D2:
1836 -> 2075.

D3:
975 -> 1338.

Therefore the immediate-release action
trades some recovery speed
for greater local cycling.

G5 MECHANISM ACTIVITY

D2:

early releases 3217;
5:3 recovery early releases 1069;
same-epoch recruitments 1279;
former-side eventual recruitments 1906;
opposite-side eventual recruitments 337;
H recruitments 893.

D3:

early releases 4374;
5:3 recovery early releases 1413;
same-epoch recruitments 1764;
former-side eventual recruitments 2468;
opposite-side eventual recruitments 562;
H recruitments 1243.

CAUSAL INTERPRETATION

The large deterioration
seen in the frozen independent-stream primary
is not reproduced
when the stochastic realization
is held common.

Therefore it should not be interpreted
as evidence that G5 itself
destroys the A45 core
or 6:2 stability.

The causal G5 effect is smaller:

recovery becomes modestly faster;

refractory debt releases earlier;

wrong-side capture remains absent;

but short-cycle chatter increases;

and the inherited 5:3 oscillator label
does not change.

The D3 unresolved-duration reduction
of 22.61%
comes close to,
but does not reach,
the preregistered 25% information-gain threshold.

Thus G5 contains useful recovery signal,
but immediate re-entry to U
is a stronger intervention
than the evidence justifies.

NEXT JUSTIFIED ACTION CLASS

Return to the earlier A45
evidence-gate diagnostic.

The strongest first-locked-epoch
zero-threshold signal was:

local SUPPORT

AND

post-update former-side margin M_post > 0.

That signal was too common
in balanced worlds
to justify immediate release.

But a ONE-TICK TIMER ACCELERATION
does not immediately expose the cell
to recruitment.

It simply removes
one future refractory epoch.

This is now the justified successor action.

Use:

SUPPORT-only one-tick acceleration
as the causal control;

SUPPORT + M_post > 0
as the evidence-aligned treatment.

Apply only
on the first locked refractory epoch.

A qualifying cell remains refractory
for the current epoch.

No same-epoch recruitment occurs.

The timer can be shortened
by at most one epoch
per refractory episode.

COMMON-RANDOM DISCIPLINE

The successor should use
common stateless action-random draws
between paired control and treatment arms.

This is not outcome tuning.

It is a variance-control improvement
motivated by the A46 primary/diagnostic discrepancy.

All exogenous worlds,
sensor draws,
heterogeneity,
and event salts
remain frozen and shared.

PLAIN-SPEAK INTERPRETATION

The release signal was not bad.

When we replayed
the exact same worlds
with the exact same random breaks,
letting those cells stand up early
did help recovery.

Especially in D3,
the organism got its majority back
about one epoch sooner.

But immediate release
also caused more short-cycle activity.

And it still did not remove
the repeated unresolved-state cycle.

So the lesson is:

do not throw the safety lock away.

Make it slightly flexible.

When a benched cell
is on its first waiting turn,
and the local evidence
already supports its old side again,
let good evidence
remove one turn
from the remaining sentence.

The cell still sits out
for the current epoch.

It cannot instantly rejoin,
cannot instantly recruit,
and cannot immediately chatter.

That is a much smaller
and cleaner test.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
