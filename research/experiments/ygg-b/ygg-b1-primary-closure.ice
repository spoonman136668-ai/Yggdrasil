TITLE: YGG-B1 Persistent Sequence Memory Primary Closure
DATE: 2026-09-24
STATUS: CLOSED / PASS
LANE: YGG-B
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

PREREGISTRATION:
d210b0ea6f5d65fb7c8cca2551bcd7658de37899

PRIMARY RUN:
36073229204

PRIMARY HEAD:
e74f910d007fff4c23f7758306c9d1ca8c75d6af

DUPLICATE EVIDENCE
byte_identical: TRUE
sha256: 3db74e4e11a70f2536ddcd76158a4b1707130fe2a6bcb5f5c75a29a0c52a6e05

SCIENTIFIC STATUS
YGG_B1_PERSISTENT_SEQUENCE_MEMORY: TRUE

MODEL
parameter_count: 1032
state_width: 16
token_embedding_width: 8
sequence_length: 16
dependency_lag: 8
vocabulary: 8

PER-SEED RESULTS
seed 101: persistent=1.000000 reset=0.1318359375 shuffle=0.1865234375
seed 202: persistent=1.000000 reset=0.1367187500 shuffle=0.1845703125
seed 303: persistent=1.000000 reset=0.13720703125 shuffle=0.19189453125
seed 404: persistent=1.000000 reset=0.1328125000 shuffle=0.18310546875
seed 505: persistent=1.000000 reset=0.13427734375 shuffle=0.2041015625

QUALIFICATION
min persistent >= 0.90: PASS
max reset <= 0.70: PASS
min persistent-reset gap >= 0.20: PASS
min shuffle degradation >= 0.15: PASS
all five seeds causal direction: PASS
median persistent >= 0.95: PASS

INTERPRETATION
A 1,032-parameter bounded recurrent cellular state learned to retain and causally use an earlier symbol across an eight-position delay.

The reset control remained near the 1/8 chance level.
Shuffling the earlier history while preserving the target label destroyed most performance.
Therefore the terminal prediction depends on carried sequence state rather than only the final symbol or class imbalance.

BOUNDARY
This is evidence for bounded persistent sequence memory.
It is not yet evidence for variable-length language modeling, content-addressed binding, compositional syntax, or long-context generalization.
The normalized position signal and fixed sequence length remain possible simplifications.

NEXT SCIENTIFIC UNCERTAINTY
Can the same bounded-state principle perform content-addressed binding rather than fixed-position recall?

NEXT JUSTIFIED DIRECTION
Test a key-value sequence in which a terminal query specifies which earlier binding must be retrieved.
Use shuffled-binding and reset-state controls.
Do not increase state width before measuring the 16-state baseline.

No shared-baseline promotion is authorized by this lane-local closure.
