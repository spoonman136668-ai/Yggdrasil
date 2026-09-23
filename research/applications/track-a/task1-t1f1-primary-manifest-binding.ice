TITLE: TASK-1 T1F1 PRIMARY MANIFEST BINDING
DATE: 2026-09-22
STATUS: BOUND AFTER T1F1 / BEFORE PRIMARY EXECUTION
TRACK: DG-1 / TASK-1

T1F1:
22b6ab5a036732cc9efbda077069e971c34a337e

FROZEN TASK-1 SOURCE:
bytes = 37394
sha256 = 567c37e3e2171bc3cfc15b996c447e87b7ac5cdafb7bc299ba104284ae826e12

DERIVATION

The exact frozen T1F1 source was reconstructed from its eight
source.chunkNN.b64 parts and verified against the T1F1 loader identity.

The post-freeze primary manifest was derived only by calling the frozen:
primary_manifest(T1F1)
function.

No Task-1 primary arm was executed before this binding.

PRIMARY PROGRAMS

4589
53564
43880
23346

All four are balanced, non-constant, non-affine 16-bit truth tables
under the frozen Task-1 derivation rule.

PRIMARY ARRIVALS

count = 320

The exact per-request arrival sequence is the deterministic output of
the frozen make_arrivals / primary_manifest implementation under T1F1.
Its identity is included in the full manifest hash below.

PRIMARY CORRUPTION SCHEDULE

count = 19

request ids:
30
33
44
68
81
103
107
127
139
147
174
188
190
251
263
278
279
286
302

PRIMARY LESION

cells:
5
13
21
29
37
45
53
61

PRIMARY ANCHORS — PHASES 0-3

C_IN = 3
C_OUT = 9
S_IN = 43
S_OUT = 37

PRIMARY ANCHORS — PHASE 4

C_IN = 19
C_OUT = 25
S_IN = 59
S_OUT = 53

FROZEN MANIFEST PARAMETERS

n = 64
t = 160
d = 2
r_task = 2
route_edges = 6
g5_full = false

PRIMARY MANIFEST SHA256

ef76ca548a1c9754eb2779812d7c14cbe66788821198b5d7c6ebc291360f2d86

BINDING RULE

The primary is valid only if the frozen source regenerates a manifest
whose manifest_sha256 is exactly the value above and whose explicit
programs, corruption schedule, lesion set, anchors, and scalar parameters
match this record.

No program replacement, arrival change, corruption change, lesion change,
anchor change, D-family change, G5_FULL change, task-threshold change,
or qualification change is permitted after this binding.

Duplicate raw primaries must be byte-identical before the frozen
external open(primary1, primary2) gate may calculate scientific
qualification.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
