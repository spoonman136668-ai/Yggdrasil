TITLE: TASK-1H PRE-T1HF1 MECHANICAL GATE
DATE: 2026-09-23
STATUS: PASS / T1HF1 FREEZE AUTHORIZED
TRACK: DG-1 / TASK-1H

PREREGISTRATION:
1e284a15d0e176cbee09c57a1e219ba6927f05b0

PARENT TASK-1F T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063

PARENT TASK-1F SOURCE SHA256:
a3122a9f4f6da6c138cc12944528f5e2e3ef608e904067ef30da7feab7d640f4

PARENT TASK-1F CLOSURE:
fda86a2fee99fb948524b53b0eb0652011d655f6

SERVICE-ENVELOPE AUDIT:
e6ea693894ab12a6d542d50e297e97abf801124c

PURPOSE

Mechanically prove the Task-1H confirmation driver
before T1HF1 and before any primary world exists.

Task-1H adds no dynamics.

The candidate delegates both:

GLOBAL_HEDGE;

LOCAL_HEDGE;

directly to the exact frozen Task-1F R1 implementation.

The only Task-1H additions are:

fresh post-freeze manifest derivation;

confirmation scoring;

and observation-only service-envelope telemetry.

CANDIDATE SOURCE

bytes:
15363

SHA256:
076e67aef313943fdcd5545ed8c888b6630431638bd158be4e705d81ebebe445

DETERMINISTIC PUBLICATION

gzip level:
9

gzip mtime:
0

gzip bytes:
4336

gzip SHA256:
6216d22a9bf789a984bf0bb295f07a7a15126de440000b120fcb01edcf3a9221

base64 characters:
5784

base64 SHA256:
7875afd9e96adbfcb16502584c3d355ff9cbc6a936745b9bdfbbed8ae47d0750

source chunks:
3

chunk sizes:
2048;
2048;
1688.

MECHANICAL SWEEPS

Two complete mechanical replicate sweeps
inside the gate are byte-identical.

Canonical per-sweep bytes:
36620.

Canonical per-sweep SHA256:
824bcf02b6fa34642ebbffa9409bfb910986867cc02fc53bf571364d67114279.

The full mechanical-gate invocation
was itself executed twice.

Full gate-output bytes:
37135 each.

Full gate-output SHA256:
210e6826f2188fd4592fb9f5b9ecdffadace7ba2794448de8146e52d1d680fd1.

Full gate outputs byte-identical:
true.

PROBES

GLOBAL_HEDGE exact Task-1F R1 parity:
PASS.

LOCAL_HEDGE exact Task-1F R1 parity:
PASS.

LOCAL_HEDGE mechanism active:
PASS.

No dynamics reimplementation:
PASS.

D2:
PASS.

G5_FULL OFF:
PASS.

N = 64:
PASS.

R_TASK = 2:
PASS.

Request-bound handoff preserved:
PASS.

Neutral sensing preserved:
PASS.

One operation per cell per epoch:
PASS.

One operation per request per epoch:
PASS.

Primary-format manifest JSON round-trip:
PASS.

Duplicate mechanical determinism:
PASS.

Runtime integrity:
PASS.

OBSERVATION TELEMETRY BOUNDARY

Task-1H wraps the inherited request constructor
and inherited operation function only for read-only observation.

It records:

age at first VERIFY;

remaining lifetime at first VERIFY;

remaining lifetime when corruption is first detected;

deadline-impossible detections under the unchanged 32-epoch expiry;

and repaired requests censored by the fixed horizon.

The wrapper calls the exact inherited operation function
for every modeled state transition.

It does not alter:

request state;

operation selection;

operation ordering;

randomness;

expiry;

repair;

verification;

V0 dynamics;

LOCAL_HEDGE equations;

or any scientific threshold.

FREEZE AUTHORIZATION

The exact candidate above may freeze as T1HF1.

Only after T1HF1 exists may the five Task-1H primary manifests
be derived from:

TASK1H-CONFIRM | T1HF1 | k

and:

TASK1H-PRIMARY-SEED | T1HF1 | k

for k = 1..5.

No Task-1H primary arm has executed.

No Task-1H primary manifest has been derived or observed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
