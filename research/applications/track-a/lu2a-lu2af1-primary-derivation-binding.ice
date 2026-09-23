TITLE: LU-2A LU2AF1 FIVE-MANIFEST BINDING
DATE: 2026-09-23
STATUS: BOUND / NO PRIMARY ARM EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU2AF1:
d6d9302b114b7ddac6cf43871878be47a1a177a1

PREREGISTRATION:
bdd6bc440635597e1fec64cc1c5124dfc1e0369b

SEED NAMESPACE:
LU2A-PRIMARY|LU2AF1|replicate

REPLICATES:
1..5

BINDING RULE

For replicate k in 1..5:

replicate_key =
SHA256(
  "LU2A-PRIMARY|" +
  LU2AF1 +
  "|" +
  decimal(k)
)

The implementation's deterministic primary-manifest generator
must derive the complete Task-1 world only from:

LU2AF1;

replicate index;

this literal namespace;

and the inherited frozen Task-1 deterministic derivation functions.

No result-dependent selection.

No rejection sampling.

No replacement world.

No primary arm has executed before this binding.

BOUND REPLICATE KEYS

1:
556194c263ea42e7d77035d7742ead992eeef80054473f575dc6e5625e533e7e

2:
d1371e8ab397cef3d033b2ebe89ff565356dbd0eb4fc906af655ed8e28ec019e

3:
449fde103dc7ec8cd22952a3f9abef9258fef23294c30a7fb1402e9371cada4c

4:
b1429f0fc4298cb5315433dfd3c2f118cc29ae6877d357b224404ad2c04dcb70

5:
c90424d2a766cb03163ad57e99afdeb0bc54f10b171f7513e0b285d8f39a5dfe

NOTE

This record binds the derivation function and indices.
The executable LU2AF1 implementation is authoritative
for the full manifest bodies and their SHA256 identities.

Before any primary arm executes:

materialize all five manifests with LU2AF1;

validate each manifest structurally;

record all five manifest SHA256 values in a follow-up binding record;

then execute no scientific arm until that exact five-SHA record exists.

This two-stage binding is intentional because the recovered frozen
implementation is now the sole authority for world materialization.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
