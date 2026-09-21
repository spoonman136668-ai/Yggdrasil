TITLE: YGGDRASIL A23 / T8G — Persistent Patch Confidence Ledger
DATE: 2026-09-21
STATUS: PREREGISTERED SEQUENTIAL EVIDENCE-ACCUMULATION EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8G / APPLICATION-A
PARENT: A22 Two-Window Canary Hysteresis
BRANCH: dg1a-ar

PURPOSE

A21 showed that one positive real canary window is too noisy.

A22 showed that requiring two consecutive positive windows
substantially improves safety,
but discards too much partial evidence
and leaves too few expansions.

A23 therefore replaces the consecutive-win switch
with a persistent confidence ledger.

The ledger does not forget a positive window
just because the next window is neutral.

It also does not ignore contradiction.

Every independent real window
adds signed evidence to the same immutable record.

The scientific question is:

CAN A PATCH ACCUMULATE ENOUGH REAL EVIDENCE
TO EARN AUTHORITY
WITHOUT REQUIRING CONSECUTIVE WINS
AND WITHOUT REINTRODUCING THE A21 HARM RATE?

A23 is not permitted to weaken A22 safety limits.

FROZEN PARENT EVIDENCE

A20:
real-canary discovery positive in known A17 worlds.

A21:
fresh one-window replication failed.

A22:
two-window hysteresis reduced harm sharply
but failed the 48 / 384 coverage floor.

A22 closure:

42726774fc258e2f23e1ee5f00342205ab58607f.

A23 FREEZE

Let the exact A23 implementation freeze commit be:

F23.

No real post-F23 trajectory may be derived
before F23 exists.

FRESH TRAJECTORIES

After F23,
derive exactly:

384

fresh trajectories:

48 fixed A17 patch contexts
x
8 post-F23 replicas.

Each trajectory contains:

40 demand epochs.

Replacement episodes:

0;
8;
16;
24;
32.

Windows:

W1 = epochs 0-7;
W2 = 8-15;
W3 = 16-23;
W4 = 24-31;
W5 = 32-39.

W1-W4 are provisional evidence windows.

W5 is untouched confirmation.

Every 40-demand sequence has exact mean
equal to the candidate target prior.

All demand and replacement namespaces are:

YGG-A23-*

and distinct from A17-A22.

CANARY ARMS

C1:
1 of 4 newborns candidate-controlled
during W1-W4.

C2:
2 of 4.

C3:
3 of 4.

The remaining newborns use stale-previous authority.

The same canary fraction is used
at each provisional replacement episode:

0;
8;
16;
24.

No full candidate expansion occurs
before W5.

STALE TWIN

Every provisional trajectory has
an exact stale-control twin
from the same pre-window state.

Candidate canary and stale twin receive
the same demand sequence.

The twin provides:

counterfactual evidence;
rollback authority;
matched service comparison.

CONFIDENCE LEDGER

Initial confidence:

0.

After each provisional window Wi,
compute:

delta_i =
canary cumulative service in Wi
-
matched stale-twin service in Wi.

Evidence contribution:

delta_i > 0:
+1.

delta_i == 0:
0.

delta_i < 0:
-1.

Ledger score after window i:

L_i =
sum of all contributions from W1..Wi.

No clipping.

With four provisional windows:

L_i is bounded naturally in [-4,+4].

A23 intentionally uses only the sign,
not the magnitude,
because A21 showed that larger positive margins
were not reliably safe.

IMMUTABLE LEDGER RECORD

Every evidence record contains:

scenario;
patch;
replica;
canary arm;
window index;
canary service;
stale-twin service;
delta;
signed contribution;
prior ledger digest;
post-update score;
window evidence digest.

Each ledger record is digest-chained.

Historical evidence is immutable.

A neutral or contradictory window
does not erase prior evidence.

EARNED AUTHORITY RULE

At the end of W4:

if L_4 >= +2:

EARNED_EXPANSION.

Otherwise:

NO_EXPANSION.

No earlier full expansion is permitted.

No score below +2 deletes the learned patch.

The patch remains:

LEARNED / DORMANT / PROVISIONAL.

A23 therefore tests:

two NET positive windows
across four independent opportunities,

not:

two consecutive positive windows.

WHY +2

A22 required two positive windows in a row.

A23 preserves the same net evidentiary requirement
but removes the adjacency requirement.

Thus A23 changes evidence memory,
not the nominal amount of positive evidence required.

W5 CONFIRMATION

At epoch 32:

EARNED_EXPANSION:
all four newborns use candidate target prior.

NO_EXPANSION:
all four newborns use stale-previous prior.

Then execute W5 untouched.

No W5 demand identity
may reach the ledger or decision function.

REFERENCE RULES

R0:
always stale in W5.

R1:
all-candidate in W5.

R2:
A21-style one-hit reference:
W1 positive.

R3:
A22-style two-hit consecutive reference:
W1 positive AND W2 positive.

R4:
A23 ledger:
L4 >= +2.

R2 and R3 are diagnostic references only.

PRIMARY QUALIFICATION PER ARM

An arm is LEDGER-QUALIFIED iff all are true:

EARNED_EXPANSION count >= 48

AND

actual W5 harmful expansion rate <= 0.05

AND

R1 W5 harmful labels
among EARNED_EXPANSION trajectories <= 0.05

AND

actual harmful expansion rate
is no greater than half
the unconditional R1 W5 harm rate
when that rate is nonzero

