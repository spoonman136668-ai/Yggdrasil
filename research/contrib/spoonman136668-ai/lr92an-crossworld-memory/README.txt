LR-92AN — CROSS-WORLD CAUSAL-OPERATOR MEMORY AND UNSEEN-STRUCTURE TRANSFER
============================================================================

FROZEN OUTCOME: DEVELOPMENT_NO_GO (3/6).
Engineering: local structural fixture PASS; independently authored replay and
audit PASS (324,144 assertions); GitHub original-source / result readback PASS.
Official Yggdrasil native scientific qualification: UNVERIFIED.
No merger, runtime controller, research-loop authority, scientific first-use,
production model, accepted ref or deployment was changed.

CHECKPOINT AND PROSPECTIVE CUSTODY
----------------------------------
Repository: spoonman136668-ai/Yggdrasil
Main baseline: 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9
Predecessor, evidence only: draft PR #1308, head
280980e14ac032d2ea3efb2ed67de53e18102a96

Preregistration committed BEFORE primary:
  1a5c79f5f4e1f29e25784e01ea51b14812e75bd7
Exact executable committed BEFORE primary:
  434eaaacf9551ac6c17c510af55a339621ae4ceb
Decoded runner SHA-256:
  f9a2e6440bf495bc3c4a7404daac733d4b04fc15411759d87f33851253325cee
Fixture-only tests: PASS (2 distinct fixture worlds, seed 73004301).
No evaluated seed used before the GitHub source commit and verified readback.

EXACT PROGRAM AND BUDGET
------------------------
Three seeds: 929207101, 929207102, 929207103.
Per seed: 12 acquisition AND worlds, 6 interfering L1 worlds,
6 interfering L2 worlds, then 20 AND transfer worlds plus 10 XOR
structurally unfamiliar worlds. TOTAL 162 worlds:
72 historic acquisition/interference worlds and 90 evaluation worlds.

Historic worlds have 32 q0 +32 q1 fitting outcomes each.
Evaluation worlds have 12 q0 +12 q1 fitting outcomes and independent
128 q1 and 128 cold q0 validation outcomes each.
Every arm sees identical action/outcome evidence within a world.
No active-intervention advantage was claimed: actions are random and passive.
Bit-flip noise p=.25, three possible action identities (0,1,2).

Historic base functions are six-bit q-by-action truth tables 0..31.
Evaluation base functions are 32..63: structurally disjoint identities.
Transfer AND(prev1=0,prev2=1) was seen during acquisition, followed
by L1 and L2 interference. XOR(prev1=0,prev2=1) is absent from the
predictor's four-operator library: static, L1, L2, AND. Do not describe
this as genuine autonomous invention of a new operator: all usable
operators, including AND, were predeclared. The archive saves four
cross-world posterior family weights, not new neural model weights.

All four Bayesian operator models analytically marginalize the current
world's fresh 64 possible base truth tables. Predictions on new worlds
use the archive of previous-world family posterior votes (with a
fixed 1-count Dirichlet pseudocount per operator). Comparators:
uniform fresh learner, last-12-world recency-only archive,
no-AND fixed operator set, whole-history pooled Bayesian evidence,
true paired-history permutation in both historical and evaluation
fits, fully fitted RF32 per-world, and RF32 fitted on historic + current
training records. RF32 capacity/compute differ from the Bayes arms.

ONE PRIMARY RESULT: 90 EVALUATION WORLDS, NO POST-SCORE TUNING
-------------------------------------------------------------
Family              Archived  Uniform  Recent  No-AND  Pooled Bayes  Sham  RF32 world
AND transfer (60)     65.98%   65.48%   63.23%   60.31%      68.40%   61.48%     57.03%
XOR OOD (30)          51.93%   50.86%   51.17%   50.86%      51.22%   50.18%     52.14%

RF32 pooled historic+current: 43.36% on AND and 50.65% on XOR.
Original primary wall 11.392682 seconds by its internal timer
(13.56 seconds OS process elapsed, approximately 166 MB max RSS).
This is not compute-matched whole-process model training evidence.

Six PRESET qualification criteria:
 C1 archive AND vs fresh uniform:    +0.4948 pp, needed +1.5: FAIL
 C2 archive AND vs recency:          +2.7474 pp, needed +3.0: FAIL
 C3 archive AND vs no-AND:           +5.6641 pp, needed +5.0: PASS
 C4 archive AND vs shuffled history: +4.4922 pp, needed +5.0: FAIL
 C5 all-world cold q0 archive vs
    fresh uniform:                   -0.2431 pp, floor -1.0: PASS
 C6 XOR archive vs best aggregate
    fully-fitted RF32:               -0.2083 pp, floor -3.0: PASS

=> 3/6. Development NO-GO, NOT MIXED, NOT SCIENTIFIC_SUPPORTED.

The strongest overall conventional/model control on AND was
whole-history pooled Bayesian evidence at 68.40%, 2.42 percentage
points BETTER than the proposed archive. This prevents a claim of
superiority even if the archive had passed its weaker preregistration.

