# Gate 25 — Unfamiliar intervention worlds, temporal consequences, cold source reuse

**SCIENTIFIC NO-GO.** New evaluator/world class (not a sixth rerun of the Gate20–24 static six-bit Boolean prediction experiment). This is a contributor-only development test on draft PR #1340.

## Frozen chronology and custody

- Parent fully qualified Gate24: `2a42430cecc25d4fea84034cf9a31d0bc1dc0715`.
- [Frozen preregistration](prereg.json): `5f9cc9abeea1b9b339452e3229cd56fc0139d3cc`.
- [Frozen executable](run.cjs): `5ab2dff8f42292d92ffc64cb44a92a18e525fe22`, blob `fc614a8ce4dc08406d29450521684f770094c981`, committed before primary outcome.
- [Initial scored result](result.json): `550c2ce10250a89850c898afc8cdeeb733ff810a`. [Audit](audit.cjs) and [provenance](provenance.json) added later.
- No updated source, changed primary seed, tuned thresholds, retested alternative primary policy, or scientific first-use replay after seeing results.

## Different experimental environment

Four fresh 24-trial cohorts: **immediate intervention effect**, **delayed prior-action effect**, **stationary stable topology**, **independent fair-noise outcomes**. Each 8-bit public sensor state is changed by one of **four applied actions**. The next state has two public consequence bits generated from two hidden sensor parents and an immediate or previously applied action; the six remaining state sensors also evolve with state and actions. The learner observes the current public state and current/prior action, predicts the *next* two consequence bits, then receives the actual public transition. It never receives the true hidden parent edges or the actual A→B→A phase labels.

Each world has 64 source interventions A, 48 online transitions under unfamiliar changed B wiring, and 48 return-A transitions. An independent action policy supplies the same sequence to all predictors (not an agent-selected policy). At the end of B and return A, 16 independent intervention probes per phase are evaluated without revealing those outcomes for fit or selection. Held probes have distinct full public state+action+history feature vectors from target-phase training, though lower-order patterns can overlap.

## Learner, comparisons and budgets

- **Local self-assembling:** per-outcome graph of at most three incoming public features from 8 sensor bits, 2 current-action bits, 2 previous-action bits. Updates by one-edge add/delete/swap locally every eight experiences if recent penalized leave-one-out Brier improves >=0.006. A64 source topology and counts remain immutable. Source reliability abstention for source LOO risk >0.20, plus a last16 prequential log-likelihood soft blend of source and recent local models.
- **Independent strong controls:** separately written globally refit rolling-32 conditional subset, globally refit all-history subset, Bayesian hazard mixture of source and rolling recent predictor, source-only frozen memory, constant .5, and a no-retention local ablation. Same observed intervention/outcome stream and source exposures for every arm.
- **Persistent state:** fixed **512 byte** packed A64, B/R96, masks, graph edits and evidence; saved/restored after B48 and R72 and tested throughout continuation. No process-exit or actual native checkpoint tested.
- **Compute counts:** local about 1,344 candidate evaluations per related trial, global exhaustive comparator 14,304; these differ. Neither exact compute equality nor faster wall time/energy is established.

## Frozen result — 48 related paired interventions (Brier, lower is better)

| Paired contrast | Mean improvement local over comparator (positive is local better) | Normal 95% CI |
|---|---:|---|
| B prequential vs exhaustive rolling-32 | **−0.107292** | [−0.119515, −0.095070] |
| B prequential vs Bayesian hazard | **−0.095088** | [−0.107151, −0.083025] |
| Return held vs rolling-32 | **+0.019764** | [+0.015773, +0.023755] |
| Return held vs Bayesian hazard | **+0.001168** | [+0.000417, +0.001918] |
| Return held vs frozen A-only | **−0.000079** | [−0.000196, +0.000039] |
| B prequential vs no-retention ablation | **−0.024509** | [−0.028080, −0.020937] |

The stored A graph explains essentially the entire useful return benefit. The local rewiring layer makes predictions much worse **while the changed-world interventions are happening** than global recency or Bayesian controls. On a truly stationary graph, local edits still occurred in **7/24** trials (frozen false-edit limit ≤20%); fair-noise false edits **0/24**. All 96/96 exact in-process byte checkpoints, immutable source state, fixed action-schedule and phase-held exclusion checks passed.

**Verdict:** **10/18 PASS; 8/18 FAIL → SCIENTIFIC NO-GO.** Better source persistence is not proof of better learning or intelligence. The new trial is more causally grounded than earlier IID label worlds but remains synthetic, fully observable apart from hidden parent wiring, and does not prove agent-selected intervention value, outside-world transfer or genuine cold-process retention.

## Exact reproduction

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate25/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate25/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate25/audit.cjs
```

**ENGINEERING:** chronological source/result custody confirmed; final dual-platform G29 atlas, repository tests, and exact Node replay must pass on the final candidate for engineering PASS.

**SCIENCE:** unequivocal NO-GO on frozen joint thresholds. Recommend discontinuing speculative local-graph superiority claims on this mechanism until evidence that source knowledge actually improves novel B actions; source-only and strong Bayesian controls are sufficient for much of observed benefit.

**DEPLOYMENT:** NONE. Existing research contributor PR #1340 stays draft. The accepted Yggdrasil cumulative Amalgam learner, native PublicCausalCells control, main, checkpoints and owner research loop are untouched.
