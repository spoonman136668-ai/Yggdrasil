LR-92AO — OPT-IN NATIVE-FACING TEMPORAL CAUSAL MEMORY DEVELOPMENT GATE
======================================================================

DECISION: FROZEN DEVELOPMENT_SUPPORTED (6/6), NOT SCIENTIFIC_PASS.
The component is an opt-in research source candidate, not installed in
Yggdrasil's accepted/native package. No model first-use, merge or deployment.

VERIFIED CHECKPOINT
-------------------
Repo spoonman136668-ai/Yggdrasil, exact base main
5e74f8db85b2f5839c42148c0dfba69a88b1a2c9.
Prior frozen external research: LR-92AN draft PR #1310,
961e717ae1fee1d16a4e2269f1ff487d4defbb36 (3/6 NO-GO).

Preregistration was committed before primary evaluation:
2ad2fbb87e2669a65079f5f2b2763073c0d81cac.
Exact opt-in source commit BEFORE scoring:
ad7d8a06fdd2ac99bc2d16d1b827e1ff70c7040e.
Decoded source SHA256:
7c73ae6d867780fc9e1119d1520f1fbf6ca86d61a289add710664fa5be930428.
8/8 fixture unit tests PASS; separate 4-world fixture seed 73004302 PASS.
Exact tests and evaluator were also committed before any primary scoring.
All archives had GitHub blob SHA-1 readback verified.

WHAT WAS ACTUALLY IMPLEMENTED
-----------------------------
PublicTemporalCausalCells is a small, tokenless public-action memory
candidate following existing PublicCausalCells' fixed address split:
7 active and 9 retained memory addresses, with 2 current actions
and explicit boundary/rest action 2 in previous-action slots.

Only 7 predecessor-history pairs are possible after correctly resetting
episode chronology: (2,2), (0,2), (1,2), (0,0), (0,1), (1,0), (1,1).
The first development version incorrectly required all 9 predecessor
pairs, including impossible (2,0)/(2,1), and was corrected BEFORE the
primary freeze. Impossible histories are now rejected. The final
candidate uses exactly 14 (current action, predecessor pair) patterns.

Unlike the previous external four-operator families, the native-facing
candidate does not have hardcoded AND/XOR learner labels. It can infer
any observed 14-bit Boolean conditional pattern when all 14 cells
have adequate non-tied observed evidence. This is a bounded look-up
representation, NOT autonomous causal structure discovery.

Streaming observe_step updates actual two-step action chronology only
after a public outcome; end_episode resets history without clearing
learned counters. Independent retained addresses survive unrelated
active-address observations. No counterfactual or hidden observation
oracle exists. Invalid observation types and impossible histories
cannot mutate state. End-to-end checkpoint restore checks SHA256
integrity and episode-history consistency.

Resource cost: 896 uint16 counter bytes + 32 action-history bytes =
928 learned/chronology bytes. Frozen YPT3 checkpoint is 964 bytes.
Existing PublicCausalCells code, 164-byte legacy checkpoint,
accepted model refs and live controllers were not changed.
The earlier pre-correction 1,184-byte estimate DOES NOT apply to the
final candidate.

FROZEN TEST DESIGN
------------------
One valid scored primary; three seeds 929208101/102/103, 12 worlds
each for XOR, AND, static and fully generated random 14-bit relations
(144 worlds). Each receives 45 public training episodes ×8 steps =
360 actual observed training labels. Each has 35 completely separate
evaluation episodes ×8 steps = 280 heldout outcomes. Total 51,840
training labels and 40,320 heldout labels. Binary outcome flip .15.
All learning algorithms observe the same actions, histories and labels.

Controls:
  temporal: the proposed PublicTemporalCausalCells (read by exact
    Laplace-smoothed posterior outcome rates).
  tabular14: conventional full 14-bin conditional frequency lookup,
    same observations and Laplace smoothing, exactly equivalent.
  action_only: Laplace-smoothed action/outcome counts ignoring temporal
    history. This mimics PublicCausalCells' observation-counting baseline
    but does NOT execute its distinct choose() action selection method.
  history_shuffle: valid training history pairs randomized independently
    of actions/outcomes while heldout uses real predecessor histories.
  rf32: FULLY FITTED 32-tree sklearn random forest on action, prev1,
    prev2; same 360 training observations, same 280 heldout outcomes.

ONE-SHOT PRIMARY RESULT
-----------------------
Family (36 worlds)   Temporal  Tabular14  Action-only  Shuffled  RF32
XOR                   85.347%   85.347%      53.571%    53.492%  85.308%
AND                   84.742%   84.742%      71.925%    71.438%  84.742%
Static                85.526%   85.526%      85.526%    85.526%  85.526%
Random table          84.742%   84.742%      62.044%    61.627%  84.742%

