LR-92AH — OUT-OF-GRAMMAR ACTION-HISTORY CAUSAL LEARNING
=======================================================

Disposition: DEVELOPMENT NO-GO (8/9 frozen checks). This is an independently
executed, external synthetic learning experiment, NOT native Yggdrasil training,
scientific acceptance, general intelligence, research-loop integration or deployment.

Parent: Yggdrasil main 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9.
Research predecessor: draft PR #1281 (original active-EIG feasibility).
Isolated research branch: research/lr92ah-open-causal-family-20261118.

FREEZE, ONE PREPRIMARY INFRASTRUCTURE ABORT, AND CORRECTED PRIMARY
-----------------------------------------------------------------
The original v1 prereg and runner were committed before any evaluation:
  prereg commit 5e23e2f14b5f5656d95a7c6147db896cc40a1294
  source commit a6f6135561ef09c2297adeae3e596d767220ffe2
  source SHA256 f83872b8958bf832eca3d0cb2cf0d98fc7570fe5dfc72dda735e5e93a73605af

The first attempt aborted during the first world's fully fitted RF32 construction:
scikit-learn rejected an out-of-range deterministic random_state. NO primary
result was produced or inspected. Old seeds 929201101-103 were retired.

The source-pinned apply_v2.py script (published BEFORE the corrected primary)
repairs ONLY the seed range and reserves three fresh seeds 929201201-203.
The exact v2 prereg/runner/tests derive byte-for-byte from the v1 archives:
  amendment commit ca2daff1a729025fe90d7b3d933b235df824c6cf
  patch commit f5ade408f96a64d0408d3a04b6ea35d29802a2d5
  corrected runner SHA256 0865118de9caef585c197600acee47a508c4dd2a467cfa5bf920b44f121a991b
  corrected prereg SHA256 8714764208a9db5031c5a389e1f89c838a852af6bb36d6d5251d6dcd4de964ba
  preprimary tests SHA256 bf196738dcd88bd14850b1c75614c7c0ffdd0f1017f6c9f894190420d416eb58
  13/13 fixture-only preprimary tests PASS.

ONE prospective v2 cohort was scored after the amendment was committed.
360 worlds: 120 static, 120 lag1, 120 lag2 (three new independent seeds).
All policies get the same 112 initial + 64 context1 outcomes, 35% flip noise,
and 256 heldout validation observations per world. Counterfactual response
noises are indexed by (step, action), so the selected action alters the true
history-dependent state but the exogenous randomness is controlled.

MODELS AND COMPARATORS
----------------------
Old frozen 256-state posterior + historical q-conditioned DELTA prior.
Candidate: a learned 16-pattern first-order predecessor-action XOR effect,
giving 256x16=4096 latent hypotheses updated online from selected actions.
Unfamiliar lag2: a two-steps-prior effect, OUTSIDE both hypothesis grammars.

Controls: unchanged static EIG, balanced static, balanced lag1, replay lag1
on identical static-EIG experiences, shuffled predecessor histories as
negative control, fully fitted per-world RF32 using all 176 observations
and lag1/lag2 features. RF32 lacks the learner's prior historical DELTA
information: conventional performance is descriptive, not an equal-information
native scientific superiority comparison.

ONE-SHOT RESULTS, EXACT COUNTS
------------------------------
Family (120 worlds)      Static EIG      Lag EIG      RF32      Lag sham
static accuracy           63.4570%      63.0241%     57.8678%   62.7962%
lag1 accuracy             49.2415%      58.2324%     53.5872%   51.6406%
lag2 accuracy             50.6901%      50.7585%     52.9167%   50.9635%

Lag1 gained +9.0 percentage points over static EIG and +6.59 points
over its own shuffled-history negative control. Per-seed correct-count gains
over static EIG: +832, +924, +1006 out of 10240 heldout labels/seed.
Paired postscore bootstrap (2000 draws, seed 929201901), descriptive
95% interval: +7.464% to +10.563% points.

Novelty flags on lag1: 55/120 = 45.833%, below the frozen >=60/120
qualification requirement. Static false novelty flags: 0/120.
Lag2 wrong accepted mechanisms for candidate: 1/120. Lag2 predictions
remain near chance: NO higher-order causal-family transfer demonstrated.
Candidate accepted ZERO fully correct lag1 mechanisms at preregistered
posterior >=90% and fit-misfit p>.01. On static worlds, exact accepted
mechanisms fell to 9 from the original EIG's 21: preserve this loss even
though its prediction accuracy nearly matches the baseline.
Eight of nine checks passed: DEVELOPMENT NO-GO, no postscore tuning.

AUDIT AND CUSTODY
-----------------
Primary result: original raw 12,883,731-byte JSON, SHA256
  0cf91997855d1ad2a1aa67155cf29033dba719ba1d74c680b4a3f12fb494127a
Independent read-only audit: PASS, 452,283 assertions, SHA256 source
  8f558599f75ee4c6742c37b58af2a57cce5bf374add48198fa1d6482dd18d996
Audit receipt raw SHA256
  2fd02291ee2c57ccc425492c8438350f0b5753b38628441ced4a29b296522d62
Auditor recomputes observation/tape causality, posterior and MAP confidence
using both count-based and sequential calculations, and rescores heldout
labels and the fully fitted RF. An initial audit-only predictive 0.5-tie
discrepancy was corrected by verifying independent count-based posterior
within tolerance while using source-consistent sequential floating-point
tie ordering to reproduce an exact binary label. Primary source and result
were unchanged.

GitHub contains prereg/source/parent/test, exact reproducible v2 patch,
result summary, independent audit source, and provenance. Full original
per-observation raw record remains in isolated local custody, hash-pinned,
NOT uploaded to GitHub. The deterministic frozen source and seeds reproduce it;
the compact per-world score ledger is NOT raw observations.

REPRODUCTION (clean throwaway directory)
-----------------------------------------
For each *.zlib.b64 archived Python or JSON source, decode as follows:
  python -c "import base64,zlib,pathlib,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_bytes())))" lr92ah_run.py.zlib.b64

Also decode prereg.json.zlib.b64, test_preprimary.py.zlib.b64,
lr92af_frozen.py.zlib.b64 and apply_v2.py.zlib.b64.
Then, BEFORE any test-primary execution, in the directory holding decoded v1:
  python apply_v2.py .
  python -m unittest -v test_preprimary      # expect 13/13 PASS
  python lr92ah_run.py                       # refuses existing primary_result.json
  sha256sum primary_result.json              # expect 0cf91997855d1ad2a1aa67155cf29033dba719ba1d74c680b4a3f12fb494127a
  python audit_readonly.py                   # expect 452283 checks PASS

The protocol explicitly prohibits a second scored cohort or postresult tuning
for this gate. The above is a clean-room reconstruction recipe, not a request
to rerun on protected/native scientific first-use or owner infrastructure.

G29 atlas: all added contribution artifacts use .txt or .b64 extensions,
which are outside the atlas's pre-existing indexed extension set. The
original source-index integrity check remains intact; an atlas PASS
cannot establish scientific efficacy. Official native owner qualification,
cross-platform model execution, full regression, first-use, integration,
merge and deployment remain UNVERIFIED/HOLD.

Research decision: pursue adaptive intervention with richer family
recognition and higher-order recurrent state discovery under new
prospectively frozen tests; do NOT promote this limited result.
