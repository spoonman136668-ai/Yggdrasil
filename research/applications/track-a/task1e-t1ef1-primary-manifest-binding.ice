TITLE: TASK-1E T1EF1 PRIMARY MANIFEST BINDING
DATE: 2026-09-22
STATUS: BOUND AFTER T1EF1 / BEFORE PRIMARY EXECUTION
TRACK: DG-1 / TASK-1E

T1EF1:
04872029aeb773b3e98ccb71537c18ff965487e1

FROZEN TASK-1E SOURCE:
bytes = 15476
sha256 = c1578a0d21d1125a26d81664adc0c3a78a3a23e9a4a2a4865d526e41af7d2207

PARENT T1BF1:
83af31c2a95adeba47700f7c34d159d7739549c9

PREREGISTRATION:
5b77a388267479f7bdb2bb005df1ea7c245b436e

HANDOFF DIAGNOSIS:
d3c42b834e684a7716c3c87f4c9b36d02c9c82c6

DERIVATION

The exact frozen T1EF1 source derived this manifest
using only primary_manifest(T1EF1).

No Task-1E primary arm was executed before this binding.

PRIMARY SEED

c7ee4a3e9aa376e6fdad9119ae128919

PRIMARY PROGRAMS

26057
37786
34614
58028

All four satisfy the frozen balanced,
nonconstant,
non-affine truth-table rule.

PRIMARY ARRIVALS

count = 320

PRIMARY CORRUPTION SCHEDULE

count = 19

request ids:

16
50
53
73
95
103
136
158
159
175
176
188
210
239
266
281
282
311
318

PRIMARY LESION

cells:

3
11
19
27
35
43
51
59

PRIMARY ANCHORS — PHASES 0-3

C_IN = 2
C_OUT = 8
S_IN = 42
S_OUT = 36

PRIMARY ANCHORS — PHASE 4

C_IN = 18
C_OUT = 24
S_IN = 58
S_OUT = 52

FROZEN MANIFEST PARAMETERS

n = 64
t = 160
d = 2
r_task = 2
route_edges = 6
g5_full = false

PRIMARY MANIFEST SHA256

b759aca22f379bffa887ea820cb476a9f8a9da15bf58c78cb3f7b52455edccda

BINDING RULE

The primary is valid only if T1EF1 regenerates
this exact manifest identity and all explicit fields above.

No change is permitted after this binding to:

request-bound handoff semantics;
programs;
arrivals;
corruption;
lesion;
anchors;
D family;
G5 status;
scheduler;
R_TASK;
expiry;
phase lengths;
or qualification.

Two complete raw primary sweeps
must be byte-identical
before scientific opening.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
