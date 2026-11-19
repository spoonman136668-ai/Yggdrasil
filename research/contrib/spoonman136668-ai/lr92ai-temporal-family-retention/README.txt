LR-92AI — HIGHER-ORDER CAUSAL FAMILY MEMORY AND RETENTION
==========================================================

DISPOSITION: EXTERNAL DEVELOPMENT NO-GO (7/10 frozen criteria PASS).
This is NOT native Yggdrasil training, official scientific qualification,
accepted-model integration, controller execution, protected first-use or deployment.

CHECKPOINT / IMMUTABILITY
-------------------------
Repository: spoonman136668-ai/Yggdrasil
Pinned main: 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9
Predecessor: LR-92AH draft PR #1287, head
4dffd431bab41c1ae4c7b6088a4f720cf14ff439 (G29 PASS both OS).

This experiment's preregistration was committed FIRST:
  commit 1abb8b0b10b879cecab5442ccc2267d53b2a8c05
  decoded prereg SHA256 792c7fc313e414a14119a18538991e6cffb77e2a889633f59b022e6bdbeff0e2
Exact runnable source was committed BEFORE primary scoring:
  commit 5517a999ab748c220cc30be39c1b53f36a49c892
  decoded runner SHA256 c5c94cee0f10da3f4d713047f271436027d44f32f87ef6fcfe99e6303273d46e

Also committed before scoring: 12 fixture-only pre-primary tests (12/12 PASS)
and exact unchanged frozen LR-92AH/LR-92AF source, with GitHub readback
verifying byte-identical blobs. No primary seeds were used in fixture tests.

PURPOSE AND DESIGN
------------------
LR-92AH learned first-order action consequences but failed unfamiliar two-step
transfer. LR-92AI adds a *predefined* mixture of three causal families:
  STATIC: 1 no-effect mask
  LAG1: 15 nonzero previous-action effect masks
  LAG2: 15 nonzero second-previous-action effect masks
together with 256 frozen base causal truth tables = 7,936 joint states.

This enlarges a programmed grammar; it is NOT autonomous discovery of
arbitrary causal families. All Bayesian methods preserve the frozen historical
context prior DELTA, and update their causal state from observed consequences.
Mixture family prior: static .65 / lag1 .175 / lag2 .175.

Primary data: exactly 240 new procedural worlds, seeds 929202101,929202102,
929202103; 81 static, 81 lag1, 78 lag2. 112 initial/context0 outcomes, 64
context1 interventions and 256 heldout outcomes/world; Bernoulli noise .35.
Candidate uses greedy predictive-entropy interventions and deterministic
tie breaking. A balanced intervention policy uses the SAME model, prior,
observations budget and world-generating distribution. Sham history control
receives EXACTLY the candidate actions/outcomes but independently permutes
both predecessor-action histories during posterior inference.

Other controls: unchanged first-order EIG, unchanged static EIG, fully fitted
RF32 with lag1+lag2 features. RF32 receives the same 176 fitted outcomes as the
candidate but NOT the historical DELTA prior. The RF comparison is therefore
descriptive rather than equal-historical-information scientific proof.

FIXED ONE-SHOT RESULT
---------------------
All accuracies are held-out, by family; denominators are worlds x 256 labels.

                     MIX EIG   BALANCED MIX   PARENT LAG1   STATIC EIG   RF32
Static  (81 worlds)   63.10%       62.15%        62.84%       63.48%     58.00%
Lag1    (81 worlds)   56.35%       55.84%        57.63%       50.13%     52.45%
Lag2    (78 worlds)   56.83%       56.75%        51.02%       50.42%     54.79%

Lag2 candidate minus original lag1: +5.8143 percentage points.
Descriptive postscore paired world-bootstrap CI (10,000 draws, frozen summary
seed 929202901): [+4.23,+7.48] points; gain positive all 3 evaluation seeds
in raw label counts (+385,+275,+501). The aligned-history negative control
obtained 52.14%, i.e. a +4.69-point difference favoring actual causal history.

BUT the SAME enlarged model with balanced interventions yielded 56.75%;
adaptive EIG advantage was just +0.0801 points (descriptive CI spans zero).
No adaptive action-selection superiority was established in this new model.

