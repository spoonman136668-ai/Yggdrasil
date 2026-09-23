TITLE: TASK-1G T1GF1 FIVE-MANIFEST PRIMARY BINDING
DATE: 2026-09-23
STATUS: BOUND AFTER T1GF1 / BEFORE ANY PRIMARY ARM EXECUTION
TRACK: DG-1 / TASK-1G

T1GF1:
ec41d76f5e80005e6b65db651753b04ec3f9d8cf

FROZEN SOURCE:
bytes = 15987
sha256 = dc46ac0cc462f5f3ff93c56c28db4ed7da92ce67654d1633b4d3014e9ae01197

PREREGISTRATION:
2b1988f0d891d1e24de28ad32b8a32a3d6c0e29a

MECHANICAL GATE:
6c98e16f72c695ef08668ad86cf56281e424fba1

PARENT TASK-1F T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063

PARENT TASK-1F CLOSURE:
fda86a2fee99fb948524b53b0eb0652011d655f6

REPLICATE COUNT:
5

No Task-1G primary arm was executed before this binding.

REPLICATE 1

replicate key:
f2e11cf492f0f1fc415dfcb3b155c296cd42bef6

seed:
79fce0ca900b343a729b9b908c7c0d0d

programs:
61734;
34398;
42294;
14769

manifest SHA256:
1cb66e836c4311eb840cc6d7574aefb876d0e7c37869b65157a83ef784099d09

corrupt request ids:
0,139,168,213,217,222,239,243,258,283,295,302,309

lesion:
6,14,22,30,38,46,54,62

anchors 0-3:
C_IN 7; C_OUT 13; S_IN 47; S_OUT 41

anchors 4:
C_IN 23; C_OUT 29; S_IN 63; S_OUT 57

REPLICATE 2

replicate key:
969ee52018444a6a64c86d732b003c640c9e6e43

seed:
6a95729607408200ba8ae66a83221884

programs:
42412;
25068;
955;
45171

manifest SHA256:
3ab5adc367fe24c112d1055393077f540d070104ba8f5e67558f60d7f893acfc

corrupt request ids:
37,51,52,118,139,153,161,176,221,224,252,267,275,280

lesion:
3,11,19,27,35,43,51,59

anchors 0-3:
C_IN 7; C_OUT 13; S_IN 47; S_OUT 41

anchors 4:
C_IN 23; C_OUT 29; S_IN 63; S_OUT 57

REPLICATE 3

replicate key:
a3fa4cfe00d053331f7bb01391ffbb0f9495d1ab

seed:
c2edae41233dcabca7ee3836178ab4ea

programs:
4511;
10119;
23189;
7794

manifest SHA256:
493bf2a47cebe50ac9ebd54d9cfbcde2fcd24c0037da1d3548f570ccb9002d0f

corrupt request ids:
17,21,26,60,61,89,112,120,121,162,175,217,238,254,279,297,307

lesion:
6,14,22,30,38,46,54,62

anchors 0-3:
C_IN 0; C_OUT 6; S_IN 40; S_OUT 34

anchors 4:
C_IN 16; C_OUT 22; S_IN 56; S_OUT 50

REPLICATE 4

replicate key:
db43d33b402e92df8774d05a9311205a3a1f8f4d

seed:
b3a90962a4c57efeb155038a5e66f46b

programs:
18991;
62534;
30948;
28766

manifest SHA256:
b72e767d556220339b71ff256aabc00745d315864f33bcf52edde9dd9733cba7

corrupt request ids:
15,26,40,58,76,84,97,110,124,125,158,159,163,164,176,213,222,234,236,246,255,259,288,293

lesion:
3,11,19,27,35,43,51,59

anchors 0-3:
C_IN 0; C_OUT 6; S_IN 40; S_OUT 34

anchors 4:
C_IN 16; C_OUT 22; S_IN 56; S_OUT 50

REPLICATE 5

replicate key:
9f101caa304fe5ee1c89df45819f3b6ad32390a2

seed:
7adc92487fd026770d7907e95b9d7972

programs:
59139;
11109;
58964;
51907

manifest SHA256:
d17af6ff367c2626420bec0e1ff3ce363d2fa50d160e795e62c736dfcf8f1a8a

corrupt request ids:
1,3,59,77,99,103,118,121,157,186,188,190,220,235,238,281,292,299

lesion:
3,11,19,27,35,43,51,59

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
LOCAL_HEDGE unchanged;
request-bound handoff;
neutral sensing;
32-epoch expiry;
mandatory post-repair verification;
five 32-epoch phases;
+16 anchor rotation.

TASK-1G treatment changes only
local proposal ordering for
already-detected repair-critical work.

SERIALIZED FIVE-MANIFEST FILE IDENTITY

bytes:
111576

SHA256:
17577c5dca1802f23533876fd5f3dcaa4878ebaafd8caef10878e313c6afadbf

BINDING RULE

All five manifests are fixed.

No replicate may be replaced.

No sixth replicate may be added.

No program,
arrival,
corruption,
lesion,
anchor,
deadline,
expiry,
repair rule,
verification rule,
LOCAL_HEDGE equation,
scheduler rule outside the repair critical path,
threshold,
or V0 mechanism
may change after primary execution begins.

Two complete five-replicate sweeps
must be byte-identical
before scientific interpretation.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
