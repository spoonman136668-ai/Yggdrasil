# ENERGY-CAL-05 — Calibrated local/global causal repair

**2026-11-20 · Independent, source-free synthetic research contributor · SCIENCE: NEGATIVE / NO-GO · DEPLOYMENT: NONE**

This extends the independent ENERGY-SHIFT-04 negative in existing [draft Yggdrasil PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346). Accepted `main` was `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. The only cumulative Yggdrasil learning and integration owner remains [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278); no accepted checkpoint, controller or native training changes occurred.

## Question

Does a small contradiction-based gate that turns on global causal repair when **at least four of five action-conditioned rows show sufficiently strong local change evidence** perform better than calibrated Bayesian alternatives, without discarding earlier readouts?

The freeze placed the threshold at local change posterior `>= 0.65`. When it fires, the candidate uses `max(local-change posterior, global-change posterior)` per row to blend reset and pooled predictions. Otherwise it uses smooth row-local change weights. This is **not** equivalent to the fully fitted hierarchical Bayesian comparator, which marginalizes over unchanged, independently changed and globally changed regimes with priors 0.25/0.50/0.25. That comparator is included as the strongest fitted control; an exact correctly specified structural oracle is included as a lower expected-loss reference.

## Precommitted procedure and provenance

1. [Preregistration](prereg.json) committed **before code and outcomes** at `01402c1cd6b06296f87ec6185143db25645fa698`.
2. [Executable source](experiment.mjs) committed `2943295d8174f1258b284ba78f1753003bfb5653`. The source is the *exact same JavaScript function object* serialized by `Function.prototype.toString()`, stored as an ES module and independently fetched back; full Git blob SHA-1 `b34ce6a71ac6d73dc71f6cf118b38160894f060d`. GitHub readback was byte-for-byte equal before any scoring.
3. One engineering smoke used **seed 93097**; no primary observations were exposed in that step.
4. One primary evaluation used frozen seeds **93111, 93119, 93127, 93133, 93149, 93157, 93169, 93181, 93193, 93203, 93211, 93227** across LOCAL_SWAP, GLOBAL_REVERSE and NULL. **36 worlds, 2,520 public fit/adaptation observations, 46,080 disjoint held outcomes.**
5. The original primary evaluation's [result.json](result.json), including all 36 world-level arm scores, was committed at `e2b826039b868e7b52ff57e44d15a835e1cb6ee9` and read back. The full result blob SHA-1 is `502af7d5908d98b1e276ffc4cf1874615741929a`. Its 36 world-level records were arithmetically re-aggregated from the **committed JSON** without rerunning the source. See [provenance.json](provenance.json).
6. The primary seeds are now **consumed**. Do **not** rerun them, tune the threshold with their scores, or convert these numbers into an independent scientific first-use result.

A future researcher may reproduce only the distinct non-primary smoke:
```bash
node --input-type=module -e "import('./research/contrib/chatgpt/ENERGY-CAL-05/experiment.mjs').then(m=>console.log(JSON.stringify(m.runExperiment('smoke').summary)))"
```
This does not qualify native Yggdrasil regression or independent replication.

## Frozen outcome

Multiclass held action-1 Brier score; smaller is better:

| Frozen arm | Action-1 Brier | Overall Brier |
| --- | ---: | ---: |
| Correct-source structural Bayesian oracle (reference floor) | **0.274064** | **0.273322** |
| **Fully fitted hierarchical change Bayes** | **0.392890** | **0.361225** |
| Candidate local/global context gate | 0.404242 | 0.366901 |
| Fully fitted global change Bayes | 0.403999 | 0.366779 |
| Fully fitted row-local change Bayes | 0.412972 | 0.371266 |
| Post-reset Dirichlet | 0.424021 | 0.376790 |
| Recency-weighted Dirichlet | 0.435394 | 0.402531 |
| Static pooled Dirichlet | 0.515654 | 0.422607 |

The candidate was **0.011352 Brier worse** than the strongest fully fitted conventional hierarchical control, not at least 0.01 better. No accuracy superiority. Total CPU and separate-process cold restore were **not measured/qualified**; the one-call V8 diagnostic wall time (~570 ms for all generation, fitting and scoring) cannot establish whole-process efficiency. Do not turn a short isolated runtime into a claimed model-efficiency gain.

| Frozen scenario (12 worlds each) | Context gate Brier | Hierarchical Bayes Brier | Best specific other baseline | Gate triggered |
| --- | ---: | ---: | --- | ---: |
| LOCAL_SWAP | 0.389723 | 0.396083 | Row-local Bayes 0.389723 (tie) | 0/12 |
| GLOBAL_REVERSE | 0.459632 | 0.423007 | Global Bayes 0.420852 | 6/12 |
| NULL | 0.363372 | 0.359581 | Static Dirichlet 0.356074 | 0/12 |

The candidate did **not** outperform row-local Bayes in LOCAL_SWAP; it made no global-gate changes there, as expected. In GLOBAL_REVERSE, broad evidence triggered only half the time, and the threshold produced worse calibrated predictions. In NULL, it did not trigger a false *global* gate in any of the 12 worlds. This is narrower than proving no false local change hypotheses.

All 36 stored historical per-state/action predictions passed an **in-process JSON round-trip**. This is **not** a multi-world cumulative memory test or independent-process cold model restoration. Action-0 held Brier was 0.329559 for the candidate and fitted adaptive controls; the protected-row criterion passed.

### Scientific interpretation and recommended stop

**Frozen verdict: `NEGATIVE_NO_GO`**. The proposed heuristic is not an improvement to cumulative intelligence, nor evidence of better causal discovery over strongest matched controls. Hard switching can be inferior to probabilistic integration of both sparse and broad causal change explanations. The exact oracle remains stronger as expected from the [correct-Bayes Brier identity](../ENERGY-BOUND-03/ANALYSIS.md); it should not be relabelled a weak opponent or target for expected-Brier superiority.

**Retire this fixed threshold/global activation mechanism from immediate primary experimentation.** Do not spend another seed cohort tweaking 0.65 or the 4-of-5 trigger based on these outcomes. Higher-value research would require a qualitatively different falsifiable mechanism, such as learned cumulative causal structures and real independent-process functional retention across **out-of-family** intervention tasks, against equal-data flexible conventional controls. New studies need fresh frozen sources and separate owner-controlled qualification; avoid creating a rival canonical learner.

## Engineering, science and deployment separation

- **ENGINEERING — PARTIAL:** Exact executable GitHub readback, once-only deterministic primary, repo-stored full world-level score table and arithmetic readback PASS. Dual-platform native tests and G29 source atlas qualification are **not passing**: the existing source index is pinned to an older tracked file set. Do not weaken the guard.
- **SCIENTIFIC — NO-GO:** Strongest conventional comparison fails. Local vs global behavior and null negatives are preserved. No native retention, reasoning, transfer or intelligence gain verified.
- **DEPLOYMENT — NONE:** No main ref edit, runner/queue dispatch, native checkpoint promotion, model restart, scheduler, or integration was authorized or performed.

## Postscore arithmetic audit (not a science replay)

A separately committed [audit.mjs](audit.mjs), commit `2d54051c607c408628a10e66d2a84a9b08ba9c6b`, checks the saved primary receipt only: 36 unique seed/scenario keys, per-arm Brier bounds, world quotas, aggregate mean equality, each scenario mean, source commit identity, recorded negative controls, control ranking and frozen verdict. The audit source was GitHub-readback-verified (Git blob `d5f66df41e95f16d8d813e8800f1ffe3d475fa86`), then executed against the repo-stored 71,458-byte [result.json](result.json) without rerunning the generator. **AUDIT PASS: 36/36 worlds, 46,080 held, hierarchy Bayes strongest fitted baseline, candidate +0.011352 Brier worse, 0 NULL global gate false triggers, negative NO-GO.**

Local reproduction of **arithmetic auditing only**, safe on a clone without reusing scientific primary seeds:

```bash
node --input-type=module -e "import('node:fs').then(async fs=>{const m=await import('./research/contrib/chatgpt/ENERGY-CAL-05/audit.mjs');console.log(m.auditResult(JSON.parse(fs.readFileSync('./research/contrib/chatgpt/ENERGY-CAL-05/result.json','utf8'))));})"
```

This audit is **postscore**, not independently preregistered scientific validation. It cannot independently verify the unrecorded individual held transition outcomes, runtime environment, model first use or science qualification.
