# CKAD25-SRL01 optimization gate — exact integer parity, source-free CPU

**Decision: focused engineering PASS / local fit-and-select CPU improvement measured / authentic native full regression UNVERIFIED / scientific improvement NOT proven / deployment NONE.** This is an engineering-only optimization of the existing isolated opt-in SRL01 shared-risk component; it neither adds a learner nor alters accepted `main`, the Amalgam coordinator #1278, retention #1329, native checkpoint format, source-owner permissions or consumed scientific trial.

## Pinned source and exact patch

- Original frozen source-free SRL01 branch head `2da3f907b2a622b5af801d75a8b2ed46f14f1d3e`, native shared-risk component Git blob **`6b9811f4c61ef6fba67ba9685ca14bd14d0c5f1d`**.
- Optimized code-only commit **`a37358d467c3ffa7e2a8b3e40a7236c2ed72c049`**, tree **`fe0fe054c45fcb9ae304be76d5255f02943c5833`**. Changes only `yggdrasil/native_shared_fault_risk.py` (Git blob **`f5f98069b74a984906295256e61c6b1b97bc6b7c`**) and `research/contrib/chatgpt/CKAD25-SRL01/test_exact_optimization.py` (Git blob **`6311e65bd623b3d67edd6187ee8017abf810b7ac`**). Full source bytes matched locally tested bytes.
- Original opt-in `NativeCumulativeLearner.propose_shared_source_change_witnesses` adapter was **not** changed or executed on an authenticated native checkpoint. No source admission, owner workstation or runner operation was invoked.
- Optimization is strictly exact algebra: all four provided q-grid values have a common integer likelihood denominator of 60; three historical worlds yield integer likelihood products, risks are exact integer numerators over one common denominator, `select` sorts those numerators, and fractional evidence/posterior/probabilities are lazily materialized only upon read. The bounded source-independent 18-event likelihood table (six address pairs × three source-visible outcomes) is compiled from the **unchanged conventional finite hypothesis class**. It contains no source data, hidden labels, model weights, training samples or cross-source memoization.

## Exhaustive correctness qualification

**Local Python 3.13.5 Linux: 15/15 focused source-only tests PASS** (8 original SRL01 +7 new). The new independent conventional `Fraction` reconstruction checks **all 18³ = 5,832 allowed three-world public two-probe witness sequences**, **exact identity** of full posterior, evidence likelihood, four-address risks and two selected actions. Tests also check 72 previously consumed public source histories and independently relabeled action identities; invalid/duplicate/bool public witnesses are rejected and original source inputs remain unmodified.

Separately, the prior original source-free trial result was verified locally against its immutable stdout SHA256 `e15d86a168d3a788c6a7d9e9adbcac3d46db75da7075cae4f61715280aa04b5f`. The optimized source matched **all 72 original archived public-history forecasts and action choices exactly**. **Custody caveat:** the original 299,869-byte stdout is *not available as a committed GitHub archive*; only its original hash, frozen deterministic scorer and source summary are in Git. The original training/evaluator target labels were never re-admitted to the model. No new science trial, first-use or adaptive retuning of the consumed cohorts occurred.

## Measured CPU, same public inputs

The [read-only pinned-blob selection CPU profile](profile_exact_selection.py) (Git blob `809039aeb7702d725403ecfccba80eb218f0ecaf`) compares **full fit + selected two-action choice**, not just fitting. All methods use the same 72 previously consumed *public training histories*, 80 repetitions each (=**5,760 fit+select calls per arm per round**), 3 CPU `process_time` rounds per run, and two separate runs. Predecessor Fraction source is fetched via read-only pinned `git show` or a blob-checked local path, never an unpinned model.

| CPU median for 5,760 fit+select calls | Run A | Run B |
|---|---:|---:|
| Previous exact-Fraction shared model | 3.495287 s | 3.032055 s |
| **Optimized exact-integer shared model** | **0.091635 s** | **0.088267 s** |
| Existing independent empirical Beta | 0.052234 s | 0.058264 s |
| **Exact shared optimization vs original** | **38.14× faster** | **34.35× faster** |
| Optimized CPU ratio to Beta | **1.754×** | **1.515×** |

All six raw CPU times per arm/run and both sha256-identified stdout receipts are recorded in [`optimization-qualification.json`](optimization-qualification.json), Git blob `7589901f79648308fd08207ae853dc8ae7509054`. Timing varies on a shared Linux environment and is not a production energy, wall-clock or paired-native regression estimate. **The earlier fit-only ratio remains distinct from this actual fit+select measurement**; do not silently compare a fit-only numerator with an action-path denominator.

**Local scoped performance condition:** 1.52–1.75× empirical Beta on this source-free Python fit+select workload; ~34–38× reduction in the expensive prior path. This does **NOT** prove true native end-to-end <=2× CPU (native source checks, checkpoint restore, action effects and OS effects are not included). A strict final CPU acceptance gate remains **UNVERIFIED**, not PASS.

## Reproduction (no new source first-use)

From exact source checkout on a machine with stdlib Python 3.13+ and Git:

```bash
cd research/contrib/chatgpt/CKAD25-SRL01
PYTHONPATH=../../../.. PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_exact_optimization test_focused
PYTHONPATH=../../../.. PYTHONDONTWRITEBYTECODE=1 python profile_exact_selection.py
```

`profile_exact_selection.py` verifies source Git blob identities before executing and reports its own timings; times need not be byte-identical between runs/platforms. The Git ancestor `2da3...` must be available for a read-only `git show`; a local copy with the **same original blob** can be supplied using `SRL01_PINNED_PRIOR_SOURCE_PATH`. This is not a scheduled task, runner dispatch or scientific source replay.

## Engineering/science/deployment boundary

- **ENGINEERING:** 15/15 focused local tests PASS; source-only exact parity PASS; local 2× fit+select criterion PASS on two CPU profiles. Full final Windows/Linux regression, exact owner-platform native adapter/checkpoint exercise, old-task cold retention gate and genuine native <=2× cost **NOT RUN/UNVERIFIED**.
- **SCIENTIFIC:** The previous frozen 48/24-cohort SRL01 result remains only **`DEV_GO_FOCUSED_ONLY`**. Its 1,202/1,536 detection and 0.14202 Brier **tie fully trained conventional exact Bayes**. Detection gain vs empirical Beta was concentrated and uncertain; no new scientific experiment, independent replication, unfamiliar causal-law transfer or novel intelligence gain exists. The negative remapping result also remains binding.
- **DEPLOYMENT:** NONE. No merge, promotion, native accepted-weight write, FORGE/controller change, owner runner, first-use source action, paid API or scheduler. Owner [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) still blocks new protected original-world first-use.

**Next authorized gate:** independently exercise the *unchanged native adapter* with genuine source-pinned native checkpoint custody, mandatory exact-final source SHA full Linux+Windows regression, lossless cold retention and actual end-to-end native CPU ratio; do not claim acceptance before those receipts. Keep this contributor lane isolated under the sole Amalgam coordinator [#1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).
