TITLE: TASK-1F T1FF1 FIVE-MANIFEST PRIMARY BINDING
DATE: 2026-09-22
STATUS: BOUND AFTER T1FF1 / BEFORE ANY PRIMARY ARM EXECUTION
TRACK: DG-1 / TASK-1F

T1FF1:
f21bdb00fbd585e36068940322f54f2e6a6af02e

FROZEN SOURCE:
bytes = 17800
sha256 = b57ac5d76c6e4e8ceb7dc9ba94aa54bce6ca5207c26739f91e9d1d5d0fb62557

PREREGISTRATION:
38bb2970abbe0544754b9d4a48d4cb3aff93db0d

REPLICATE COUNT:
5

Each replicate is derived deterministically from:

T1FF1;
literal TASK1F-REPLICATE;
replicate index 1..5.

No Task-1F primary arm was executed before this binding.

REPLICATE 1

replicate key:
51fc7eb66921d3827e1f4c70e57e5a1e882f96a6

seed:
7ccf127c6c1c27beadb97f0d86028e5d

programs:
58693;
30028;
38423;
15148

manifest SHA256:
d6b985a879f9acae3a34e87d1d6bce5e37c71295bc4079c4ca26f0d554bd8d85

corrupt request ids:
0,8,24,39,41,59,97,100,128,154,171,182,212,260,265,281,311,316

lesion:
4,12,20,28,36,44,52,60

anchors 0-3:
C_IN 5; C_OUT 11; S_IN 45; S_OUT 39

anchors 4:
C_IN 21; C_OUT 27; S_IN 61; S_OUT 55

REPLICATE 2

replicate key:
ed4a5e09a1888433976db10f26d6f9d55f8558c0

seed:
a76e6fdb0522515d199f89932ba9b692

programs:
15916;
15002;
64006;
40840

manifest SHA256:
3b6afc3820ab5506a2ec82e293886e4f7bf00b9e5c8b93d5efbc3bd651626064

corrupt request ids:
7,19,41,56,65,81,171,178,183,219,261,288,290

lesion:
2,10,18,26,34,42,50,58

anchors 0-3:
C_IN 5; C_OUT 11; S_IN 45; S_OUT 39

anchors 4:
C_IN 21; C_OUT 27; S_IN 61; S_OUT 55

REPLICATE 3

replicate key:
fb5109fff78209eded8a462861af70a2535aa998

seed:
0b41e888516a56a68285968358e0ec0c

programs:
3883;
7958;
21647;
27461

manifest SHA256:
bdede7ab0eac270a62d2fdd293d572d70c8cb7ad05687252237eebb9b1cd02c2

corrupt request ids:
24,25,30,162,176,181,211,217,218,220,221,252,264,279,289,291,303,307,315

lesion:
0,8,16,24,32,40,48,56

anchors 0-3:
C_IN 4; C_OUT 10; S_IN 44; S_OUT 38

anchors 4:
C_IN 20; C_OUT 26; S_IN 60; S_OUT 54

REPLICATE 4

replicate key:
9e9c45683cdfc245ea25a50dbcdb4dc21a7bb948

seed:
b90eb2ea130dd73f2aa2f6f8bc3fdea3

programs:
58005;
34515;
51668;
9958

manifest SHA256:
c0c2b5d775f46231e955ddd0e8d6ce034b8aef1d5188ee8ae3e94e5d4130d733

corrupt request ids:
5,8,25,36,45,75,106,119,129,137,139,210,245,255,256,260,264,285,318

lesion:
3,11,19,27,35,43,51,59

anchors 0-3:
C_IN 6; C_OUT 12; S_IN 46; S_OUT 40

anchors 4:
C_IN 22; C_OUT 28; S_IN 62; S_OUT 56

REPLICATE 5

replicate key:
16463d490a36ae609875305435c3901260ef186d

seed:
bbf2d7891607695beaae516eb61cfc8e

programs:
12510;
54442;
41944;
35644

manifest SHA256:
32f7409af8645e028a39ed4a4cebdef6c18e46538e7e1766b0c163518bc5144a

corrupt request ids:
20,38,90,106,130,144,171,172,176,178,183,186,192,199,273,284

lesion:
1,9,17,25,33,41,49,57

anchors 0-3:
C_IN 2; C_OUT 8; S_IN 42; S_OUT 36

anchors 4:
C_IN 18; C_OUT 24; S_IN 58; S_OUT 52

COMMON CONTRACT

Each manifest contains:

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

The full deterministic manifest array was also produced locally
before any primary execution.

Local serialized five-manifest file identity:

bytes:
110440

SHA256:
38d491590769dca6b99f647218089f37fc6559f55168be2b5adcabac9edad067

BINDING RULE

All five manifests are fixed.

No replicate may be replaced.

No sixth replicate may be added.

No program,
arrival,
corruption,
lesion,
anchor,
threshold,
H semantic,
task mechanism,
or V0 mechanism
may change after primary execution begins.

Two complete five-replicate sweeps
must be byte-identical
before scientific interpretation.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
