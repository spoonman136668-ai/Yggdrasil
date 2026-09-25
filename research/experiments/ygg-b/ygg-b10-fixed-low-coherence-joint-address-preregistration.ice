TITLE: YGG-B10 Fixed Low-Coherence Joint Address Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 540d004b8a99b3b909f074e143fd699f3c9a367d
PARENT_EXPERIMENT: YGG-B9

QUESTION
Are B6-B9 failing primarily because learned entity/role address geometry collapses, and can a fixed low-coherence joint entity-by-role codebook recover the frozen role-sensitive Cartesian-holdout capability under the same 16-scalar persistent-state budget?

FROZEN FROM B6-B9
- exact entity/role/value task and 14-token sequence;
- exact two-entity, two-role, four-binding structure;
- exact Cartesian held-out triple rule: (key + 2*role + value) mod 4 == 0;
- exact training/evaluation corpus generation;
- train_examples=8192;
- eval_examples=4096;
- batch_size=256;
- epochs=75;
- optimizer=Adam;
- learning_rate=0.005;
- seeds=111,222,333,444,555;
- exact RESET, VALUE_SHUFFLE, ROLE_FLIP controls;
- exact frozen success thresholds;
- persistent_state_scalars=16;
- deterministic CPU execution.

SCIENTIFIC CHANGE
Remove learned key and role address embeddings entirely.
Assign each of the 16 (key,role) addresses a fixed 8-dimensional sign code of unit norm.

Address index:
joint_index = 2*key + role

Raw codebook rows in joint_index order:
0  [1,1,1,1,1,1,1,1]
1  [1,1,1,1,1,1,-1,-1]
2  [1,1,1,1,1,-1,1,-1]
3  [1,1,1,1,1,-1,-1,1]
4  [1,1,1,1,-1,1,1,-1]
5  [1,1,1,1,-1,1,-1,1]
6  [1,1,1,1,-1,-1,1,1]
7  [1,1,1,1,-1,-1,-1,-1]
8  [1,1,1,-1,1,1,1,-1]
9  [1,1,1,-1,1,1,-1,1]
10 [1,1,1,-1,1,-1,1,1]
11 [1,1,1,-1,1,-1,-1,-1]
12 [1,1,1,-1,-1,1,1,1]
13 [1,1,1,-1,-1,1,-1,-1]
14 [1,1,1,-1,-1,-1,1,-1]
15 [1,1,1,-1,-1,-1,-1,1]

Each row is divided by sqrt(8).

GEOMETRY CONTRACT
- all 16 addresses are unique;
- every address has unit norm;
- no two addresses are equal or antipodal;
- maximum absolute off-diagonal address cosine is exactly 0.5;
- address geometry is fixed and non-learned.

MODEL
fixed joint address codebook: 16 x 8, non-learned
value embedding: 8 x 1
terminal readout: linear 1 -> 8 classes
learned_parameters=24

PERSISTENT STATE
Memory M: 1 x 8 = 8 scalars.
Pending address register: 8 scalars.
Total persistent_state_scalars=16 exactly.

TOKEN HANDLING
- KEY stores the key id as pending discrete routing metadata only until ROLE arrives.
- ROLE converts pending key plus current role to the fixed joint address and stores that 8-scalar address in the pending register.
- VALUE writes outer(value_embedding[value], pending_address) to M and clears pending.
- QUERY_KEY stores the query key id as pending discrete routing metadata only until QUERY_ROLE arrives.
- QUERY_ROLE resolves the same fixed joint address, reads M, and applies the frozen scalar readout.

The discrete key id used between KEY and ROLE is not persistent learned state and must not coexist with an address-valued pending register. For accounting, the scientific persistent state remains the exact 8-scalar memory plus 8-scalar address register used by the inherited B6-B9 model family.

RATIONALE
B9 made cross-role cosine exactly zero but same-role learned addresses collapsed to approximately 0.998-0.9998 absolute cosine.
B10 removes address learning as a confound and fixes all 16 joint addresses at bounded coherence <=0.5.
This separates address-geometry failure from limitations of the scalar value channel and superposition readout.

MECHANICAL GATE
Before interpreting primary results confirm:
- 16 unique addresses;
- unit norm within 1e-7;
- maximum absolute off-diagonal cosine <=0.5000001;
- no equal/antipodal pair;
- persistent state exactly 16 scalars;
- learned parameter count exactly 24;
- fixed codebook has requires_grad=false.

SUCCESS
Use the frozen B7-B9 capability thresholds unchanged:
- minimum OOD persistent accuracy >= 0.90
- median OOD persistent accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum value-shuffle degradation >= 0.40
- minimum role-flip degradation >= 0.40
- all five seeds persistent > reset, value-shuffle, and role-flip
- persistent state exactly 16 scalars
- learned parameter count exactly 24
- no held-out triple appears in training
- all 32 held-out triples appear in scored evaluation for every seed
- duplicate complete execution byte-identical

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not alter the codebook, thresholds, data, seeds, training schedule, state budget, or controls after observing results.

INTERPRETATION
Positive: learned address collapse was the principal B6-B9 bottleneck; later work may reintroduce learnable address mechanisms with explicit geometric constraints.
Negative: even bounded low-coherence joint addresses are insufficient, shifting the next hypothesis toward the scalar value channel or the superposition/readout mechanism.

BOUNDARY
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
