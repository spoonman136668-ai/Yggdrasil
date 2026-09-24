TITLE: LU-2N PRE-LU2NF1 MECHANICAL GATE
DATE: 2026-09-24
STATUS: PASS / LU2NF1 FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
f35e9330ba703fecdcdcfc6b9134b89e07df0dc3

TESTED CANDIDATE:
7623d3c2710cbceb2e1f95738622cca9378a303f

POST-RUN NO-OP SOURCE COMMIT:
cfbc109d90da0afea3d559be1a7b343afdb2eb7f

The post-run commit changed no files. The tested candidate blob is unchanged.

MECHANICAL RUN:
36055795803

EXECUTION HEAD:
46044792398119b8640414867a0276e9867a0944

MECHANICAL ARTIFACT:
10832586014

CANDIDATE SOURCE SHA256:
b058c2f449b05ac4cb180bcc234b20cd50432d572e2aa005db5c4ea71f5424cc

DUPLICATE HARNESS EVIDENCE

bytes each:
22704

SHA256 both:
ac46e8db451abf18758573660383d23e0f3a37d0f59221701b5b1806cf88ec55

byte-identical:
TRUE

INTERNAL PAIRED MECHANICAL RESULT

bytes:
21561

SHA256:
083850486012214c67ea4e6b82c4ad8c07f8372af2a976333c6ecd39c2b218d9

all_pass:
TRUE

LESION GEOMETRY FIXTURE

inherited 8-cell lesion:
4,12,20,28,36,44,52,60

LU-2M distributed 16-cell reference:
0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60

LU-2N contiguous 16-cell lesion:
4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19

contiguous cell count:
16

ring footprint:
25 percent

duration:
12 epochs

window:
[96,108)

same seed-derived base offset family:
PASS

geometry differs from LU-2M distributed pattern:
PASS

MECHANICAL CONTRACT

exact LU-2M / LU-2L alpha=.25 semantics:
PASS

exact canonical LU-1E weight SHA:
PASS

U_A0 exact teacher one-step:
PASS

U_A25 exact convex blend:
PASS

H exact teacher:
PASS

C/S/FC/FS exact teacher:
PASS

OBS-V1 unchanged:
PASS

one request per epoch:
PASS

Task-2 stage / repair / reverify semantics unchanged:
PASS

expiry 32:
PASS

contiguous lesion exactly 16 cells:
PASS

one contiguous ring interval:
PASS

lesion footprint 25 percent:
PASS

lesion duration 12:
PASS

no lesion feature enters learned inference:
PASS

common paired transition variates:
PASS

no model RNG:
PASS

learned calls restricted to H/U:
PASS

no primary manifest during gate:
PASS

duplicate mechanical evidence byte-identical:
PASS

mechanical zero incorrect DONE:
PASS

MECHANICAL CAUSAL ACTIVITY

U evaluations:
1037

nonzero teacher-vs-A25 U TV:
1037

realized U transition differences:
10

mean U TV:
0.0047391687

first state divergence epoch:
4

state-divergence epochs:
137

H learned probability differences:
0

H realized learned-controlled differences:
0

U_A0 correct DONE:
148

U_A25 correct DONE:
149

U_A0 incorrect DONE:
0

U_A25 incorrect DONE:
0

U_A0 expired:
0

U_A25 expired:
0

DECISION

Freeze the exact tested candidate source as LU2NF1.

Do not derive any LU-2N primary world before the freeze commit exists.

PLAIN-SPEAK INTERPRETATION

The concentrated-damage experiment is wired correctly.

The damage budget is identical to LU-2M: sixteen unavailable cells for twelve
epochs, one request per epoch, the same Task-2 job, the same expiry, and the
same 25-percent learned U authority.

The only scientific change is geometry: instead of spreading the sixteen
unavailable cells around the ring, all sixteen occupy one neighborhood.

In the fixed mechanical fixture the neural recruiter changes ten real U
decisions, while H and all committed-cell behavior remain hand-written.
Both arms still produce no wrong answers and no expiry.

The ten fresh worlds may now be derived from the frozen implementation.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
