TITLE: LU-2D PRE-LU2DF1 MECHANICAL GATE
DATE: 2026-09-23
STATUS: PASS / SOURCE FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
2da357eca10263973e627c32d01c9274eb18ef6a

CANDIDATE STAGING:
0518caf00a225f6ef21588b28aa847491899c5ce

PARENT LU2AF1-R1:
ba771ec410b5a35498e0b146e71781ac4df4285c

CANDIDATE SOURCE

bytes:
7269

SHA256:
97c4013c9bd4fec1b7b26a1a9e5a76edb7d6793c739d1de162cc702374c1c7ec

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

MECHANICAL DUPLICATION

complete mechanical gates:
2

canonical evidence bytes each:
72181

SHA256 both:
f73cdb6bc29863536a99725152e6dd32dff4a1a1440004d7b6e7db639d7e8ade

byte-identical:
TRUE.

MECHANICAL PROBES

U_A0 exact parent-result parity
excluding literal arm-label metadata:
PASS.

State snapshots U_A0 vs exact teacher:
PASS.

All H learned-vs-teacher deltas:
ZERO.

Thus H authority remains exact teacher
for every dose arm.

Alpha set exactly:

0.00
0.25
0.50
1.00

PASS.

D2:
PASS.

G5_FULL OFF:
PASS.

LOCAL_HEDGE:
PASS.

ECHO_PHASE:
PASS.

NO_POOL:
PASS.

Request-bound handoff:
PASS.

OBS-V1 unchanged:
PASS.

No new RNG:
PASS.

Blended U probabilities finite / bounded / normalized:
PASS.

MECHANICAL DOSE ACTIVITY

U_A0

mean teacher-vs-active U TV:
0.0

realized U differences:
0

U_A25

mean teacher-vs-active U TV:
0.0061867476

realized U differences:
8

U_A50

mean teacher-vs-active U TV:
0.0126786904

realized U differences:
11

U_A100

mean teacher-vs-active U TV:
0.0255021923

realized U differences:
44

These are mechanical-fixture observations only.

They are not LU-2D primary results.

IMPLEMENTATION BOUNDARY

The candidate reuses the exact LU2AF1-R1
closed-loop step and sampling code.

It changes only the callback supplying
H/U probabilities.

For H:

the callback returns the exact V0.2 teacher probability
for every alpha.

For U:

the callback returns:

(1-alpha) * teacher
+
alpha * learned.

No other transition family changes.

DECISION

Pre-LU2DF1 mechanical gate:
PASS.

Exact candidate source freeze:
AUTHORIZED.

No fresh LU-2D primary world
may be derived before LU2DF1 exists.

PLAIN-SPEAK INTERPRETATION

The dose-control plumbing works.

At zero learned authority,
the organism is exactly the hand-written parent.

At 25, 50, and 100 percent,
only recruitment probabilities move.

Uncertainty release is completely hand-written
in every arm.

The same random numbers are reused.

On the mechanical world,
larger learned authority already caused
more actual recruitment decisions to differ.

That is only a wiring check.

The fresh ten-world experiment
still has to determine whether
larger authority also produces
larger developmental and functional divergence.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
