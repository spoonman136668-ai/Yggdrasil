TITLE: YGG-B16 Fixed Factorized Entity-Code Binding Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: 1dc476cb2d6f4597a7fae39bdef2440fe74614fb
PARENT_EXPERIMENT: YGG-B15

QUESTION
Is the two-entity failure isolated by B15 caused by interference in the learned entity-address geometry, such that a fixed factorized entity code restores compositional retrieval under the same two-entity/four-binding load and 24-scalar persistent-state budget?

NORTH-STAR TARGET
Resolve the entity-binding boundary before increasing sequence load or moving toward language capability.

FROZEN FROM YGG-B15
- exact two distinct entities per sequence;
- exactly two distinct ROLE×SLOT addresses per entity;
- four bindings total;
- sequence length=19;
- KEYS=8, ROLES=2, SLOTS=2, VALUES=8;
- address dimension=8;
- value dimension=2;
- memory shape=2x8;
- pending address register=8;
- persistent_state_scalars=24;
- exact ROLE masks;
- exact SLOT masks;
- exact training/evaluation corpus construction;
- exact Cartesian holdout rule;
- TRAIN_N=8192, EVAL_N=4096;
- batch_size=256, epochs=75, Adam lr=0.005;
- seeds=111,222,333,444,555;
- RESET, VALUE_SHUFFLE, ROLE_FLIP, SLOT_FLIP controls;
- deterministic CPU execution;
- all capability thresholds unchanged.

SCIENTIFIC CHANGE
Replace the learned 8x8 entity/key embedding with the following fixed, non-learned sign masks:

K0=[+1,-1,-1,-1,-1,-1,-1,-1]
K1=[+1,-1,-1,-1,+1,+1,+1,+1]
K2=[+1,-1,-1,-1,-1,-1,+1,+1]
K3=[+1,-1,-1,-1,+1,+1,-1,-1]
K4=[+1,-1,-1,-1,-1,+1,-1,+1]
K5=[+1,-1,-1,-1,+1,-1,+1,-1]
K6=[+1,-1,-1,-1,-1,+1,+1,-1]
K7=[+1,-1,-1,-1,+1,-1,-1,+1]

Address:
address(k,r,s)=normalize(KEY_MASK[k] * ROLE_MASK[r] * SLOT_MASK[s])

The entity, role, and slot factors therefore remain explicitly compositional and multiplicative.

FIXED CODE PROPERTIES
Under the frozen ROLE and SLOT masks:
- all 32 KEY×ROLE×SLOT addresses are unique;
- no antipodal duplicate is permitted;
- unit norm after normalization;
- maximum absolute off-diagonal cosine must equal 0.5.

MODEL
fixed key masks: non-learned
fixed role masks: non-learned
fixed slot masks: non-learned
value_embedding: 8 x 2
terminal_readout: linear 2 -> 8 classes
learned_parameters=40
persistent_state_scalars=24

No attention.
No external memory.
No learned entity/address vector.
No additional recurrent hidden state.
No evaluation-time adaptation.

SUCCESS
Same B15 capability thresholds:
- minimum OOD persistent accuracy >=0.90
- median OOD persistent accuracy >=0.95
- maximum reset accuracy <=0.35
- minimum persistent-reset gap >=0.50
- minimum value-shuffle degradation >=0.40
- minimum role-flip degradation >=0.40
- minimum slot-flip degradation >=0.40
- all five seeds persistent > reset, value-shuffle, role-flip, slot-flip
- persistent state exactly 24 scalars
- learned parameter count exactly 40
- no held-out quadruple in training
- all 64 held-out quadruples scored for every seed
- duplicate complete execution byte-identical.

MECHANICAL GATE
- fixed entity code exact;
- exact frozen ROLE/SLOT masks;
- 32 unique joint addresses;
- maximum absolute off-diagonal joint-address cosine exactly 0.5;
- no antipodal duplicates;
- two distinct entities per sequence;
- exactly two structural addresses per entity;
- four bindings total;
- sequence length=19;
- state=24;
- parameters=40.

INTERPRETATION
Positive:
Learned entity-address interference is a causal contributor to B15 and can be removed with a compact factorized entity code while preserving structural composition.

Negative:
The B15 entity-count boundary persists even with bounded fixed entity-address coherence; the remaining limitation is superposition/readout capacity or another interaction, not merely learned key geometry.

FAILURE
Do not alter masks, state budget, value width, thresholds, data, seeds, training schedule, or controls after observing results.

BOUNDARY
No shared-baseline promotion from B16 alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
