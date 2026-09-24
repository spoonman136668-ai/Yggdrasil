TITLE: LU-2O LU-2N EXACT-PARENT REPAIR-TIMING AUDIT CLOSURE
DATE: 2026-09-24
STATUS: CLOSED / HORIZON TRUNCATION SUPPORTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
0102a36037d1db57fdc51d137004e5b9705fb0d7

PARENT LU-2N CLOSURE:
096c8dee7ae368f69e322be8e1b8a5ca20feff08

PARENT LU2NF1:
a4657c94a654d2b4f83b6af0c7844b65e6999593

ACCEPTED LU-2N PRIMARY SHA256:
a742491a9282e346d848850000c0f24a3f6ea7fdf4b8c62eefa35e7f31432d77

DIAGNOSTIC RUN:
36057264057

DIAGNOSTIC HEAD:
d556691c7a84b18f9b44398e2031edb80cb9920f

DIAGNOSTIC ARTIFACT:
10832942524

DUPLICATE DIAGNOSTIC OUTPUT

bytes each:
54863

SHA256 both:
fbf871b37064ed31ef482fcf591ad2743f5904f3c14fcc1ef72f537b6e887d32

byte-identical:
TRUE

REPLAY INTEGRITY

All ten U_A0 replay projections matched the accepted LU-2N evidence exactly.

LU2O_REPLAY_INTEGRITY:
TRUE

No timing interpretation was made before this gate passed.

FAILED-WORLD TIMING

replicate 5

request id:
412

arrival:
137

first egress:
158

first verification detection:
159

epochs remaining after detection:
0

repair epoch:
none

successful reverify:
none

DONE:
none

terminal state:
REPAIR_PENDING

expired:
no


replicate 8

request id:
430

arrival:
143

first egress:
158

first verification detection:
159

epochs remaining after detection:
0

repair epoch:
none

successful reverify:
none

DONE:
none

terminal state:
REPAIR_PENDING

expired:
no


replicate 10

request id:
424

arrival:
141

first egress:
158

first verification detection:
159

epochs remaining after detection:
0

repair epoch:
none

successful reverify:
none

DONE:
none

terminal state:
REPAIR_PENDING

expired:
no

CLASSIFICATION

LU2O_HORIZON_TRUNCATION_SUPPORTED:
TRUE

LU2O_DEEPER_REPAIR_CAPACITY_DEFECT_SUPPORTED:
FALSE for the three observed LU-2N baseline failures.

RATIONALE

In every failed exact-parent world:

- the corrupted request reached egress;
- verification correctly detected the corruption;
- detection occurred on the final simulated epoch;
- zero service epochs remained;
- the request ended in the correct next repair state;
- no incorrect DONE occurred;
- no expiry occurred.

The Task-2 lifecycle requires separate operations for:

detection;
repair;
successful re-verification;
and subsequent DONE finalization.

A request first detected at epoch 159 cannot complete that sequence inside a
simulation that ends after epoch 159.

Therefore the LU-2N baseline failures are caused by the evaluation horizon
ending while a valid repair is in progress.

This does not alter the sealed LU-2N FALSE verdict.

SECONDARY UNRESOLVED SIGNAL

LU-2N replicate 1 still contains the separate descriptive signal:

U_A0 anchor recovery = 2
U_A25 anchor recovery = null

That signal was not diagnosed in LU-2O because exact-parent repair timing was
the preregistered first question.

NEXT SCIENTIFIC QUESTION

Run a fresh contiguous-lesion experiment with unchanged organism dynamics and
a mechanics-derived maturity-conditioned repair contract.

Do not retroactively rescore LU-2N.

A corruption detected too late to physically complete
detect -> repair -> reverify -> DONE before epoch 160 must be classified as
terminal in-flight work rather than a completed-repair failure.

All mature repair opportunities must still complete strictly.

PLAIN-SPEAK INTERPRETATION

We found the reason.

The three supposed parent repair failures were all the same thing: a bad
request reached verification on the very last tick, the organism detected it
correctly, switched it into repair, and then the experiment stopped.

There was literally no next tick available to perform the repair.

So concentrated damage did not expose a broken repair mechanism in those
three worlds.

It exposed an evaluation rule that was asking a multi-step repair to finish
after the clock had already run out.

The right next test is fresh worlds with the same organism and the same
damage, but a scoring rule that only demands completed repair when enough
service ticks physically existed to complete it.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