AND

all integrity probes pass.

Coverage floor:

48 / 384.

Harm ceiling:

5%.

These are inherited unchanged from A22.

MINIMUM-EXPOSURE SELECTION

If multiple arms qualify,
select the lowest exposure:

C1
then C2
then C3.

If none qualify:

NONE.

No highest-service post-hoc selection.

SECONDARY METRICS

For each arm report:

W1 positive count;
W2 positive count;
W3 positive count;
W4 positive count;

score distribution L4 = -4..+4;

EARNED_EXPANSION count;

provisional W1-W4 aggregate service delta
versus stale twins;

W5 service delta versus stale;

complete 40-epoch service delta versus R0;

complete service delta versus R1;

actual beneficial / neutral / harmful W5 expansions;

R1 beneficial / neutral / harmful W5 labels
among earned expansions;

one-hit reference count and harm rate;

two-hit consecutive reference count and harm rate;

persistent-ledger count and harm rate;

coverage recovered by ledger
relative to A22-style two-hit;

harm difference
relative to one-hit and two-hit;

time distribution of positive / neutral / negative evidence.

EVIDENCE-PATTERN DIAGNOSTICS

Report separately:

++00;
+0+0;
+-+-;
++--;
+--+;
0++;
and all other observed sign patterns.

The purpose is to identify
whether nonconsecutive positive evidence
is genuinely useful
or merely re-admits transient false positives.

No sign pattern may be excluded post hoc.

INTEGRITY PROBES

P1:
exact A17 replay remains unchanged.

P2:
384 unique F23-derived trajectories.

P3:
40 demands per trajectory;
exact mean equals candidate target.

P4:
replacement episodes exactly 0/8/16/24/32;
four unique IDs each.

P5:
W5 future leakage impossible.

P6:
ledger contribution mapping exactly:
positive +1;
zero 0;
negative -1.

P7:
ledger score equals exact sum of immutable records.

P8:
prior ledger digest chain exact.

P9:
contradictory evidence subtracts one
and does not delete prior records.

P10:
neutral evidence changes neither score
nor historical evidence.

P11:
no full candidate authority before W5.

P12:
C1/C2/C3 exposure limits exact
through all provisional windows.

P13:
NO_EXPANSION leaves learned patch preserved.

P14:
two complete primary sweeps byte-identical.

P15:
no C-v3;
no duplicate context;
major history [v1,v2];
slot count 3.

NEGATIVE / LIMIT CONTROLS

N1 — RESET LEDGER AFTER NONPOSITIVE WINDOW

Expected to reproduce the information loss
of consecutive-win hysteresis.

N2 — IGNORE NEGATIVE WINDOWS

Unsafe confidence ratchet.

N3 — WEIGHT POSITIVE MARGIN BY MAGNITUDE

Not authorized in A23.
A21 showed margin magnitude alone
did not establish safety.

N4 — INSPECT W5 BEFORE DECISION

Invalid future leakage.

N5 — DELETE PATCH BELOW THRESHOLD

Invalid learned-memory destruction.

N6 — FULL ACTIVATE BEFORE SCORE +2

Outside A23 authority boundary.

N7 — CORRELATED / NONSTATIONARY WINDOWS

Boundary.

A23 derives independent deterministic window namespaces,
but real-world dependence remains a later research problem.

INTERPRETATION

A23 tests whether the problem in A22
was evidence forgetting.

If A23 materially raises coverage
while retaining the A22 safety improvement,
that supports a persistent confidence representation.

If coverage rises
but harm returns toward A21 levels,
nonconsecutive positive windows are not interchangeable evidence
and the ledger requires stronger temporal weighting.

If coverage remains too low,
the problem is not merely consecutive-win reset;
the canary observation process itself
does not provide enough information.

PLAIN-SPEAK QUESTION

A22 made Yggdrasil prove itself twice.

That made it safer,
but almost every patch got stuck waiting.

The problem is that A22 effectively forgot partial evidence.

If a patch did well,
then had a neutral or bad stretch,
its earlier success stopped helping.

A23 gives each learned patch a small confidence notebook.

Every real trial writes one permanent line:

worked: +1;
tie: 0;
hurt: -1.

Nothing gets erased.

Contradictory evidence counts against confidence.

Neutral evidence does not fake confidence.

After four small real trials,
a patch needs at least two more wins than losses
to earn full authority for a completely untouched fifth window.

So A23 asks:

CAN YGGDRASIL REMEMBER EVIDENCE
WITHOUT BECOMING GULLIBLE?

That is closer to real confidence calibration
than a simple win-twice switch.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-IMPLEMENTATION CLARIFICATION 01 — W5 NO-EXPANSION STATE

DATE:
2026-09-21.

STATUS:
LOCKED BEFORE A23 IMPLEMENTATION FREEZE
AND BEFORE ANY REAL F23-DERIVED TRAJECTORY.

At the epoch-32 boundary:

EARNED_EXPANSION:

continue the provisional canary trajectory;
apply 4 / 4 candidate-controlled newborn births.

NO_EXPANSION:

discard the provisional canary trajectory at the W5 boundary;
restore the exact matched stale-twin state;
apply 4 / 4 stale-controlled newborn births.

Reason:

NO_EXPANSION must mean no residual unearned candidate authority
enters the untouched confirmation window.

This clarification changes no ledger threshold,
no window,
no exposure arm,
no demand generation,
and no qualification criterion.

No A23 outcome has been observed.

