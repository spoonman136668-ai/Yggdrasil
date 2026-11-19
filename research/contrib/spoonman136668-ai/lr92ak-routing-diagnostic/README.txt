LR-92AK — INDEPENDENT RETROSPECTIVE ROUTING AUDIT OF LR-92AJ
=============================================================

STATUS: ENGINEERING LEDGER AUDIT PASS; SCIENTIFIC EVIDENCE IS EXPLORATORY.
No new training, no new-world scored experiment and no promotion.
This is NOT a confirmatory study and does not revise LR-92AJ's 9/10
DEVELOPMENT NO-GO status.

PARENT CHECKPOINT (read-only evidence)
--------------------------------------
Repo: spoonman136668-ai/Yggdrasil
Main base: 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9
Predecessor: draft PR #1294; exact head
df51f37c2ce819b5cf3f313c3ca91274df2fa20b
Parent G29 atlas CI: run #44446185931 SUCCESS on Linux and Windows.
That run proves indexed-source custody, NOT the original science.

This PR carries a byte-for-byte snapshot of predecessor file:
research/contrib/spoonman136668-ai/lr92aj-family-gated-retention/
paired_ledger.bin.zlib.b64

Git blob SHA-1: 98a42af7fb397ea8762705db1d69f5138ca1361e
Decoded binary length: 5,768 bytes; first 8 bytes ASCII "LR92AJ01".
Decoded SHA-256:
404c35a82958afcb95f52c9ed2ce2b4ab97459774c195b2b2367a5417f1a861b

240 worlds, 3 fixed seed cohorts of 80; each cohort has 27 static,
27 one-step (lag1) and 26 two-step (lag2) worlds. The next 240 records
are 24 bytes each: '<8B8H', consisting of seed index, world ID, true
family, q, base ID, effect mask, trust flag, selected family, then eight
uint16 numbers of correct held-out labels for gate EIG, balanced gate,
shuffled-history gate, ungated mix, fallback-free mix, original lag1 EIG,
original static EIG and fully fitted RF32, in that order.

This analysis recomputed all 24 family-by-arm accuracy numbers from
the published binary, independently of the prior report's aggregates.

FAMILY-SELECTION CONFUSION — OBSERVED, NOT CAUSALLY VERIFIED
----------------------------------------------------------
true family        predicted static  predicted lag1  predicted lag2
static (81 worlds)       77                 4               0
lag1 (81 worlds)         37                34              10
lag2 (78 worlds)         32                 2              44

Lag1 was classified as static in 37/81 worlds (45.68%; descriptive
exact binomial 95% interval approximately 34.56% to 57.13%). Of those,
27 were also marked trusted by the 55% family-confidence gate.

On lag1 worlds ROUTED STATIC, the family-gated EIG policy had:
 -4.234 percentage points accuracy vs frozen prior lag1 EIG.
On lag1 worlds ROUTED LAG1, its difference vs prior lag1 EIG was:
 +1.482 percentage points.

These strata are selected retrospectively from model outcomes. This
conditional association is a plausible causal explanation for retention
loss, not proof that changing the route would reverse the loss.

PAIRED RETROSPECTIVE ACCURACY DIFFERENCES
-----------------------------------------
Family         Gate - old lag1 EIG    Gate - ungated mix EIG
static                 +0.0916 pp              +0.0000 pp
lag1                   -1.2876 pp              +0.6993 pp
lag2                   +5.0130 pp              -0.1202 pp

Descriptive paired WORLD bootstrap (10,000 draws, local seed 929204901):
 - lag1 gate vs old lag1: [-3.0768, +0.4726] pp (crosses zero)
 - lag1 gate vs ungated:  [+0.1013, +1.3455] pp
 - lag2 gate vs old lag1: [+3.5106, +6.5405] pp

Lag1 gate minus prior lag1 by independent seed group:
 -1.7506 pp, -3.3275 pp, +1.2153 pp.
This is NOT a uniformly positive retention finding.

Additional group information:
 - Gate trusted family assignment: 77/81 static, 56/81 lag1,
   and 63/78 lag2 worlds.
 - Lag1 when TRUSTED: gated accuracy -2.009 pp vs prior lag1 EIG;
   when UNTRUSTED: +0.328 pp.
 - Correctness labels in this ledger are per-world aggregates. The
   original old-lag policy chose its own intervention actions. Thus
   gate-vs-old-lag differences do NOT isolate inference routing under
   identical observed evidence. Gate-vs-ungated uses the same candidate
   tape according to the original protocol, but raw tape is unavailable
   for independent reconstruction here.

REPRODUCIBILITY
---------------
The exactly locally executed source is stored as
audit_ledger.py.zlib.b64; decoded SHA-256:
e60094260fb82e5a18b4144eae1c90e728ca1cc475157a3f7e27f765492dbe48

The exact generated JSON result is stored as result.json.zlib.b64;
decoded SHA-256:
4055b6b94860dc7e67642ee90ec12954fe62cb918f6b8a3c7c012e40d3ce6055

Run in an empty read-only analysis directory with Python 3.12+
(standard library only):
  python -c "import base64,zlib,pathlib;[pathlib.Path(p.name.removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_bytes()))) for p in pathlib.Path('.').glob('*.py.zlib.b64')]"
  python audit_ledger.py lr92aj_scored_ledger.zlib.b64
  sha256sum result.json
  # Expected 4055b6b94860dc7e67642ee90ec12954fe62cb918f6b8a3c7c012e40d3ce6055

The script refuses overwriting an existing result.json. Remove a
locally generated result in a *new clean work directory* to rerun.

EVIDENCE AND AUTHORITY BOUNDARIES
---------------------------------
This script verifies the ledger SHA, exact length, record format,
world IDs, seed family counts, score bounds, aggregate accuracies,
route confusion, and paired descriptive resampling.

It does NOT reconstruct the 1,206,291-byte original LR-92AJ raw
observation record (only its SHA was published), reproduce the parent
source's posterior probabilities or original environment action tapes,
or independently re-execute the prior claimed 146,426-check audit.
Previous parent claims remain historical, NOT verified by this
ledger-only audit.

Because this analysis examined already-used outcomes, it is
EXPLORATORY only. No data from those 240 worlds can count as
prospective validation for an improved routing gate.

NEXT FALSIFIABLE TEST (NOT EXECUTED IN THIS PR)
------------------------------------------------
Before observing any fresh outcome, preregister a fixed lag1-memory
preservation policy: compare posterior lag1 vs static causal evidence
on the FIT-ONLY action history. On evidence supporting lag1, keep the
frozen first-order learner active rather than switching to a static
family; retain the lag2 representation on sufficiently diagnostic
two-step action histories.

Require a NEW disjoint world cohort with identical intervention
budgets and matched prior information. Compare:
 (1) exact original LR-92AJ gate (frozen)
 (2) new fixed evidence-based gate
 (3) unchanged first-order EIG (retention control)
 (4) ungated higher-order mixture
 (5) balanced intervention selection
 (6) sham/corrupted predecessor history.
Run negative two-step and static-transfer cases and report ALL
failures. Freeze thresholds, sources, seeds, success criteria and
whole-process compute *before* scoring; do not tune on LR-92AJ worlds.
Prioritize lag1 retention at <=0.5 pp drop from original lag1
while retaining >=3 pp lag2 gain over original lag1, with strong
conventional controls and matched information.

The above is an actionable proposal, not a preregistered primary
evaluation or authorized native Yggdrasil first-use.

No change to accepted refs, controllers, schedulers, native model,
first-use data, main, CI contracts, or deployment. Keep draft.
