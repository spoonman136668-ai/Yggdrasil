TITLE: YGG-B2 Content-Addressed Binding Preregistration
DATE: 2026-09-24
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_RESULT: b33daf3538c987a10df6826a826c057f08ba9476

QUESTION
Can the same bounded recurrent cellular state retrieve an earlier value by content key rather than by fixed sequence position?

TASK
Each example contains four key-value bindings followed by one query token.

Token ranges:
keys: 0..7
values: 8..15
queries: 16..23

Sequence form:
K1,V1,K2,V2,K3,V3,K4,V4,Q(Kx)

The four keys are distinct.
The query selects one of those four keys.
The target is the value paired with that key.

FROZEN MODEL
token_embedding_width=8
state_width=16
position_signal=none
state_update=gated_residual_candidate
candidate=tanh(Wc[token_embedding,state]+bc)
gate=sigmoid(Wg[token_embedding,state]+bg)
new_state=gate*old_state+(1-gate)*candidate
readout=linear_terminal_state_to_8_value_classes

FROZEN TRAINING
train_examples=8192
heldout_examples=4096
batch_size=256
epochs=75
optimizer=Adam
learning_rate=0.005
loss=cross_entropy
training_seeds=111,222,333,444,555
torch_num_threads=1
deterministic_algorithms=true

CONTROLS
RESET:
zero recurrent state before every token.

BINDING_SHUFFLE:
on held-out examples, permute the four value tokens among the four keys with a fixed seed while keeping the original target label and terminal query.

SUCCESS
min persistent held-out accuracy >= 0.90
max reset accuracy <= 0.35
min persistent-reset gap >= 0.50
min binding-shuffle degradation >= 0.40
all five seeds preserve persistent > reset and persistent > binding-shuffle
median persistent held-out accuracy >= 0.95
duplicate evidence byte-identical

FAILURE
Any unmet gate is a scientific negative. Do not tune thresholds or state width after observing results.

BOUNDARY
This tests bounded associative binding, not free-form language generation.
No external memory, attention, Transformer block, pretrained model, or evaluation-time adaptation.
No shared-baseline promotion from this lane alone.
