TITLE: TASK-1F T1FF1-R1 FIVE-MANIFEST PRIMARY BINDING
DATE: 2026-09-22
STATUS: BOUND AFTER T1FF1-R1 / BEFORE ANY R1 PRIMARY ARM EXECUTION
TRACK: DG-1 / TASK-1F

T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063

R1 FROZEN SOURCE:
bytes = 18265
sha256 = a3122a9f4f6da6c138cc12944528f5e2e3ef608e904067ef30da7feab7d640f4

PREREGISTRATION:
38bb2970abbe0544754b9d4a48d4cb3aff93db0d

PRE-PRIMARY VALIDATOR REPAIR:
211cfbebb639b836926bf0ba4bfc939528d5ce5d

R1 MECHANICAL GATE:
3a049500200115fd7057ad001aca452a6e0910c7

RETIRED UNEXECUTED BINDING:
7476b025ae6d722316346ef0a7e713a8c5254fde

The retired T1FF1 binding produced no scientific arm execution.
This R1 set is freshly derived from T1FF1-R1.

REPLICATE COUNT:
5

No Task-1F R1 primary arm was executed before this binding.

REPLICATE 1

replicate key:
fa1bdce35a2a32a4257fdb47824146ec204b53b4

seed:
bafb1ffcef4ae94af8e9163ff81b78f4

programs:
61858;
42202;
42226;
41404

manifest SHA256:
83d8b163454aae8f3996e7c0e1c685005525d5499094c6b7bed7946cf2209475

corrupt request ids:
14,22,40,84,96,117,120,175,182,192,194,197,217,246,276,287,306

lesion:
5,13,21,29,37,45,53,61

anchors 0-3:
C_IN 5; C_OUT 11; S_IN 45; S_OUT 39

anchors 4:
C_IN 21; C_OUT 27; S_IN 61; S_OUT 55

REPLICATE 2

replicate key:
5f6cbab62ddf0f0992d5fd193c2fbf3fd45d752a

seed:
2ac9660731ac686d48919cd424f8dc15

programs:
36276;
39142;
30828;
18164

manifest SHA256:
3da4cbaf3b2a928c2af91023c78ee2efede9650491657275d1d3b6fd06754db0

corrupt request ids:
23,67,78,165,166,210,219,238,275,312

lesion:
6,14,22,30,38,46,54,62

anchors 0-3:
C_IN 1; C_OUT 7; S_IN 41; S_OUT 35

anchors 4:
C_IN 17; C_OUT 23; S_IN 57; S_OUT 51

REPLICATE 3

replicate key:
2c7a4c8bd7a7e28c136874379238b689d223f60d

seed:
9524a11ae64bf3d14cf4caf1d4b7c34b

programs:
1895;
33627;
7395;
28914

manifest SHA256:
05852dcb247e9bf412d2bdd41e8f59c36acfb73547148dd2cb1b9cf898e9f1fe

corrupt request ids:
11,14,56,80,97,103,124,127,135,176,209,214,216,225,250,273,276,281,291

lesion:
1,9,17,25,33,41,49,57

anchors 0-3:
C_IN 0; C_OUT 6; S_IN 40; S_OUT 34

anchors 4:
C_IN 16; C_OUT 22; S_IN 56; S_OUT 50

REPLICATE 4

replicate key:
69663a14b6f54feb2e00151acba90d1526a136e4

seed:
fd39c36ce37b557ec46c395f61cb2cac

programs:
14953;
26169;
10907;
13993

manifest SHA256:
65e5e2199a3ea0391d3930ed3e4c08439e0566a3a78926482c73e85967e9379b

corrupt request ids:
11,69,72,126,137,161,162,189,253,264,282

lesion:
0,8,16,24,32,40,48,56

anchors 0-3:
C_IN 7; C_OUT 13; S_IN 47; S_OUT 41

anchors 4:
C_IN 23; C_OUT 29; S_IN 63; S_OUT 57

REPLICATE 5

replicate key:
28c09dbf9bc7838ce41e8bb1c0293fba1a2e92f7

seed:
d8711d43294ab8f2b27ca5ba6b3233c0

programs:
47690;
53874;
53534;
21177

manifest SHA256:
fe96f0234c3f77da0452c51b5297bf78b28111eebf470b1fb91fe20e245d6278

corrupt request ids:
1,25,28,57,71,91,129,194,214,232,263,272,281

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

R1 SERIALIZED FIVE-MANIFEST FILE IDENTITY

bytes:
110472

SHA256:
4b1a8f40d2cb813cc3ca2a215832f1aca9b219aedfd834a5fb81b0b82bf1b6db

BINDING RULE

All five R1 manifests are fixed.

No replicate may be replaced.

No sixth replicate may be added.

No program,
arrival,
corruption,
lesion,
anchor,
H semantic,
task mechanism,
threshold,
or V0 mechanism
may change after R1 primary execution begins.

Two complete five-replicate sweeps
must be byte-identical
before scientific interpretation.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
