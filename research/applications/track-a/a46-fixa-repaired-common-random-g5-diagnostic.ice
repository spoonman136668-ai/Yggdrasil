TITLE: YGGDRASIL A46-FIXA DIAGNOSTIC — REPAIRED COMMON-RANDOM G5 ISOLATION
DATE: 2026-09-22
STATUS: POST-DEFECT CAUSAL DIAGNOSTIC / PRE-REPAIR-FREEZE
PARENT DEFECT: 9a9dbc4bb5711c3156ca22efa0dd878554226319
ORIGINAL F46: 80c1673f5fccfe55e98e85a2dad8453b6ad3291e
BRANCH: dg1a-ar

PURPOSE

Repeat the A46 common-random
causal diagnostic
after restoring
the missing A45 ECHO_PHASE
parent behavior
inside G5_REENTRY.

This diagnostic does not replace
the required repaired frozen primary.

It determines whether
the intended G5 action itself
is harmful,
neutral,
or useful
once the parent-mechanism defect
is removed.

REPAIR CANDIDATE

Source SHA256:

53d643ca7c1b17b9368abd60cae1666de7698dd3530795845250d2481767c885.

Only parent-dispatch behavior changes
relative to F46.

G5_REENTRY now participates in:

A45 CHALLENGE q_eff
cooperative reinforcement;

A45/A44 support-gated
active margin recruitment;

and corresponding echo diagnostics.

G5 gate,
timer action,
worlds,
thresholds,
and metrics are unchanged.

PARENT PARITY

For parity testing only:

G5 action disabled;

G5 arm assigned
the paired ECHO_PHASE
A45 action-random identity.

Representative pair comparisons:

60.

Behavioral mismatches:

0.

COMMON-RANDOM METHOD

Use the original A46
primary world seed:

A46-F46-80c1673f5fccfe55e98e85a2dad8453b6ad3291e-PRIMARY.

Pair each repaired G5_REENTRY arm
to its ECHO_PHASE control
with identical stateless action-random draws.

G5 remains the only intended
behavioral difference.

RESULT

A46_RECOVERY_INFORMATION_GAIN
under repaired common-random comparison:

FALSE.

No 5:3 oscillator
is broken by G5.

D2 ECHO_PHASE:

aggregate service 237801;
harm rate 15.36%;
overall oscillation 5.99%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
balanced false-majority 3.12%;
reversal acquisition 89.06%;
median old-majority loss 3 epochs;
5:3 epoch-3 core persistence 33.76%;
mean unresolved episode 3.616 epochs;
mean favored-majority recovery latency 4.580 epochs;
same-side short-cycle chatter 632.

D2 repaired G5_REENTRY:

aggregate service 238598;
harm rate 15.10%;
overall oscillation 6.25%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
balanced false-majority 3.12%;
reversal acquisition 89.06%;
median old-majority loss 3 epochs;
5:3 epoch-3 core persistence 34.50%;
mean unresolved episode 3.190 epochs;
mean favored-majority recovery latency 4.136 epochs;
same-side short-cycle chatter 839.

D2 causal deltas:

mean unresolved episode:
-11.78%;

mean recovery latency:
-0.443 epoch;

service:
+797;

epoch-3 core persistence:
+0.74 percentage point;

6:2 oscillator delta:
0;

5:3 oscillators broken:
0 of 16.

D3 ECHO_PHASE:

aggregate service 234093;
harm rate 14.84%;
overall oscillation 7.03%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
balanced false-majority 0.00%;
reversal acquisition 87.50%;
median old-majority loss 3 epochs;
5:3 epoch-3 core persistence 31.73%;
mean unresolved episode 4.795 epochs;
mean favored-majority recovery latency 6.000 epochs;
same-side short-cycle chatter 0.

D3 repaired G5_REENTRY:

aggregate service 235332;
harm rate 14.84%;
overall oscillation 8.07%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
balanced false-majority 0.00%;
reversal acquisition 87.50%;
median old-majority loss 3 epochs;
5:3 epoch-3 core persistence 33.17%;
mean unresolved episode 3.711 epochs;
mean favored-majority recovery latency 4.875 epochs;
same-side short-cycle chatter 256.

D3 causal deltas:

mean unresolved episode:
-22.61%;

mean recovery latency:
-1.125 epochs;

service:
+1239;

epoch-3 core persistence:
+1.44 percentage points;

6:2 oscillator delta:
0;

5:3 oscillators broken:
0 of 16.

SAFETY

For repaired G5:

5:3 direct favored-to-adverse
majority flips:

0.

5:3 adverse-majority entries:

0.

Old-side G5 fires
during the first four
true-reversal epochs:

0.

Balanced false-majority
does not increase.

CAUSAL INTERPRETATION

After the parent-mechanism repair,
the A46 G5 action is not
the destructive mechanism
suggested by the independent-stream
F46 treatment output.

The intended G5 action:

preserves 6:2 stability;

modestly accelerates
unresolved recovery;

slightly improves service;

slightly improves
third-hit core persistence;

and preserves wrong-side
and true-reversal safety.

But the benefit is incomplete.

D2 unresolved-duration improvement:

11.78%.

D3:

22.61%.

Neither reaches
the original 25%
information-gain threshold.

No 5:3 oscillator
is broken.

Short-cycle chatter rises:

D2:
632 -> 839.

D3:
0 -> 256.

Thus immediate G5 re-entry
contains useful recovery information
but exposes cells to plasticity
more aggressively than necessary.

SCIENTIFIC STATUS

The repaired common-random diagnostic
supports the general conclusion
of the earlier common-random note
that G5 has modest beneficial signal.

However the original F46 primary
remains treatment-invalid
because its G5 arm
did not preserve parent mechanics.

A formal A46-FIXA frozen primary
is still required
under the originally preregistered
independent treatment RNG.

Only that repaired primary
may close the intended A46 question.

SUCCESSOR DIRECTION — NOT YET AUTHORIZED

If A46-FIXA confirms
the common-random diagnosis,
the next justified intervention
is smaller than immediate U release:

one-tick refractory acceleration
on the first locked epoch,

with no same-epoch recruitment.

The evidence-aligned treatment candidate is:

local SUPPORT
AND
M_post > 0.

A SUPPORT-only acceleration arm
should serve as causal control.

This direction is not frozen
until A46-FIXA closes.

PLAIN-SPEAK INTERPRETATION

Once we put back
the two A45 abilities
that A46 accidentally lost,
the picture changes.

Early release is not disastrous.

It helps a little.

The organism recovers
somewhat faster,
especially with D3,
and the easier 6:2 cases
stay stable.

But we are still
opening the gate wider
than the benefit requires.

The cells recover faster,
but they also cycle locally more.

And the hard 5:3 pattern
is still there.

So the likely lesson is:

the evidence signal is useful;

the action is too abrupt.

Before changing the design,
we still need to rerun
the formally repaired A46 experiment
under its original rules.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
