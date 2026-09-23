TITLE: TASK-1H T1HF1 FIVE-MANIFEST PRIMARY BINDING
DATE: 2026-09-23
STATUS: BOUND AFTER T1HF1 / BEFORE ANY TASK-1H PRIMARY ARM EXECUTION
TRACK: DG-1 / TASK-1H

T1HF1:
2b57ce116fa9a92a5da55399fbdea3737f9aafe8

FROZEN TASK-1H SOURCE:
bytes = 15363
sha256 = 076e67aef313943fdcd5545ed8c888b6630431638bd158be4e705d81ebebe445

PREREGISTRATION:
1e284a15d0e176cbee09c57a1e219ba6927f05b0

MECHANICAL GATE:
251f7a789b7a12b40d8dda3fa882f217ec268c2e

PARENT TASK-1F T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063

PARENT TASK-1F CLOSURE:
fda86a2fee99fb948524b53b0eb0652011d655f6

SERVICE-ENVELOPE AUDIT:
e6ea693894ab12a6d542d50e297e97abf801124c

REPLICATE COUNT:
5

No Task-1H primary arm was executed before this binding.

DERIVATION

For k = 1..5:

replicate_key =
SHA1("TASK1H-CONFIRM|" + T1HF1 + "|" + k)

task seed =
first 32 hex chars of
SHA256("TASK1H-PRIMARY-SEED|" + T1HF1 + "|" + k)

All programs, arrivals, corruption identities,
lesion positions, and anchors are then generated
by the exact frozen inherited Task-1 generators.

REPLICATE 1

replicate key:
311af451a77c785926d79a5fd50a384137965c0b

seed:
fc094e7faa2b90729dd6adb61f85073f

programs:
60937;
27925;
57405;
33756

manifest SHA256:
68a7f38dc4ac7af861d74e589a5ada3129cbc27fd52dd360eaad5949dfb2fb62

corrupt request ids:
2,40,63,76,101,154,157,165,176,198,207,211,213,225,227

lesion:
2,10,18,26,34,42,50,58

anchors 0-3:
C_IN 2; C_OUT 8; S_IN 42; S_OUT 36

anchors 4:
C_IN 18; C_OUT 24; S_IN 58; S_OUT 52

REPLICATE 2

replicate key:
1c09f3fd73f3e148270185f5e504ddd939b07245

seed:
b2cbba1cf8ae0f97ffff577339e76399

programs:
10459;
53363;
7516;
57660

manifest SHA256:
ca1e9327f731544e3d78e5a9febe3caf4dfac5eb649f423d642cff74223f7b1e

corrupt request ids:
2,19,21,49,57,85,93,103,126,152,159,177,215,249,256,286,313

lesion:
3,11,19,27,35,43,51,59

anchors 0-3:
C_IN 6; C_OUT 12; S_IN 46; S_OUT 40

anchors 4:
C_IN 22; C_OUT 28; S_IN 62; S_OUT 56

REPLICATE 3

replicate key:
7b0a4a8a56c1cba48e1f9f9c909f2dd5501c701a

seed:
d16268e9ab15958da5ad0d3e27594349

programs:
44806;
63824;
9581;
58764

manifest SHA256:
fdcf8a9fb51d42b171a760f94640b907de0c59c820899efe7016a187d9f03dce

corrupt request ids:
14,16,43,48,51,60,114,123,137,147,172,186,198,201,220,256,261,268,270,286,297,310,317

lesion:
0,8,16,24,32,40,48,56

anchors 0-3:
C_IN 5; C_OUT 11; S_IN 45; S_OUT 39

anchors 4:
C_IN 21; C_OUT 27; S_IN 61; S_OUT 55

REPLICATE 4

replicate key:
24fcafb86cefc960a30ef1899818967e07066b7c

seed:
a404b7321e8fe956a8067707367e358f

programs:
39315;
29861;
32448;
37590

manifest SHA256:
c2157e4a7803abc01a5042160834156b332aaac1fb4ba92b85ef78f20d3fb021

corrupt request ids:
3,25,39,74,89,113,120,139,152,167,171,173,174,192,228,234,237,247,267,273

lesion:
6,14,22,30,38,46,54,62

anchors 0-3:
C_IN 6; C_OUT 12; S_IN 46; S_OUT 40

anchors 4:
C_IN 22; C_OUT 28; S_IN 62; S_OUT 56

REPLICATE 5

replicate key:
52f7658c47c770ca4d41bcd161b6bd56bb2989b9

seed:
cb728c11e6609406fb5515271f4933f8

programs:
11407;
27106;
53940;
52269

manifest SHA256:
f85408555abdbee91950ca6c9f76231c0b0c56f97b28f1026b59a712958727a9

corrupt request ids:
3,7,32,43,67,71,102,116,123,130,138,159,215,223,250,267,299

lesion:
4,12,20,28,36,44,52,60

anchors 0-3:
C_IN 7; C_OUT 13; S_IN 47; S_OUT 41

anchors 4:
C_IN 23; C_OUT 29; S_IN 63; S_OUT 57

COMMON CONTRACT

Each replicate contains:

320 arrivals;
64 cells;
160 epochs;
D2;
R_TASK = 2;
six-edge route;
G5_FULL = false;
request-bound handoff;
neutral sensing;
oldest-request-first local deferred matching;
five 32-epoch phases;
+16 anchor rotation.

SERIALIZED FIVE-MANIFEST FILE IDENTITY

bytes:
112131

SHA256:
6db8aabeaa9b0ccc839339f98e52e89abb5ef8fa00b615a37a933afe213e187c

BINDING RULE

All five manifests are fixed.

No replicate may be replaced.

No sixth replicate may be added.

No program, arrival, corruption, lesion, anchor,
H semantic, expiry, service rule, task mechanism,
threshold, D family, G5 status, or V0 mechanism
may change after primary execution begins.

Two complete five-replicate sweeps
must be byte-identical before scientific interpretation.

Repair/service-envelope metrics remain descriptive only
for Task-1H confirmation.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
