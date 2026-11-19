LR-92AM — DISJOINT HISTORY-DESTROYING NEGATIVE CONTROL AND OOD CAUSAL STRUCTURES
================================================================================

Result: 5/5 preregistered DEVELOPMENT feasibility criteria PASS.
Scientific first-use, native Yggdrasil acceptance and model promotion: HOLD.
This is independent synthetic causal-learning evidence, not training the
native Yggdrasil model and not a source-continuous replication of LR-92AL.

PROSPECTIVE CUSTODY
-------------------
Repository: spoonman136668-ai/Yggdrasil
Pinned main parent: 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9
Predecessor: draft research PR #1302 head a0ce5bf75e9ad436844c42f23b58460a02a502bf.

Preregistration commit: 9e924faf279b3f04f3933fac5141ce67cc772d2c.
Frozen complete executable source commit: f135a926e0edfa3ed05d1160e9c76899f43692c8.
Source decoded SHA-256: cc5f4e81ddbeb4f573f5716f31152e1d91d281bea61c0a978f67f515209930a9.
Both were committed and GitHub-readback verified BEFORE the primary.
15 fixture assertions PASS using only seed 12345. Primary seeds
929206101, 929206102, 929206103 were NOT used for fixture development.

Single primary: 180 worlds, 36 per causal family, 3 equal independent
seed groups; 32 initial context0 and 64 context1 fit observations, 256
context1 holdout and 128 post-context1 cold context0 holdout per world.
Outcome flip noise .25; 3 actual action identities (0,1,2). Action 2
acts as a rest anchor with NO lag trigger. All policies get exactly the
same 96 fit observations, counterfactual actions and validation labels.

LEARNERS AND CONTROLS
---------------------
Candidate: exact posterior over 320 hypotheses = 64 binary base functions
on (q,current action) times 5 PREPROGRAMMED temporal mechanisms:
static, previous-action trigger0, previous-action trigger1,
two-actions-ago trigger0, two-actions-ago trigger1.

Same-tape controls: independent first-order posterior, original strongest
family gate (.55 threshold), ungated mixture, and sham posterior trained
with per-context randomly PERMUTED pairs (previous1, previous2) whose
alignment to the SAME current-action/outcome records is destroyed.
Validation uses the UNCORRUPTED true histories. Unlike LR-92AL's binary
flip, this is not a simple relabeling of the two causal masks because
the third/rest identity provides an unchanged anchor.

Conventional control: RandomForestClassifier with 32 fitted trees and
min_samples_leaf=2 on exactly the same 96 fit observations, features
(q,current action,previous1,previous2). This is data-matched but not
capacity- or compute-matched to the Bayesian models.

The true OOD_AND mechanism needs an interaction of previous1=1 AND
previous2=0. The OOD_XOR mechanism uses a parity interaction of two
previous actions. Neither is in the candidate's five temporal types.
All data are original deterministic procedural worlds; no external
licensed material or user data were used.

FROZEN PRIMARY RESULT (q1 accuracy)
-----------------------------------
Family (36 worlds each)     Gate       First-order    Shuffled sham     RF32
Static                      73.6437%    73.6437%       74.1645%        68.8802%
Lag1                        71.5603%    72.2548%       52.4631%        64.0734%
Lag2                        73.6437%    54.0256%       53.0490%        64.5833%
OOD_AND                     67.2526%    67.8928%       68.7174%        66.2652%
OOD_XOR                     53.2661%    52.0833%       49.8915%        57.6606%

Cold context0 after context1 fit, all 180 worlds:
gate 67.0095%; first-order 63.2248%; RF32 60.8941%.

Frozen criteria: 5/5 PASS.
- Lag1 gate >= first-order minus 1.00 pp: observed -0.6944 pp.
- Lag2 gate >= first-order plus 5.00 pp: observed +19.6181 pp.
- Lag2 gate >= shuffled-fit-history control plus 3.00 pp:
  observed +20.5946 pp.
- Cold q0 gate >= first-order minus 1.50 pp: observed +3.7847 pp.
- Pooled OOD_AND+OOD_XOR gate >= RF32 minus 3.00 pp:
  observed approximately -1.704 pp, PASS in aggregate.
  IMPORTANT: the XOR subgroup individually FAILS against RF32 by
  approximately 4.39 percentage points; do not hide this negative.

Primary elapsed: 9.2403 seconds local Linux CPU, not full process cost.
Five-thousand-resample paired bootstrap (seed-stratified, descriptive
not confirmatory) gives lag2 gate-minus-first [+17.458,+21.669] pp,
lag2 gate-minus-sham [+18.175,+22.982] pp.

Family identification confusion, true rows vs inferred
static / lag1 / lag2 columns:
  static: 35 / 1 / 0
  lag1:    1 /34 / 1
  lag2:    0 / 1 /35
  AND:    29 / 5 / 2
  XOR:    12 /15 / 9