Three FAILED preset checks (7/10 PASS overall):
  - Lag1 prediction retention: 56.35% vs parent 57.63%, a loss 1.28 points,
    beyond the frozen maximum loss of 1.0 point.
  - Gain vs balanced at lag2: +0.08 points, below required +0.5 points.
  - Lag2 exact family MAP: 30/78 = 38.46%, below required 40%.
The other seven checks, including lag2 gain over parent/sham, static accuracy
retention, budget parity, cold prior, and bounded false accepts passed.

IMPORTANT NEGATIVES:
  - Zero fully correct lag2 mechanisms were ACCEPTED at fixed posterior >=90%
    and fit-only binomial survival p >.01. Lag1 also had zero accepted exact
    mechanisms.
  - On static worlds, accepted exact mechanisms dropped from 18/81 (old
    static EIG) to 8/81 (new mix EIG), despite passing prediction retention.
  - The gate therefore does not establish cumulative causal memory or
    reliable novel mechanism identification.
  - Lag2 mix EIG had 0 false accepted; old lag1 had 3, but this sparse count
    is not a general safety guarantee.

ENGINEERING AND REPLAY
----------------------
12/12 fixture-only pre-primary tests: PASS.
Independent read-only original observation audit: PASS, 152,753 assertions,
240 worlds, 1,440 arm-family evaluations (six arms x 240 worlds).
It recomputes observations from selected action-specific potential outcomes,
both causal predecessor histories, likelihoods, posterior families and
decisions, held-out labels, parent baselines, RF32 fits and aggregate scores.

Auditor initially flagged a numerical near-tie: grouped sufficient-statistic
summation chose a different but almost-equal MAP mask from the source's
chronological floating accumulation. The AUDITOR ONLY was corrected to
check both forms agree within 1e-10 and use chronological ordering to
reproduce exact tie decisions. The frozen PRIMARY SOURCE/RESULT never changed.

Primary raw original: 7,314,686 bytes, SHA256
  2acff6eef4b69ace3d4c0620cc10de05e29513449baaafbe8e87132330e2200c
Raw complete observation record remains in local isolated custody, NOT
uploaded in this GitHub contribution. It is reproducible from pinned source,
seeds, dependencies and protocol. Do NOT mistake the compact scored ledger
for raw observation-level data. GitHub DOES include exact source, prereg,
tests, both unchanged parents, independent auditor, audit receipt, aggregate
results and all 240 world-by-six-arm paired decision/score records.

Runner script wall time: 19.240 seconds on local Python 3.13.5, NumPy 2.3.5,
SciPy 1.17.0 and scikit-learn 1.8.0. This is NOT matched whole-process
Yggdrasil speed evidence.

HOW TO REPRODUCE, CLEAN THROWAWAY DIRECTORY
-------------------------------------------
Download the nine *.zlib.b64 artifacts (runner, protocol, test, auditor,
result summary, ledger, audit receipt, and both frozen parent sources)
from this research folder.
Decode each archive with the same command (examples below):

  python -c "import pathlib,zlib,base64,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_bytes())))" prereg.json.zlib.b64
  python -c "import pathlib,zlib,base64,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_bytes())))" lr92ai_run.py.zlib.b64

Decode test_preprimary.py, audit_readonly.py, lr92ah_frozen.py,
lr92af_frozen.py identically before testing.

  python -m pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0
  python -m unittest -v test_preprimary
  python lr92ai_run.py                       # one shot; refuses overwrite
  sha256sum primary_result.json              # expect 2acff6ee...e2200c
  python audit_readonly.py                   # expect 152753 checks PASS

Never run the scored script against protected native source or first-use.
No second scored cohort, postscore model change, or acceptance threshold
relaxation is part of this gate. A clean independent reproduction in a
separate directory is allowed, but is NOT claimed as performed here.

G29 source atlas indexes .py/.json/.md but not .b64/.txt paths, so all
new GitHub artifacts use .b64/.txt and do not alter G29 contracts or native
model files. G29 PASS is not native scientific qualification; full Yggdrasil
regression, cross-platform science and owner acceptance are UNVERIFIED.
Keep this PR in DRAFT and unmerged.

NEXT RESEARCH QUESTION
----------------------
Test a prospectively frozen *family-selective* gate that restores static
and lag1 inference when higher-order evidence is weak, without trading away
lag2 prediction. Require matched budget, actual cold retention, and one-shot
independent evaluation; no retroactive alteration of the LR-92AI NO-GO.
