TITLE: YGG-A1 Fork Join Exact Parent Feasibility Preregistration
DATE: 2026-09-24
STATUS: PREREGISTERED
LANE: YGG-A
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Does the exact accepted Task-4 teacher substrate remain functionally feasible when compositional structure changes from a straight A -> B -> C -> D chain to a fork/join dependency graph A -> {B,C} -> D?

ONLY SCIENTIFIC CHANGE
Task dependency graph.

For each request:
A = f_A(x0,x1,x2,x3)
B = f_B(A,x1,x2,x3)
C = f_C(A,x1,x2,x3)
D = f_D(A,B,C,x3)

B and C are independent siblings after A. D is forbidden until both exist.
Even request IDs execute B before C. Odd request IDs execute C before B.

FROZEN INHERITANCE
N=64, T=160, D=2, R_TASK=2, one request/epoch, four PROCESS operations/request, route_edges=6, expiry=32, inherited phase schedule, lesion, anchor relocation, corruption, repair/reverify contract, teacher policy, and observation substrate.

NO AUTHORITY EXPANSION
No learned-U authority in A1. No learned C/S authority. No online adaptation. No recursive self-modification.

EVIDENCE
Ten fresh deterministic primary worlds derived from this preregistration lineage and replicate IDs 1..10.
Duplicate primary execution must be byte-identical before qualification.

SUCCESS
PASS only if:
- at least 8/10 worlds satisfy the inherited exact-parent feasibility envelope;
- incorrect DONE is zero in all worlds;
- duplicate/matching integrity remains exact;
- B/C sibling ordering is independently exercised in both orders;
- D is never executed before both siblings exist;
- corruption detection, full recomputation, independent reverify, and terminal maturity rules remain intact.

FAILURE
Any failed preregistered gate is a scientific negative unless an independently demonstrated infrastructure/artifact defect explains it.

BOUNDARY
Do not change frozen thresholds after observing results.
Do not increase learned authority.
Do not promote the shared baseline from this lane alone.
