TITLE: YGG-B1 Sequence Memory
DATE: 2026-09-24
STATUS: PREREGISTERED
LANE: YGG-B
BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Can bounded recurrent cellular state preserve information from earlier sequence positions and use it for a delayed target?

FROZEN TASK
vocabulary 8
sequence length 16
dependency lag 8
state width 16
five training seeds
disjoint held-out evaluation

CONTROLS
persistent state
state reset between positions
fixed-seed shuffle of earlier symbols

SUCCESS
persistent held-out accuracy >= 0.90
reset accuracy <= 0.70
persistent-reset gap >= 0.20
shuffle degradation >= 0.15
median persistent accuracy >= 0.95
all five seeds preserve the expected causal direction

RULE
Any unmet gate is a scientific negative. Thresholds remain frozen after results.
This lane cannot promote the shared baseline by itself.

IMPLEMENTATION FREEZE
token_embedding_width=8
position_signal=normalized_scalar_0_to_1
state_update=gated_residual_candidate
candidate=tanh(Wc[token_embedding,position,state]+bc)
gate=sigmoid(Wg[token_embedding,position,state]+bg)
new_state=gate*old_state+(1-gate)*candidate
readout=linear_terminal_state_to_8_classes
train_examples=4096
heldout_examples=2048
batch_size=256
epochs=50
optimizer=Adam
learning_rate=0.01
loss=cross_entropy_terminal_target
training_seeds=101,202,303,404,505
torch_num_threads=1
deterministic_algorithms=true
shuffle_control=permute_positions_0_through_14_per_example_fixed_seed
reset_control=zero_state_before_each_position
