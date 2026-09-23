TITLE: LU-2A PRE-LU2AF1 MECHANICAL GATE
DATE: 2026-09-23
STATUS: PASS / SOURCE FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
bdd6bc440635597e1fec64cc1c5124dfc1e0369b

CANDIDATE SOURCE

local isolated sandbox source:
lu2a_partial_learned_hu_closed_loop_v1.candidate.py

bytes:
27655

SHA256:
be2af2e8a496532122957011e15ebbaf83bf55004caadb3e61931a2ed85e555e

CANONICAL LEARNED WEIGHTS

bytes:
55917

SHA256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

exact accepted LU-1E canonical weight identity:
PASS

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

EXACT FROZEN-PARENT SOURCE IDENTITIES

Task-1 base:
567c37e3e2171bc3cfc15b996c447e87b7ac5cdafb7bc299ba104284ae826e12

Task-1B:
e8d409c5eb8e750123aae4979fd1091611a915c22f7cf977e420345186aef6b9

Task-1E:
c1578a0d21d1125a26d81664adc0c3a78a3a23e9a4a2a4865d526e41af7d2207

Task-1F R1:
a3122a9f4f6da6c138cc12944528f5e2e3ef608e904067ef30da7feab7d640f4

LU-0C:
57476bf302ad3117a496b5ffabb33f69d3a99d1d89eb683be2d6073c662d45ae

LU-0D:
16bd83660cee18d71ea2a26a48032d1a376dee2f9f9a8ad0a1e1b21bb0d23440

LU-1E:
38c3d42786426d4ace4a779b69d49509d65a7eb31f9bfa3c4209e603879d0b2a

All exact source identities:
PASS.

MECHANICAL DUPLICATE GATE

complete mechanical runs:
2

mechanical evidence bytes each:
2792

mechanical evidence SHA256 both:
96b1aa6362dbcfb53112d274987b4ae8c763b53abb1566cd9fcdbc6273794fec

byte identical:
TRUE.

MECHANICAL PROBES

source identity exact:
PASS.

learned weight SHA exact:
PASS.

LU-1E trainable parameter count = 13694:
PASS.

TEACHER_V02 exact parent NO_POOL parity:
PASS.

HYBRID_HU duplicate mechanical result byte identity:
PASS.

C/S plus refractory-only fixture exact parent parity:
PASS.

No learned-model query occurred in the C/S plus refractory-only fixture:
PASS.

Model queries restricted to H/U:
PASS.

H output mapping exact:
PASS.

U [C,S,H,U] output mapping exact:
PASS.

OBS-V1 semantic width 70:
PASS.

No learned-model RNG:
PASS.

No optimizer or training invoked:
PASS.

Existing V0.2 transition RNG salts retained:
PASS.

Learned outputs finite:
PASS.

Learned outputs bounded / normalized:
PASS.

D2:
PASS.

G5_FULL OFF:
PASS.

NO_POOL:
PASS.

LOCAL_HEDGE:
PASS.

ECHO_PHASE:
PASS.

Request-bound handoff:
PASS.

MECHANICAL CAUSAL ACTIVITY

The ordinary mechanical world naturally contained:

H evaluations:
0

U evaluations:
1526

U learned-vs-teacher TV delta >1e-6:
1526

realized U transition differences under shared random variates:
36

mean U TV:
0.0219896813

maximum U TV:
0.0722474793

This is sufficient for a pre-freeze implementation check.

It is NOT sufficient for the preregistered LU-2A primary causal gate.

The primary still requires:

H evaluated > 0;

U evaluated > 0;

nonzero H learned-vs-teacher probability delta;

nonzero U learned-vs-teacher TV delta;

and at least one realized learned-controlled H or U transition difference
across the five fresh worlds.

If fresh primary worlds do not naturally exercise H,
LU2A_LEARNED_PARTICIPATION_CAUSAL must fail closed.

IMPLEMENTATION BOUNDARY

TEACHER_V02 calls the exact LU-0D NO_POOL parent.

HYBRID_HU changes only:

H release probability source;

U recruitment probability source.

C/S stay-defect remains exact V0.2.

FC/FS hard lifecycle remains exact V0.2.

No new random draw is introduced.

For U recruitment:

the inherited event uniform remains the leave-U draw;

the inherited category uniform remains the C/S/H conditional draw.

Thus the learned four-way distribution is sampled
with exactly the pre-existing two random variates.

DECISION

Pre-LU2AF1 mechanical gate:
PASS.

Exact candidate source freeze:
AUTHORIZED.

No primary manifest may be derived
until LU2AF1 exists.

PLAIN-SPEAK INTERPRETATION

The hybrid cell is wired correctly.

The old organism is still the control.

Committed cells still use the proven rule.

Only uncertainty and recruitment are handed to the neural cell.

The test uses the same random numbers
as the hand-written version.

On the mechanical world,
the neural recruitment policy was genuinely different
and changed 36 actual transitions.

The mechanical world happened not to contain
an H-release event.

That does not get hidden or patched.

The five fresh primary worlds still have to
naturally exercise both learned jobs
or the causal-learning claim fails.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
