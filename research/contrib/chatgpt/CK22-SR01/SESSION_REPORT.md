# CK22-SR01 — independent seed-group robustness and novel-candidate diagnostic

This analysis was frozen AFTER the already-consumed CKAD22 experiment.
It is not new preregistered scientific evidence and it did not train a model or
execute another source episode.

**Original CKAD22 engineering PASS; original development GO; scientific PASS not established.**
Source SHA: f04cfcac2aa07806a6b942d968119de87bfb6aaf. Original result semantic SHA256: 4b20ef3b9229eddfd509e5897e6aa8f8d5226288ab331c4a98f8a7bc46fbccc2.
The original 9/9 Linux/Windows CI is run 44266448951.

| Session | Evaluator context (not given to learner) | Novel /288 | Retrieval /288 | Random probes /288 | Trailing MLE /288 |
|---|---|---:|---:|---:|---:|
| 0 | terminal_switch r0 | 264 | 225 | 232 | 252 |
| 1 | invariant r1 | 238 | 238 | 238 | 157 |
| 2 | terminal_switch r0 | 246 | 257 | 249 | 214 |
| 3 | invariant r0 | 249 | 249 | 244 | 218 |

## Per-seed gains on first encounters (sessions 0 + 1)

| Seed | Novel minus retrieval (successes /192) | Novel minus trailing MLE | Novel minus random-probe arm |
|---|---:|---:|---:|
| 101 | 0 | 16 | 32 |
| 202 | 0 | 23 | 0 |
| 303 | 39 | 54 | 0 |

Exact two-sided seed-cluster sign-flip p-values (3 independent seed groups):
- beta: 1/4
- novel_random: 1/1
- pooled_replay: 1/1
- retrieval_only: 1/1
- trailing_mle: 1/4

Novel-vs-retrieval shares actual new probe receipts. Novel-vs-random-probe
also differs in selected probes, so it is not a pure novelty ablation.
A source-matched exact independent online mixture ties the native learner;
this prevents interpreting the source experiment as architecture superiority.

All 12 sessions have 32 new-candidate updates and preserve 320 old ledger
events plus previous sessions. Candidate posterior starts at 1/8 each session;
ending weights, per-seed rewards, original metric fractions and falsification
controls are retained in the canonical result JSON.

No model state was modified. The source was already consumed.
Exact cross-platform audit SHA256: 3444e09812c50de3b827ac3b0d9193a774a15867bfa8d3fa27a593dd1d406c66

**ENGINEERING:** subject to final sealed SHA regression and independent source audits.
**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**
