TITLE: YGG-B3 Factorized Relational State Preregistration
DATE: 2026-09-24
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_RESULT: 6b39bf573b2b0a758ac0525aa6a49f5ef6807f1b
PARENT_PREREG: 4713b8d26aa9328ee6a6cebaf0a9fa07169d4d49

QUESTION
Does an explicit bounded relational binding operation solve the YGG-B2 key-value failure without increasing persistent state beyond 16 scalars?

SCIENTIFIC CHANGE FROM YGG-B2
Change only the state-update mechanism.
Keep the YGG-B2 task, tokenization, dataset sizes, optimizer, seeds, controls, and qualification thresholds.

TASK INHERITANCE
keys=8
values=8
bindings_per_sequence=4
sequence=K1,V1,K2,V2,K3,V3,K4,V4,Q(Kx)
four keys distinct
query selects one present key
target is the value paired with that key
binding order randomized per example
training examples=8192
heldout examples=4096

PERSISTENT STATE
Exactly 16 floating-point scalars:
- relational matrix M: 3 x 4 = 12 scalars
- pending key register p: 4 scalars

LEARNED REPRESENTATIONS
key_embedding: 8 x 4, shared between binding and query, L2-normalized on use
value_embedding: 8 x 3
terminal_readout: linear 3 -> 8 classes

FROZEN UPDATE ALGEBRA
On KEY(k):
- preserve M
- set p = normalized key_embedding[k]

On VALUE(v):
- M = M + outer(value_embedding[v], p)
- clear p to zero

On QUERY(k):
- read = M @ normalized key_embedding[k]
- logits = terminal_readout(read)

No attention.
No external memory.
No additional recurrent hidden state.
No position signal.
No learned gate.
No evaluation-time adaptation.

TRAINING
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
zero all 16 persistent state scalars before every token.

BINDING_SHUFFLE:
use the exact YGG-B2 held-out binding-shuffle construction and fixed per-seed shuffle procedure, preserving original target labels and terminal queries.

SUCCESS
Use the exact YGG-B2 thresholds:
- minimum persistent held-out accuracy >= 0.90
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum binding-shuffle degradation >= 0.40
- all five seeds persistent > reset and persistent > binding-shuffle
- median persistent held-out accuracy >= 0.95
- duplicate complete execution byte-identical

FAILURE
Any unmet gate is a scientific negative.
Do not increase state dimensions, change thresholds, tune seeds, change dataset size, or alter training mechanics after observing results.

INTERPRETATION
A positive result would show that explicit factorized relational binding can recover content-addressed association where generic 16-state recurrence failed.
It would not establish natural-language competence, syntax, semantic reasoning, variable-length generalization, or long-context language modeling.

AUTHORITY BOUNDARY
No LU-2V mutation.
No learned C/S developmental authority.
No online adaptation.
No recursive self-modification.
No shared-baseline promotion from this lane alone.
