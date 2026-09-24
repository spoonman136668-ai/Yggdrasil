TITLE: LU-2P PRE-LU2PF1 MECHANICAL GATE
DATE: 2026-09-24
STATUS: PASS / LU2PF1 FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
b1a02b436c223d75ceca40b00d0af852e52d128f

PARENT LU-2O CLOSURE:
1d5deaa6231b854a00fb50e76b685e437b29e700

PARENT LU-2N CLOSURE:
096c8dee7ae368f69e322be8e1b8a5ca20feff08

PARENT LU2NF1:
a4657c94a654d2b4f83b6af0c7844b65e6999593

TESTED CANDIDATE COMMIT:
f0efcb4d9bd8f8a137bcd0275b7737da6d548c8b

MECHANICAL RUN:
36058137485

EXECUTION HEAD:
870e0b851be1335aecff6f73ad0e131be39222cf

MECHANICAL ARTIFACT:
10832864011

CANDIDATE SOURCE SHA256:
0e454bbd06450b4e768ce0e3df878d757d05c3ce752e3cc0ad8a20d8d4b532d9

DUPLICATE HARNESS EVIDENCE

bytes each:
27283

SHA256 both:
980f6b98ddccb536823684248fa51136da313624573fdd616b73ab98ae867547

byte-identical:
TRUE

INTERNAL PAIRED MECHANICAL RESULT

bytes:
26286

SHA256:
b2da1eb4c8d0cba0e86888bec3f4e5097588ff8c21872b14a51ece3f50c878e7

all_pass:
TRUE

CANONICAL WEIGHTS

SHA256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

MECHANICAL CONTRACT

exact LU-2N organism dynamics inert under instrumentation:
PASS

exact canonical learned-weight SHA:
PASS

alpha exactly 0.25:
PASS

U_A0 exact teacher one-step:
PASS

U_A25 exact convex U blend:
PASS

H exact teacher:
PASS

C/S/FC/FS exact teacher:
PASS

OBS-V1 unchanged:
PASS

load exactly one request per epoch:
PASS

contiguous lesion exactly 16 cells:
PASS

lesion window [96,108):
PASS

expiry 32:
PASS

Task-2 stage / repair / reverify semantics unchanged:
PASS

maturity boundary detection <=156:
PASS

terminal detection 157 progress rule:
PASS

terminal detection 158 progress rule:
PASS

terminal detection 159 progress rule:
PASS

no drain epochs:
PASS

paired transition variates common:
PASS

no model RNG:
PASS

learned calls restricted to H/U:
PASS

no primary manifest during mechanical gate:
PASS

duplicate mechanical evidence byte-identical:
PASS

mechanical zero incorrect DONE:
PASS

MATURITY FIXTURE

mature156:
PASS

terminal157:
PASS

terminal158:
PASS

terminal159:
PASS

deliberately under-progressed 157 rejected:
PASS

deliberately under-progressed 158 rejected:
PASS

DECISION

Freeze the exact tested candidate source as LU2PF1.

Do not derive any LU-2P primary manifest before the freeze identity exists.

PLAIN-SPEAK INTERPRETATION

The new scorecard is wired without changing the organism.

The instrumented run reproduces the original LU-2N pair exactly once the
new maturity report is removed.

The organism still gets exactly 160 ticks, the same one-job-per-tick load,
the same concentrated sixteen-cell injury, the same repair state machine,
and the same 25-percent learned U authority.

The only difference is the evaluator no longer calls a repair broken when
the corruption is first detected too late for the remaining mandatory
operations to physically fit before tick 160.

The ten fresh worlds may now be derived from the frozen implementation.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
