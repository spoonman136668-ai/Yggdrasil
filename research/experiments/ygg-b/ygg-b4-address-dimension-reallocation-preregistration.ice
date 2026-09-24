TITLE: YGG-B4 Address-Dimension Reallocation Preregistration
DATE: 2026-09-24
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_RESULT: ad853adb938a4f992cbd19e2624674107987c924
PARENT_PREREG: 970d3b52c3fed6a8085d1224a98c5616c996f29b

QUESTION
Was YGG-B3's remaining binding error caused primarily by key-address interference from representing eight possible keys in only four key dimensions?

ONLY SCIENTIFIC CHANGE FROM YGG-B3
Reallocate the same 16 persistent scalars and the same 88 learned parameters between key and value factors.

B3:
key_dimension=4
value_dimension=3
relational_matrix=3x4=12
pending_key=4
persistent_state=16
learned_parameters=88

B4:
key_dimension=8
value_dimension=1
relational_matrix=1x8=8
pending_key=8
persistent_state=16
learned_parameters=88

Everything else remains frozen from B3/B2.

TASK
keys=8
values=8
bindings_per_sequence=4
sequence=K1,V1,K2,V2,K3,V3,K4,V4,Q(Kx)
four keys distinct
query selects one present key
target is the value paired with that key
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

LEARNED REPRESENTATIONS
key_embedding: 8 x 8, shared between binding and query, L2-normalized on use
value_embedding: 8 x 1
terminal_readout: linear 1 -> 8 classes

FROZEN UPDATE ALGEBRA
On KEY(k):
- preserve M
- set p = normalized key_embedding[k]

On VALUE(v):
- M = M + outer(value_embedding[v], p)
- clear p

On QUERY(k):
- read = M @ normalized key_embedding[k]
- logits = terminal_readout(read)

No attention.
No external memory.
No additional recurrent hidden state.
No position signal.
No learned gate.
No evaluation-time adaptation.

CONTROLS
Use the exact B2/B3 RESET and BINDING_SHUFFLE procedures unchanged.

SUCCESS
Use the exact B2/B3 capability thresholds unchanged:
- minimum persistent held-out accuracy >= 0.90
- median persistent held-out accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum binding-shuffle degradation >= 0.40
- all five seeds persistent > reset and persistent > binding-shuffle
- persistent state exactly 16 scalars
- learned parameter count exactly 88
- duplicate complete execution byte-identical

DIAGNOSTIC
Report the maximum absolute off-diagonal cosine similarity of the eight normalized learned key embeddings for each seed.
This diagnostic is descriptive and is not a qualification threshold.

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not change dimensions, thresholds, training schedule, data size, seeds, or controls after observing results.

INTERPRETATION
A positive B4 with negative B3 would support the hypothesis that B3 was limited by key-address interference rather than total persistent-state or parameter capacity.
A negative B4 would show that address dimensionality reallocation alone is insufficient.

BOUNDARY
No LU-2V mutation.
No learned developmental C/S authority.
No online adaptation.
No recursive self-modification.
No shared-baseline promotion from this lane alone.
