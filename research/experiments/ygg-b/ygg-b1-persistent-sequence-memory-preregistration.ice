TITLE: YGG-B1 Causal Persistent Sequence Memory Preregistration
DATE: 2026-09-24
STATUS: PREREGISTERED
LANE: YGG-B
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Can the accepted LU-2V developmental transport, verification, and repair substrate preserve task-relevant state across a causal token sequence when earlier tokens are no longer observable?

ROLE
This is a pre-language diagnostic. It tests a necessary sequence-memory primitive only. It is not evidence of natural-language competence.

ONLY SCIENTIFIC CHANGE
Replace the static four-bit request input with an ordered four-token binary sequence presented one token at a time.

SEQUENCE TASK
For tokens x0,x1,x2,x3 in {0,1}:
h0 = x0
h1 = h0 XOR x1
h2 = h1 XOR x2
h3 = h2 XOR x3
target = h3

At step k, only xk may be newly observed. Earlier raw tokens are unavailable to later task stages. Any information needed from them must persist through the request/developmental state.

ANTI-SHORTCUT FIXTURES
Include matched sequence pairs with identical suffixes and different prefixes, including:
0000 vs 1000
0111 vs 1111
0010 vs 1010
0101 vs 1101
The paired targets must differ. A suffix-only strategy therefore fails deterministically.

FROZEN INHERITANCE
Keep the accepted LU-2V substrate unchanged: N=64, T=160, D=2, R_TASK=2, one request/epoch, route_edges=6, expiry=32, inherited phase schedule, lesion, anchor relocation, corruption, repair/reverify contract, teacher policy, observation substrate, and accepted authority boundaries.

NO AUTHORITY EXPANSION
No learned-U authority. No learned C/S authority. No online adaptation. No recursive self-modification. No natural-language model is introduced in B1.

EVIDENCE
Ten fresh deterministic primary worlds derived from this preregistration lineage and replicate IDs 1..10.
Duplicate primary execution must be byte-identical before qualification.
The anti-shortcut fixtures are mandatory and scored.

SUCCESS
PASS only if:
- all anti-shortcut fixtures produce the exact causal target;
- at least 8/10 worlds satisfy the inherited feasibility envelope;
- incorrect DONE is zero in all worlds;
- duplicate/matching integrity remains exact;
- earlier raw tokens are not readable after their presentation step;
- corruption detection, full recomputation, independent reverify, and terminal maturity rules remain intact.

FAILURE
Any failed preregistered gate is a scientific negative unless an independently demonstrated infrastructure or artifact defect explains it.

BOUNDARY
Do not tune the sequence rule, thresholds, fixtures, seeds, or qualification criteria after observing results.
Do not promote the shared baseline from this lane alone.