Exploratory 95% paired bootstrap intervals (5000 draws, seed
929207901; descriptive only):
 AND archive minus uniform [-0.846,+1.745] percentage points.
 AND archive minus recency [+1.067,+4.414].
 AND archive minus no-AND [+3.997,+7.383].
 AND archive minus history-shuffled [+2.109,+6.940].
Only 34/60 AND transfer worlds were MAP-classified as AND.
On unseen XOR worlds, all models were near chance: the permissive
C6 noninferiority check is NOT a positive unfamiliar-transfer result.

LIMITATIONS
-----------
1. The q0 cold probe does NOT test a hard interference case: in this
   frozen generator the history-dependent operator applies only to
   q1, while q0 has no history effect. C5 PASS is weak.
2. No lifelong learning in Yggdrasil, no tokenless-native architecture,
   no continuously accumulated general-purpose knowledge. The four
   family weights are reused across independently generated worlds
   within each seed; the base table is relearned from scratch.
3. Training historical labels and future fit labels are available to
   all comparators in the disclosed ways, but model capacity and
   whole-process RF compute are not matched. Prediction performance
   alone is not a causal discovery or intelligence result.
4. The OOD XOR family is not representable by the four-operator
   grammar and transfer was NOT demonstrated.
5. The score ledger includes paired heldout correct counts for both
   contexts, not the full 5-column raw action/consequence tapes.
   The exact primary JSON includes recorded SHA-256 of fit and
   validation arrays; original tapes can be regenerated from source
   and seeds and independently checked against those SHA hashes.
6. The complete primary result includes wall-clock timestamps and
   therefore a clean replay will generally NOT reproduce its original
   byte SHA. Strip top-level and per-world 'wall_seconds' to compare
   canonical science data. Exact canonical replay digest SHA-256:
   80784370bd8ce0e5cf584bf507316ee98937193aeeae7d584eecadf16bf11ea9

ACTUAL INDEPENDENT AUDIT
------------------------
Original complete PRIMARY JSON (32,257 bytes, not just a summary):
  primary_result.json.zlib.b64
  decoded SHA-256 446f1499ecbb0f49461b4b55c423820c4578813b447b4dea65b966253f

Independent source:
  audit_readonly.py.zlib.b64
  decoded SHA-256 f93455f8c5b0e9e94bc4aaa9455da1ae7a261563db7390c8c6c91e1577d93520
Receipt:
  audit_receipt.json.zlib.b64
  decoded SHA-256 fcf09813bed7911a77d8522562fa8243f428dcc6541324a10f14c64a42588e3d

The independently coded auditor regenerated ALL 72 historic/90 evaluated
worlds from the frozen seeds, verified exact original fit/validation
array hashes, independently integrated Bayesian likelihoods using
grouped count statistics, refitted RF32 controls and recomputed scores.
It passed 324,144 assertion-level checks with zero score errors outside
21 near-0.5 floating point prediction tie allowances (1e-11 envelope).
These 21 cases are documented as numerical ambiguity, not identical
bit-exact decision replay. No original primary model/data changed.

Compact paired evidence:
  scores.bin.zlib.b64
  decoded SHA-256 7a7338a90530dafac236122ebf49cdcda7bb1b66b8b829c267fd24f1ead7fad9
  Binary format: eight-byte ASCII LR92AN01, then exactly 90 records,
  each '<4B16H': seed index, world number, family (0 AND/1 XOR),
  base truth-table ID, then 8 pairs of correct counts (q0,q1) in
  [archive,uniform,recency,no_AND,pooled_bayes,shuffle,rf_world,rf_pooled].
  Each heldout denominator is 128 labels per context/world.

CLEAN REPRODUCTION
------------------
Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0.
In a NEW throwaway directory, download the four .zlib.b64 artifacts
(run.py, primary_result.json, audit_readonly.py, audit_receipt.json),
and optionally the compact scores ledger.

Decode each (example):
  python -c "import base64,zlib,pathlib;p=pathlib.Path('run.py.zlib.b64');pathlib.Path('run.py').write_bytes(zlib.decompress(base64.b64decode(p.read_bytes())))"

Execute:
  python run.py fixture
  python audit_readonly.py primary_result.json
  # Original read-only audit receipt should match 324144 assertions.
Optional NEW clean scientific replay:
  python run.py primary --output fresh_result.json
  # Discard nondeterministic wall_seconds fields before comparing
  # science score/array-hash contents to the original primary.
Do not run on native owner first-use or promote based on this outcome.

RESEARCH DISPOSITION
--------------------
STOP modifying LR-92AN frozen thresholds or trying additional seeds.
The proposed equal-mass posterior archive is inferior to a stronger
whole-history Bayesian baseline and did not establish OOD transfer.
The next justified independent experiment would introduce genuine
representational induction on unseen operators and difficult cold
interference, with fully matched conventional learning and compute.
No successor has been run in this PR.

No native acceptance, full owner regression, scientific cross-platform
replication, merge, controller change or deployment. KEEP DRAFT.