C1 pooled XOR+AND vs action-only: +22.297pp >=5.0 PASS
C2 pooled XOR+AND vs shuffled:   +22.579pp >=5.0 PASS
C3 exact parity with conventional tabular on all 144 worlds: PASS
C4 random-table vs fully trained RF32: 0.000pp >=-2.0 PASS
C5 cold retained address after unrelated active-address training:
   144/144 state/readout comparisons PASS
C6 static vs action-only baseline: 0.000pp >=-3.0 PASS

Classification = DEVELOPMENT_SUPPORTED under its precommitted six
DEV criteria; DOES NOT support a scientific novelty superiority claim.
A fully trained conventional 14-state frequency table has EXACTLY
the same results. On random-world and AND cases, RF32 also matches it.
This is a capability-gap demonstration relative to action-only memory,
not a new approach outperforming conventional temporal learning.

Raw original primary: 55,446 bytes, SHA256
37bfecab480a50e5e6ddb48010965bc52ac3783c483b0159a21aba9c45d20686
The original full JSON remains in isolated local custody. It is NOT
uploaded to this GitHub PR. This PR publishes the complete paired
144-world five-arm score ledger and the original hash.
Scores ledger decoded: 2,312 bytes; SHA256
f88bfda8272e415758d3e5860fbb71a49cd015684021990c135e5c17cf588ba3.
Format 8-byte ASCII LR92AO01 followed by 144 16-byte records, packed
as <BBBH5HB: seed index, family index, world ID, 14-bit mask,
5x uint16 correct heldout counts, and 1 cold-retention flag.
Each score has fixed denominator 280.

Because the full raw JSON includes nondeterministic wall_seconds,
clean independent replay verifies the canonical JSON after removing
the top-level wall_seconds. Canonical science SHA256:
06356e417b3fbdf1257ac32d421baeb87940f5ea9e154dacf6af266f51b4cc10
All 144 train/evaluation tape SHA256s are inside the original JSON,
which is reproducible from the published source/seeds.

INDEPENDENT AUDIT
-----------------
Separate read-only implementation regenerated all 144 worlds from
the frozen seeds, checked each original input/heldout digest,
recounted outcomes, replayed candidate/14-bin and action-only choices,
independently randomized the history sham and refitted all 144 RF32s.
255,044 assertions PASS, with exact match to each of 144 x 5 heldout
scores, no numerical tolerance required.

The independent auditor verifies both the original byte SHA256 and
canonical science digest; time-only differences leave the canonical
hash unchanged. A deliberately altered scientific score is rejected.
Original auditor had only the raw checksum; its postscore
engineering-only amendment added canonical replay checking without
changing any primary model/seed/result. Original source and receipt
versions remain in Git commit history.

Updated audit source SHA256:
efafda83638c40d44d4bb2a4d88e20035caaf83e71ec1f0fbd31bd11d9efe3a6
Audit receipt SHA256:
8f2b417fbeaa274b3368c0c65e66a35432c8b1d0a37a55a1de4b6bd85131f603

REPRODUCTION IN A THROWAWAY DIRECTORY
-------------------------------------
Python 3.13.5, numpy 2.3.5, scikit-learn 1.8.0, pytest 9.0.2.
Download the .zlib.b64 files:
public_temporal_causal_cells.py.zlib.b64,
test_public_temporal_causal_cells.py.zlib.b64,
eval.py.zlib.b64, audit_readonly.py.zlib.b64.

For each compressed file, zlib-decode after Base64, writing the
original .py file. Put public_temporal_causal_cells.py under
new isolated directory yggdrasil/, test_* under tests/ and eval.py,
audit_readonly.py at the isolated directory root. No live repo edits.

From isolated root:
  PYTHONPATH=. python -m unittest discover -s tests -p 'test_public_temporal_causal_cells.py' -v
  PYTHONPATH=. python eval.py fixture
  PYTHONPATH=. python eval.py primary --output primary_result.json
  PYTHONPATH=. python audit_readonly.py primary_result.json
  # Expect 144 matched records and canonical science SHA above.

The first invocation in a clean directory is a deterministic replay of
ALREADY-CONSUMED development worlds, NOT permission to use new scientific
first-use cases or tune thresholds.

BOUNDARIES AND NEXT ACTION
--------------------------
No existing native Yggdrasil module was changed in this PR. Its code is
a reproducible proposed native component; simply naming its Python class
does not make it accepted model capability. Existing 164-byte snapshots
are not modified or silently migrated.

Native full regression, Windows execution of the new component,
trusted causal intervention assignments, hard same-address interference
repair, distributed lifelong transfer across worlds, whole-process
compute-matched claims and official scientific first-use are UNVERIFIED.
Causal inference from observation counts can be confounded if action
assignment was not controlled. No general intelligence claim.

For native engineering qualification, copy the source and focused tests
into an isolated native Yggdrasil implementation branch, regenerate the
pinned source atlas via the native OWNER-APPROVED route, run full
regression on the exact SHA and required OS, and separately authorize
scientific acceptance. Do not weaken G29 or mutate accepted refs.
This research-only PR remains DRAFT / UNMERGED / DEPLOYMENT HOLD.
