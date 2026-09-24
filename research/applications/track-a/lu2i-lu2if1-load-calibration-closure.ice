TITLE: LU-2I LU2IF1 EXACT-PARENT PAIRED LOAD-RESPONSE CALIBRATION CLOSURE
DATE: 2026-09-24
STATUS: CLOSED / ORDINARY OVERLOAD ALONE NOT SUFFICIENT / L1 CANDIDATE ENVIRONMENT IDENTIFIED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
41cbbac5e7a4d58888c25cd562b9e92ef5cdb44c

MECHANICAL GATE:
46b2bbb474e42a52fb598fef1ae829d072734f43

LU2IF1:
326f89f940818a6abb0fcbc999595b844936dc53

THIRTY-MANIFEST BINDING:
ab911b7f11dfac513d4ffaa428a9a4bd3ec9a9e3

BOUND MANIFEST BUNDLE

manifests:
30

canonical JSON bytes:
930733

SHA256:
3598c372a046530caaf8956b58e0b2654c212fed00149cf9f350d0035344995f

BOUND CALIBRATION RUN:
36050323979

EXECUTION HEAD:
517de07d1ecfa9975c7aac8977aee5c85b2c59d1

DUPLICATE CALIBRATION SWEEPS

bytes each:
1016475

SHA256 both:
ff39cb4013bf988086e7ee1ebf5cf906c697f1b7393a09ac7cce5f10a632e1da

byte-identical:
TRUE

SCIENTIFIC STATUS

LU2I_ORDINARY_OVERLOAD_SUPPORTED:
FALSE

The preregistered feasibility ordering did not hold.

STRICT BASELINE COVERAGE

L1:
9 / 10

L2:
1 / 10

L3:
4 / 10

The required ordinary-overload relation was:

coverage(L2) > coverage(L3)

and

coverage(L1) >= coverage(L2).

The second relation holds.

The first does not.

Therefore ordinary offered-load overload alone is not sufficient to explain
the strict baseline-feasibility pattern.

PRE-SENSE LOAD RESPONSE

median world pre-SENSE median:

L1:
0 epochs

L2:
9.5 epochs

L3:
26 epochs

mean world pre-SENSE mean:

L1:
0.1989322606

L2:
11.0069957995

L3:
21.4775329274

Thus admission congestion responds strongly and monotonically to offered load.

This supports the narrower statement that offered load causes pre-SENSE
queueing, but it does not explain the nonmonotonic strict feasibility score.

CORRECTNESS

total incorrect DONE:

L1:
0

L2:
0

L3:
0

Both functional streams remain active at every load in every replicate.

TOTAL CORRECT DONE

L1:
1465

L2:
2304

L3:
1444

TOTAL EXPIRED

L1:
0

L2:
518

L3:
2684

REPAIR-INTEGRITY WORLDS

L1:
9 / 10

L2:
1 / 10

L3:
4 / 10

CORRUPTION EXPOSURE ACROSS TEN WORLDS

corruptions reaching egress:

L1:
82

L2:
146

L3:
92

verification detected:

L1:
82

L2:
137

L3:
82

repaired:

L1:
81

L2:
130

L3:
75

correct DONE after repair:

L1:
80

L2:
124

L3:
69

This is a critical exposure asymmetry.

The L2 arm allows substantially more corrupted requests to reach the egress /
verification boundary than L3.

Under L3, heavier congestion and expiry prevent many scheduled corruptions
from ever reaching that boundary.

Therefore a world-level all-or-nothing repair-integrity gate has different
opportunity exposure across loads.

This observation does not alter the preregistered LU-2I verdict.

It motivates a dedicated observation-only diagnosis before attributing the
L2 feasibility trough to developmental workforce organization.

FROZEN RECOVERY TARGET — DESCRIPTIVE ONLY

worlds reaching old target:

demand reversal:
L1 10 / 10
L2 9 / 10
L3 0 / 10

lesion:
L1 10 / 10
L2 5 / 10
L3 0 / 10

anchor rotation:
L1 10 / 10
L2 7 / 10
L3 0 / 10

The frozen target becomes attainable as load falls, despite not being a
LU-2I decision gate.

FUNCTIONAL ORGANIZATION

Median phase-specific C/S/U populations remain broadly similar between L2
and L3.

No lower-load arm loses both functional stream populations.

The current evidence therefore does not establish a catastrophic
developmental workforce collapse at L2.

CANDIDATE ENVIRONMENT

L1 satisfies the preregistered candidate criterion:

strict baseline coverage >= 8 / 10

and both streams remain functionally active.

L1 is therefore a candidate Task-2 environment only.

It is NOT authorized for learned-U transfer yet.

Per preregistration, any candidate load requires a fresh exact-parent
validation on a new ten-world set before a learned-U comparison may be
preregistered.

INTERPRETATION

Offered load definitely controls the admission queue.

At one request per epoch the queue is essentially gone.

At two it is moderate.

At three it consumes most of the 32-epoch lifetime.

But the binary strict baseline score does not improve monotonically because
repair-integrity exposure is itself load-dependent.

L2 exposes more corrupted requests to verification than L3, creating more
opportunities for an incomplete repair to make the whole world fail the
all-or-nothing repair gate.

L3 can look better on that gate partly because many corrupted jobs expire
before ever reaching egress.

This means the L2 trough must not be interpreted immediately as evidence
that the organism organizes its workforce worse at medium demand.

NEXT SCIENTIFIC QUESTION

Is the apparent L2 repair-feasibility trough explained by unequal integrity
opportunity exposure and deadline geometry, or by a genuine nonmonotonic
change in developmental workforce organization?

Run one observation-only paired exposure-conditioned audit on the exact
accepted LU-2I artifact before creating any new calibration worlds.

No rerun.
No new worlds.
No learned-U arm.
No threshold change.

PLAIN-SPEAK INTERPRETATION

Lowering the workload absolutely fixes the waiting line.

At one job per epoch, jobs basically start immediately.

But two jobs per epoch oddly fails the all-or-nothing repair score more often
than three.

The likely reason is not that two jobs makes the organism dumber.

At two jobs, many more corrupted requests survive long enough to reach the
repair test.

At three jobs, lots of them die in the queue before they ever get tested.

So the heavier world can accidentally look better on a binary repair score.

We need one clean audit that compares repair only among jobs that actually
had a fair chance to repair.

Then we can tell whether the middle-load dip is a measurement/exposure
artifact or a real developmental reorganization effect.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
