TITLE: YGG-B7 Multiplicative Role-Binding Cartesian Holdout Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: ec43ed86a3adc889a0ebec36dccccf97f1827fe4
PARENT_EXPERIMENT: YGG-B6

QUESTION
Was YGG-B6 limited primarily by interference from the additive key-plus-role address representation, and can an explicit multiplicative role-binding operator recover role-sensitive compositional generalization without increasing persistent state?

FROZEN FROM YGG-B6
- exact entity/role/value task and 14-token sequence structure;
- exact two-entity, two-role, four-binding examples;
- exact Cartesian held-out triple rule: (key + 2*role + value) mod 4 == 0;
- exact training and evaluation corpora generation;
- train_examples=8192;
- eval_examples=4096;
- batch_size=256;
- epochs=75;
- optimizer=Adam;
- learning_rate=0.005;
- seeds=111,222,333,444,555;
- torch_num_threads=1;
- deterministic algorithms;
- exact RESET, VALUE_SHUFFLE, and ROLE_FLIP controls;
- exact B6 success thresholds;
- persistent_state_scalars=16.

SCIENTIFIC CHANGE
Remove the learned additive role embedding.
Bind role to key multiplicatively with fixed deterministic sign masks:
R0 = [+1,+1,+1,+1,+1,+1,+1,+1]
R1 = [+1,-1,+1,-1,+1,-1,+1,-1]

address(k,r) = L2_normalize(key_embedding[k] * Rr)

Use the same address operator for writing and querying.

MODEL
key_embedding: 8 x 8
fixed role masks: 2 x 8, non-learned
value_embedding: 8 x 1
terminal_readout: linear 1 -> 8 classes
persistent_state_scalars=16
learned_parameters=88

No attention.
No external memory.
No learned role embedding.
No additional recurrent hidden state.
No position embedding.
No evaluation-time adaptation.

RATIONALE
B6 retained causal persistent-state benefit but achieved only approximately 0.38 to 0.43 OOD accuracy and showed high address cosine interference. B7 changes only the role-binding geometry. The fixed sign operation can separate roles without consuming additional learned parameters or persistent state.

SUCCESS
Use B6 thresholds unchanged:
- minimum OOD persistent accuracy >= 0.90
- median OOD persistent accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum value-shuffle degradation >= 0.40
- minimum role-flip degradation >= 0.40
- all five seeds persistent > reset, value-shuffle, and role-flip
- persistent state exactly 16 scalars
- learned parameter count exactly 88
- no held-out triple appears in training
- all 32 held-out triples appear in scored evaluation for every seed
- duplicate complete execution byte-identical

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not tune the role masks, thresholds, training schedule, seeds, state budget, or holdout rule after observing results.

INTERPRETATION
Positive: explicit multiplicative role binding resolves the B6 address-interference boundary under the same compact persistent-state budget.
Negative: the B6 limitation is not resolved by this simple role-binding operator; advance to a new preregistered representation or structural hypothesis.

BOUNDARY
No shared-baseline promotion from this lane alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