Most AND interactions are misidentified as static; XOR assignments
are scattered. This is a failure of unfamiliar structural recognition.

REAL NEGATIVE FINDINGS / LIMITATIONS
------------------------------------
The genuine history shuffle now shows a strong prediction penalty
for in-grammar lag1/lag2 relationships. This supports using correctly
aligned action histories in THIS synthetic setting.

The candidate's gate DOES NOT outperform the predecessor-style
strongest-family gate on the familiar three families. This result is
NOT a new memory-protection advance, native intelligence result,
higher-order causal grammar discovery, or a proven adaptive action
selection benefit: all policies used the same random action tape.

No learner parameters persist ACROSS worlds. "Cold retention" here
means recalling context0 within the SAME world after context1 fitting.
It is not lifelong memory, interference recovery, or cross-world transfer.

The pooled-OOD success criterion masks the important XOR negative.
The frozen result remains 5/5 by its preregistered rule, but cannot
justify scientific promotion. Do not tune the source on these worlds
or reinterpret the subgroup loss as an infrastructure error.

INDEPENDENT AUDIT AND EVIDENCE
------------------------------
Original raw result is 1,111,558 bytes, SHA-256:
8a9d3b5824b7841efe023c239cea048baef42983dace72194f929427dd3fed89
It is preserved in isolated local custody, NOT uploaded to GitHub.

Independent read-only auditor, with no import of the original runner:
regenerated all 180 action/observation tapes from seeds, reconstructed
history resets, independently recomputed grouped Bayesian likelihoods,
refitted RF32, and checked all family-level and cold metrics.
9,581 assertions PASS. There were 1,928 nearly 0.5 individual
prediction ties and 12 world-arm score cells requiring explicit
floating-point tie envelopes; ZERO score disagreements outside them.
This is not a claim of bitwise-identical floating-point prediction.

Auditor source SHA-256:
0c0a42fbbbbf0a3e91fba80411dbdfbdbc8c177bfa23adae065a171cefe22f3f
Original audit receipt SHA-256:
5ae4a4d95779862a1c43556a8d5df1c3f2f0103918c42e2891592c441b84cd93

GitHub includes full frozen runner, prereg, independent audit,
audit receipt, scored result summary, exact provenance, replay verifier,
and a 180-world 6-arm two-context paired ledger:
paired_scores.bin.zlib.b64, decoded SHA-256
2f94e53a7d54073ce09ea2609966ad6bee061e7e69e2790e71259b6bf40bad3c.
Binary format: 8-byte ASCII LR92AM01 then 180 fixed-size
little-endian '<BBBBbH12H' records:
seed_index, true_family, world_id, selected_family, gate_route,
rounded 16-bit family confidence, then six uint16 q1 scores and
six uint16 cold-q0 scores in this order: gate, first,
original_gate, ungated, sham, rf32.
This is paired-score evidence, NOT the full observation tape.

REPRODUCE WITHOUT ACCESS TO THE ORIGINAL RAW FILE
--------------------------------------------------
Use an isolated clean research directory. Download the files in this
PR and decode the two zlib+base64 source files:

  python -c "import base64,zlib,pathlib;p=pathlib.Path('run.py.zlib.b64');pathlib.Path('run.py').write_bytes(zlib.decompress(base64.b64decode(p.read_bytes())))"
  python -c "import base64,zlib,pathlib;p=pathlib.Path('audit.py.zlib.b64');pathlib.Path('audit.py').write_bytes(zlib.decompress(base64.b64decode(p.read_bytes())))"

Install numpy==2.3.5, scipy==1.17.0 and scikit-learn==1.8.0,
Python 3.13.5. Run the fixture first:
  python run.py --fixture
Then IN A NEW EMPTY PATH:
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python run.py --primary --output primary_replay.json
  cp verify_replay.py.txt verify_replay.py
  python verify_replay.py primary_replay.json paired_scores.bin.zlib.b64

Replay verifier checks all 180 paired world-by-arm scores against
the GitHub-pinned SHA-256 ledger. PASS on the actual original result.
The original independent audit script checks the ORIGINAL raw result
SHA and cannot be run unchanged on a new primary replay, because the
one-shot result contains nondeterministic elapsed_seconds metadata.
A new reproduction should compare paired scientific results using
verify_replay.py rather than claim byte-identical original raw hashes.

AUTHORITY / QUALIFICATION
-------------------------
This is external research only. No native Yggdrasil source/model,
training loop, accepted refs, controller/queue/runner, owner scientific
first-use, merge or deployment were changed. Full native regression,
cross-platform scientific replication and stronger matched-parameter,
matched-compute training controls remain UNVERIFIED.

Keep the PR DRAFT. The highest-value successor is evidence-gated causal
grammar expansion tested on genuinely new XOR/AND structures and
cold CROSS-WORLD retention, not threshold retuning on this consumed cohort.
