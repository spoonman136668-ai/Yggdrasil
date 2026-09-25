TITLE: YGG-B6 Role-Conditioned Cartesian Holdout Binding Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: a40e007cf7b3bce6b2a88da78ee91a420f2fd532
PARENT_EXPERIMENT: YGG-B5

QUESTION
Can the compact factorized persistent-memory mechanism extend from flat key/value composition to explicit role-sensitive relational binding, while generalizing to entity/role/value triples never observed during training?

SCIENTIFIC CHANGE FROM YGG-B5
Preserve the successful factorized matrix-memory principle, 16-scalar persistent-state budget, value dimension, training size, evaluation size, optimizer, epochs, seeds, deterministic execution discipline, and core accuracy thresholds.
Add an explicit two-role factor to the address. Each example contains two entities, both roles for each entity, and four values. The query specifies both entity and role.

STRUCTURAL REQUIREMENT
Every sequence contains:
- entity K0 with role R0 and role R1;
- distinct entity K1 with role R0 and role R1;
- one value bound to each of those four entity/role addresses;
- a query selecting one of the four addresses.

Because each entity appears under both roles in the same sequence, an entity-only solution is insufficient.

TOKENS AND SEQUENCE
bindings_per_sequence=4
binding form=KEY,ROLE,VALUE
query form=QUERY_KEY,QUERY_ROLE
sequence_length=14

KEYS=8
ROLES=2
VALUES=8

MODEL
key_embedding: 8 x 8
role_embedding: 2 x 8
value_embedding: 8 x 1
terminal_readout: linear 1 -> 8 classes

Address:
address(k,r) = L2_normalize(key_embedding[k] + role_embedding[r])

Persistent update:
- on KEY(k): pending = key_embedding[k]
- on ROLE(r): pending = L2_normalize(pending + role_embedding[r])
- on VALUE(v): M = M + outer(value_embedding[v], pending); clear pending
- on QUERY_KEY(k): pending = key_embedding[k]
- on QUERY_ROLE(r): q = L2_normalize(pending + role_embedding[r]); read = M @ q; logits = terminal_readout(read)

persistent_state_scalars=16
learned_parameters=104

No attention.
No external memory.
No additional recurrent hidden state.
No position embedding.
No evaluation-time adaptation.

CARTESIAN HOLDOUT
A triple (key,role,value) is held out iff:
(key + 2*role + value) mod 4 == 0

This withholds exactly 32 of 128 possible triples, exactly two values for every key/role address.
Every key, role, value, and key/role address remains represented in training through allowed triples.

TRAINING DATA
For each sequence choose two distinct keys.
Instantiate both roles for both keys, producing four key/role addresses.
All four training values must come from allowed triples.
The query selects one of the four addresses.
target=the value bound to the queried address.

train_examples=8192
batch_size=256
epochs=75
optimizer=Adam
learning_rate=0.005
training_seeds=111,222,333,444,555
torch_num_threads=1
deterministic_algorithms=true

OOD EVALUATION DATA
Use the same two-key/four-address structure.
The queried address receives a held-out value for that exact key/role address.
The other three bindings receive allowed values.
The target is the held-out value.

CONTROLS
RESET:
Reset M and pending state before every token.

VALUE_SHUFFLE:
Apply the frozen B5 value-column shuffle construction across the four binding values while leaving key, role, and query tokens unchanged.

ROLE_FLIP:
Flip R0<->R1 for all four binding-role tokens while leaving the query role unchanged.
Because both roles exist for each entity, this swaps which value is associated with each queried structural role without removing the entity itself.

SUCCESS
- minimum OOD persistent accuracy >= 0.90
- median OOD persistent accuracy >= 0.95
- maximum reset accuracy <= 0.35
- minimum persistent-reset gap >= 0.50
- minimum value-shuffle degradation >= 0.40
- minimum role-flip degradation >= 0.40
- all five seeds persistent > reset, persistent > value-shuffle, and persistent > role-flip
- persistent state exactly 16 scalars
- learned parameter count exactly 104
- no held-out triple appears in training
- all 32 held-out triples appear in the scored evaluation corpus for every seed
- duplicate complete execution byte-identical

DIAGNOSTICS
Report per seed:
- OOD persistent accuracy
- reset accuracy
- value-shuffle accuracy
- role-flip accuracy
- persistent-reset gap
- value-shuffle degradation
- role-flip degradation
- number of distinct held-out triples scored
- maximum absolute off-diagonal cosine similarity between learned key/role addresses

FAILURE
Any unmet frozen capability gate is a scientific negative.
Do not change the holdout rule, thresholds, training schedule, data sizes, seeds, model dimensions, state budget, parameter budget, or controls after observing results.

INTERPRETATION
A positive B6 would show that the compact persistent relation mechanism supports explicit role-sensitive binding and controlled compositional generalization beyond flat key/value pairs.
A negative B6 would identify role structure as a capability boundary under this frozen compact budget.

BOUNDARY
No shared-baseline promotion from this lane alone.
No learned developmental control authority.
No online adaptation.
No recursive self-modification.
No modification of other Yggdrasil lanes or external runtimes.
