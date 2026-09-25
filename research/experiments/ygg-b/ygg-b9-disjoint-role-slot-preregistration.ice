TITLE: YGG-B9 Disjoint Role-Slot Cartesian Holdout Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 7e9640e2328eebeb154ca4baf7cdb26553b9a0a7
PARENT_EXPERIMENT: YGG-B8

QUESTION
Can explicit disjoint role subspaces remove the residual cross-role address interference that remained under B7 sign binding and B8 orthogonal mixing, while preserving the exact compact persistent-state budget and frozen role-conditioned compositional task?

FROZEN FROM YGG-B6/B7/B8
- exact entity/role/value task and 14-token sequence;
- exact two-entity, two-role, four-binding structure;
- exact Cartesian held-out triple rule: (key + 2*role + value) mod 4 == 0;
- exact train/evaluation generation;
- train_examples=8192;
- eval_examples=4096;
- batch_size=256;
- epochs=75;
- optimizer=Adam;
- learning_rate=0.005;
- seeds=111,222,333,444,555;
- exact RESET, VALUE_SHUFFLE, and ROLE_FLIP controls;
- exact B7/B8 success thresholds;
- persistent_state_scalars=16;
- deterministic CPU execution.

SCIENTIFIC CHANGE
Learn one shared four-dimensional entity code e(k).
Place that code into one of two fixed, disjoint four-dimensional role slots:

address(k,R0) = L2_normalize([e(k), 0,0,0,0])
address(k,R1) = L2_normalize([0,0,0,0, e(k)])

The same slot construction is used for memory write and query read.

MODEL
entity/key embedding: 8 x 4
fixed role-slot operator: non-learned
value embedding: 8 x 1
terminal readout: linear 1 -> 8 classes
learned_parameters=56

PERSISTENT STATE
Memory M: 1 x 8 = 8 scalars.
Pending address register: 8 scalars.
Total persistent_state_scalars=16 exactly.

No attention.
No external memory.
No learned role parameters.
No extra recurrent hidden state.
No position embedding.
No evaluation-time adaptation.

STRUCTURAL CONSEQUENCE
For every entity pair:
dot(address(k,R0), address(j,R1)) = 0 exactly.
Thus cross-role address interference is eliminated by construction; within-role entity discrimination remains learned.

RATIONALE
B6 additive addresses produced approximately 0.38-0.43 OOD accuracy.
B7 fixed sign binding improved to approximately 0.66-0.85 but retained severe address cosine collisions.
B8 globally mixing orthogonal transforms remained approximately 0.66-0.85 and still showed severe collisions on several seeds.
B9 tests the narrower hypothesis that explicit role subspaces, rather than another rotation of a shared address space, are required.

SUCCESS
Use the frozen B7/B8 thresholds unchanged:
- minimum OOD persistent accuracy >= 0.90
- median OOD persistent accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum value-shuffle degradation >= 0.40
- minimum role-flip degradation >= 0.40
- all five seeds persistent > reset, value-shuffle, and role-flip
- persistent state exactly 16 scalars
- learned parameter count exactly 56
- no held-out triple appears in training
- all 32 held-out triples appear in scored evaluation for every seed
- duplicate complete execution byte-identical

MECHANICAL DIAGNOSTIC
Before interpreting the primary result, confirm exactly:
- every R0 address has zero entries in dimensions 4..7;
- every R1 address has zero entries in dimensions 0..3;
- cross-role dot product is exactly zero within floating-point tolerance <= 1e-7;
- state budget is exactly 16;
- learned parameter count is exactly 56.

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not change slot width, thresholds, seeds, training schedule, state budget, data, or controls after observing results.

INTERPRETATION
Positive: explicit structural role separation resolves the role-conditioned binding boundary under the same persistent-state budget.
Negative: eliminating cross-role interference is insufficient, locating the next limitation in within-role entity/value representation or the scalar value channel.

BOUNDARY
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
