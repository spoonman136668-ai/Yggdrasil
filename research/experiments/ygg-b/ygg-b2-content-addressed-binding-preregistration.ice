STATUS_NOTE: SUPERSEDED BEFORE RESULT
AUTHORITATIVE_PREREG: 4713b8d26aa9328ee6a6cebaf0a9fa07169d4d49
AUTHORITATIVE_FILE: research/experiments/ygg-b/ygg-b2-content-binding-preregistration.ice
REASON: The concurrent B2 preregistration above was committed earlier and is the one bound by the executable. This later file is unbound and retained only as an audit record.

TITLE: YGG-B2 Content-Addressed Binding Preregistration
DATE: 2026-09-24
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_RESULT: b33daf3538c987a10df6826a826c057f08ba9476
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Can the same bounded recurrent-state principle that passed YGG-B1 retrieve a value by content key rather than by a fixed sequence position?

SCIENTIFIC CHANGE FROM YGG-B1
Change only the sequence task from fixed-lag symbol recall to key-value binding with a terminal key query.
Do not increase hidden-state width.

FROZEN MODEL
hidden_state_width=16
token_embedding_width=8
position_signal=normalized_scalar_0_to_1
state_update=gated_residual_candidate
candidate=tanh(Wc[token_embedding,position,state]+bc)
gate=sigmoid(Wg[token_embedding,position,state]+bg)
new_state=gate*old_state+(1-gate)*candidate
readout=linear_terminal_state_to_8_value_classes
optimizer=Adam
learning_rate=0.01
loss=cross_entropy_terminal_target
torch_num_threads=1
deterministic_algorithms=true
training_seeds=101,202,303,404,505

TASK
keys=4
values=8
bindings_per_sequence=4
sequence_tokens=9
token_vocabulary=16

Each sample contains all four distinct keys in a fresh random order.
Each key is bound to one of four distinct values sampled without replacement from the eight value classes.
Bindings are serialized as:
KEY_1, VALUE_1, KEY_2, VALUE_2, KEY_3, VALUE_3, KEY_4, VALUE_4, QUERY_KEY
The terminal QUERY_KEY is sampled uniformly from the four keys.
The target is the value bound to that queried key.

TOKEN IDS
binding key tokens: 0..3
value tokens: 4..11
terminal query-key tokens: 12..15

DATA
train_examples=4096
heldout_examples=2048
batch_size=256
epochs=50
Training and held-out samples use disjoint deterministic generators.
Binding order, queried key, and values are independently resampled per example.

CONTROLS
1. persistent_state:
   normal recurrent state across the complete sequence.

2. reset_state:
   zero recurrent state before every token.
   This leaves the terminal query but destroys earlier binding memory.

3. shuffled_binding:
   keep the same keys, values, query, and target label, but apply a deterministic derangement of the four VALUE tokens among key slots.
   The original target value remains present in the sequence but is no longer paired with the queried key.
   No value may remain attached to its original key.

SUCCESS
PASS only if all frozen gates hold:
- minimum persistent held-out accuracy across five seeds >= 0.90
- median persistent held-out accuracy >= 0.95
- maximum reset-state accuracy across five seeds <= 0.25
- maximum shuffled-binding accuracy across five seeds <= 0.25
- minimum persistent-minus-reset gap across five seeds >= 0.60
- minimum persistent-minus-shuffled gap across five seeds >= 0.60
- all five seeds satisfy persistent > reset and persistent > shuffled
- duplicate complete execution is byte-identical

FAILURE
Any unmet preregistered gate is a scientific negative unless an independently demonstrated infrastructure or artifact defect explains it.
Do not tune thresholds, capacity, optimizer, dataset size, epochs, or controls after observing results.

INTERPRETATION BOUNDARY
A positive result would establish bounded content-addressed key-value binding under this synthetic task.
It would not establish natural-language competence, variable-length generalization, compositional syntax, semantic understanding, or long-context language modeling.

AUTHORITY BOUNDARY
This lane does not modify LU-2V.
No learned C/S developmental authority.
No online adaptation.
No recursive self-modification.
No shared-baseline promotion from this lane alone.
