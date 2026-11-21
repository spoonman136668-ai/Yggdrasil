# CSMC-01 — Causal-structure-aware replay (exploratory development)

**Status:** `ENGINEERING_MIXED_FORECAST_GATE_FAIL`; **SCIENCE UNVERIFIED**; **NO deployment, merge or scientific first-use**.

## Question
Can the native Yggdrasil learner retain a smaller set of previously experienced, causally important interventions, rather than simply the largest prediction errors, while preserving the two-stage mechanism's decisions and forecasts?

## Frozen source / parent
- Original coordinator Amalgam [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), exact parent `86264b41a08d49f558418c0fba367f3a2636befa`.
- Only **50 previously consumed synthetic FIT events**, archived `research/contrib/chatgpt/CAUSAL-AMALGAM/selection-dev-01/trace.json`, raw SHA256 `36f535c451c813dd56afd58c4f1833ac8e5fca98627d898a571e40c8bc8a0114`.
- Exclude ALL 46 previously used validation / familiar-return records, indices 50..95; no novel world observations.
- Current candidate work is in this independent contributor branch. There is **no second coordinator or promoted learner**.

## Method
1. Preserve the original first 8 projection witnesses, so the projection selection sequence is not discarded.
2. Cover all 15 observed second-stage evidence cells keyed by public `(context, x1, s2, x2)`, choosing each missing cell's earliest witnessed event.
3. Use a **20/50 active-reference budget**. Fill remaining positions using a fixed ordered score (fewest changed action decisions, then smallest stage-two forecast discrepancy, then stage-one discrepancy, then mean discrepancy, then chronological witness index). Exactly two bounded local swap passes are allowed.
4. Evaluate only the *already consumed* FIT records against the entire 50-FIT compact exact-fraction model; compare with PCER-02, uniform20, earliest20, coverage20 and the exact sufficient-statistics control.
5. Test the candidate on the **actual original Yggdrasil native episode class** with the new tracked `test_csmc01.py`. Full original native execution on this branch is **not yet evidenced**. No model, archive or accepted state is rewritten.

The local preregistration was frozen with SHA256 `49c9c00d4b6752d28ff9ce934b6405c9b16b9fdc1bce70375579a57a6dcc4612` *before the exploratory local run*. However, the Git commit recording it occurred *after* that run. **This is therefore UNPREREGISTERED exploratory development for the repository's confirmatory-science rules.** No prospective scientific claim is made.

## Observed local development outcome
| Method | References | Terminal cells covered | Changed actions / 10 | Maximum stage-1 probability gap | Maximum stage-2 probability gap |
|---|---:|---:|---:|---:|---:|
| Full FIT reference | 50 | 15 | 0 | 0 | 0 |
| **CSMC-01** | **20** | **15** | **0** | **0.153846** | **0.190476** |
| PCER-02 | 10 | 8 | 4 | 0.252747 | 0.357143 |
| Uniform-20 seeded by SHA256 | 20 | 13 | 3 | 0.115385 | 0.190476 |
| Earliest-20 | 20 | 14 | 3 | 0.211538 | 0.380952 |
| Coverage-earliest-20 | 20 | 15 | 2 | 0.250000 | 0.380952 |

**Frozen engineering limits:** 15/15 terminal-cell coverage, unchanged 10/10 actions, stage-1 maximum probability gap **≤0.10**, stage-2 maximum **≤0.15**. **FAIL** on both probability limits, even though actions and coverage pass. No replay index is accepted or promoted.

The exact two-stage conventional sufficient-statistics state is an essential stronger baseline; it exactly reproduces the *frozen FIT snapshot* without 50 active replay references, although it does not supply identity-aware replay, complete provenance, long-horizon repair or causal transfer. No matched-feature memory savings are established here.

## Reproduce from a full repository checkout
```bash
PYTHONPATH=. python -B research/contrib/chatgpt/CSMC-01/selector.py
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CSMC-01 -p 'test_*.py' -v
```
The new tracked test imports the original `NativeEpisodeExperience` and checks 50-vs-20 forecasts, 10 proposed actions, cold restore, tampered checkpoint, duplicate IDs and conflicting replay. **Those repository-native tests have not yet run on the exact branch**. The 7/7 PASS was an isolated local **independent compact-source surrogate**, not a Windows/Linux full regression. No PR is open for this branch and no hosted CI or workstation runner has been dispatched.

## Implication and next proposed design
Selecting more causally diverse experiences improves **action choice fidelity** on the observed FIT cohort but still discards enough evidence to distort probabilities. A more defensible next approach is a **two-tier mechanism sketch**: losslessly preserve the sufficient statistics and adaptive loss selectors for *both* causal stages, plus a bounded witness cache and immutable archive read-through for replay identity, disagreement resolution and future repairs. It must beat or meaningfully complement a matched-feature compact sufficient-statistics baseline; simply matching it or being smaller than the original native ledger is not scientific gain.

Fresh original-world science, unfamiliar transfer, cold long-horizon retention and deployment are outside this research authorization and remain blocked on source-owner admission (Yggdrasil issue #426). No current branch or CI check grants that authority.

See `prereg.json`, `selector.py`, `test_csmc01.py`, `result.json` and `provenance.json`.
