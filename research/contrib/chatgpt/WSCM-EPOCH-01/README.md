# WSCM-EPOCH-01 — Source-free native local-epoch retention experiment

**Disposition: INVALID_INCOMPLETE_WALL_TIMEOUT (NO SCORED RESULT).** This line did not demonstrate improvement or failure of the scientific memory hypothesis. Its first frozen primary attempt exhausted the execution wall limit without a result. Neither positive nor negative Brier claims are authorized from this attempt.

## Freeze and provenance

- Research contributor [Yggdrasil PR #1364](https://github.com/spoonman136668-ai/Yggdrasil/pull/1364), stacked only on frozen Amalgam [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) head `86264b41a08d49f558418c0fba367f3a2636befa`; accepted main unchanged.
- **Preregistration commit BEFORE source code and BEFORE the first scored invocation:** `c8dbfb5156e3ebe2878bf518806579c311df9467`, file `prereg.json` Git blob `55dbc55bf9722d02bb1f5adfea537d47e055bb15`.
- **Exact implementation/test commit BEFORE first scoring:** `effa9b6ff1cd054b473ce2b22475a50568493f05`; `experiment.py` blob `bc91d9817d4edfcfd16b2b313782270c7ef87c14`; focused test blob `bf7e5f12478b42dd0bf7a5b92ecbf7370f7ffb7a`. No algorithm, threshold or frozen seed was changed after the first scored attempt.
- Original native episode module Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`, original previously consumed 1,025-witness joint archive SHA256 `576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8`. The local test environment used the exact native episode source with its declared subset source-equivalent dependencies, not the complete original dependency tree.

## Research design, frozen before execution

A fixed two-epoch, public-context-isolated transition candidate retains the original frozen native checkpoint and creates separate bounded native `PublicCausalCells` counters when genuine public transition surprises recur. An eight-event prequential paired-loss window elects a new specialist or reactivates the old one, without showing the learner source regime labels. Counter states and the native continuing control cold-restore at the specified stage boundaries.

Three independent source-free seeds for A→B→A, and three for unfamiliar context-1 change A→C→A; 112 paired episodes per seed, with fixed public actions; total planned **672** synthetic transition observations. Matched readouts: frozen original native; continuing original native; fully fitted per-context/action cumulative Beta; trailing-32 Beta; bounded hazard-1/32 change-point Beta; and equal-two-expert Bayesian evidence baseline. Every readout observes exactly the same actions/outcomes in the original code. Compare mean transition Brier, cold familiar return, uninformative/spurious triggers and unfamiliar structure transfer. Exact thresholds and STOP rule are immutable in `prereg.json`.

## What ran

- Pre-scoring Git blob parity checks for prereg, script, tests and original native module: **PASS 4/4**. Nine source-free deterministic negative/interface and leakage unit tests: **PASS 9/9** (Linux CPython 3.13.5).
- **First primary execution** invoked `experiment.py` unchanged with the archived original checkpoint and original `prereg.json`. The container command hit the **120-second wall timeout**, returned no usable stdout/result, and was terminated. No `result.json` exists. The number of generated/scored synthetic episodes completed before termination is **UNKNOWN**. Do not describe the 672 planned events as 672 completed events.
- No protected/original-world source was first-used. No paid model call, training dispatch, native production modification, model promotion, accepted ref update, or deployment.
- Follow-up engineering smoke profiling on *non-primary*, non-scored synthetic inputs found initial cold restore ~1.53s; eight native observational appends ~0.013s each; one 112-event constant smoke ~7.93s; one unrelated stochastic 112-event smoke ~8.35s. **These profiles do not explain the primary timeout.** The failure could be platform/test harness or a data-dependent native execution path; root cause is unverified.

The prereg freezes **one scored pass** and prohibits replay/tuning to rescue a result. Accordingly, the attempted trial is **terminal incomplete/invalid**, not `DEV_PROMISING`, `DEV_NO_GO` on learning, or a `SCIENTIFIC_PASS`. No scored metrics are populated or invented. Its incomplete source-free trial is recorded in `execution-failure.json`.

## Reproduction (do not rerun consumed primary seeds as acceptance)

The immutable candidate is inspected with:

```sh
python -m unittest discover -s tests -p 'test_wscm_epoch01.py' -v
```

The exact frozen scorer requires the authentic archived joint JSON and the candidate `prereg.json` under a checkout that includes the pinned Amalgam base; the primary scorer command is in the source's `--help`. **Do not run the same frozen scored seeds again without a distinct, prospectively authorized recovery protocol and custody of the consumed attempts.** The next substantive scientific trial must freeze a new independent source-free seed cohort, bounded time/cost/accounted partial progress, use exact original-module dependencies on the final candidate, compare fully fitted matched baselines and score after cold A→B→A retention, while reserving original-world protected first-use for separate owner authorization.

**ENGINEERING:** source integrity and 9 contract tests PASS; primary execution FAIL_TIMEOUT; complete final Linux/Windows regression UNVERIFIED. **SCIENTIFIC:** native memory retention/transfer advantage UNVERIFIED. **DEPLOYMENT:** UNVERIFIED, draft unmerged.
