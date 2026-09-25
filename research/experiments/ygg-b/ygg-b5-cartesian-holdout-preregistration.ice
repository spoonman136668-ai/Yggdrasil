TITLE: YGG-B5 Cartesian Holdout Compositional Binding Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_RESULT: f32f387b2048c7c2423346f4d509f2e44774637b
PARENT_PREREGISTRATION: f4a67d36b972efe2406c5323ae7f45ee45e0a57f

QUESTION
Does the frozen positive YGG-B4 factorized binding mechanism generalize compositionally to key/value combinations that are never observed during training?

SCIENTIFIC CHANGE FROM YGG-B4
Keep the B4 model, state budget, parameter budget, sequence format, optimizer, training size, evaluation size, epochs, seeds, controls, and qualification thresholds unchanged.
Change only the train/evaluation support so a deterministic Cartesian subset of key/value pairs is withheld from all training bindings and used as the queried relation at evaluation.

HOLDOUT RULE
keys=0..7
values=0..7
A key/value pair is held out iff:
(key + value) mod 4 == 0

This withholds exactly 16 of 64 possible key/value combinations.
Every key and every value still appears in allowed training combinations.

TRAINING DATA
Same B4 sequence:
K1,V1,K2,V2,K3,V3,K4,V4,Q(Kx)
four distinct keys
bindings_per_sequence=4

All four training bindings must come from the 48 allowed key/value combinations.
The query selects one of the four present keys.
The target is its paired value.

train_examples=8192
batch_size=256
epochs=75
optimizer=Adam
learning_rate=0.005
training_seeds=111,222,333,444,555
torch_num_threads=1
deterministic_algorithms=true

OOD EVALUATION DATA
heldout_examples=4096
For every evaluation sequence:
- choose four distinct keys;
- choose exactly one queried key;
- assign the queried key a value satisfying the holdout rule;
- assign the other three keys values from allowed training combinations;
- query the held-out binding;
- target is the held-out value.

Thus the scored target relation is a key/value composition absent from training while both constituent key and value identities remain familiar.

MODEL
Exact YGG-B4 model:
key_embedding: 8 x 8, shared between binding and query, L2-normalized on use
value_embedding: 8 x 1
terminal_readout: linear 1 -> 8 classes
persistent_state_scalars=16
learned_parameters=88

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
RESET: exact B4 reset-each-step control on the same OOD evaluation set.
BINDING_SHUFFLE: exact B4 value-column derangement procedure on the same OOD evaluation set.

SUCCESS
Use the exact B4 thresholds unchanged:
- minimum OOD persistent held-out accuracy >= 0.90
- median OOD persistent held-out accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum binding-shuffle degradation >= 0.40
- all five seeds persistent > reset and persistent > binding-shuffle
- persistent state exactly 16 scalars
- learned parameter count exactly 88
- all 16 held-out key/value combinations represented in the scored evaluation corpus for every seed
- no held-out key/value combination appears in the training corpus
- duplicate complete execution byte-identical

DIAGNOSTICS
Report per seed:
- OOD persistent accuracy
- reset accuracy
- binding-shuffle accuracy
- persistent-reset gap
- binding-shuffle degradation
- number of distinct held-out pairs in evaluation
- maximum absolute off-diagonal cosine similarity of normalized learned key embeddings

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not change the holdout rule, thresholds, training schedule, data size, seeds, model dimensions, state budget, or parameter budget after observing results.

INTERPRETATION
A positive B5 would demonstrate exact controlled compositional generalization to unseen key/value combinations in the B4 relational memory mechanism.
A negative B5 would show that B4's perfect IID binding does not transfer to Cartesian holdout composition under the same resource budget.

BOUNDARY
No LU-2V mutation.
No learned developmental C/S authority.
No online adaptation.
No recursive self-modification.
No shared-baseline promotion from this lane alone.
