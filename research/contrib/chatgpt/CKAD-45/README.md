# CKAD45 — Real closed-loop intervention selection against strong native causal controls

**Standalone source-trained Yggdrasil development experiment.** Parent CKAD44 [PR #1304](https://github.com/spoonman136668-ai/Yggdrasil/pull/1304) pinned SHA `c61e5d28a6e87542ed4018cd3da07216dadc669b`; pre-source protocol commit `ab6f435adcbb09116efde103c4be5614db6f1d0c` predates all CKAD45 implementation and original DEV scoring. Neither accepted `main` nor native training owner is changed.

## Why this is a different and falsifiable experiment

Previous CKAD43/CKAD44 used an authentic action-consequence training stream but received intervention actions from a prechosen exogenous policy. They **could not establish an improvement from deciding which action to take**. CKAD45 makes that decision causally consequential: the learner chooses first action `x1`; the environment reveals a stochastic next state `s2`; only then does the learner choose second action `x2`; the world reveals stochastic terminal consequence `y`. Both actually witnessed consequences are trained once using the existing `NativeEpisodeExperience(repair=True)` and the exact-lossless `NativeInterventionRelations`, without resetting historical native weights. The private world family, phase and unchosen action outcomes are inaccessible to the policies.

Two **new** hand-specified structural families differ from the prior CKAD39 A/B rules and each experiences an unannounced A→B→A shift. Common observed context, nuisance variables and exogenous outcome noise are identical across policy counterfactual branches, but actual trained source events **differ by chosen interventions**, as they must. This is development-only synthetic structural variation: it is not independent real-world grounding, unseen action meanings, unrestricted causality or intelligence.

## The causal decision and comparison

**IPFC-style contradiction-conditioned falsification:** Its fully trained CKAD42 exact learned-causal model maintains full evidence and discounted recent evidence. During a predeclared 12-observation source-history alarm (>0.19 mean two-stage prequential Brier), choose each first/second intervention maximizing `H2(P_short)+4*(P_full-P_short)^2`; otherwise use pure exact Bayesian short-posterior information gain `H2(P_short)`. The action second stage conditions on the observed next state only. This is a bounded research hypothesis, *not validated IPFC or a new accepted Yggdrasil foundation*.

**Strong independent controls**, each with separate cumulative native and exact-causal learners trained on the same number of witnessed interventions:
- Exact learned Boolean-hypothesis posterior **Bayesian expected information gain**. Within each hypothesis the outcome noise is fixed, so `I(H;Y|a)=H2(P(Y=1|a))-H2(noise)`. Maximizing information gain is exactly maximizing predictive entropy here, not a weak heuristic mislabeled as a strong control.
- Independently fitted Beta(1,1) posterior-entropy selection over observed action/consequence cells.
- Intervention-coverage-balanced action choice, least observed cell.
- Source-seeded random intervention choice.
- Fixed-zero negative control.

No oracle-chosen action, counterfactual outcome or guessed regime is available to any policy.

## Fairness: same action budget, same unseen evaluator

All six policies get **232 episodes per world**, exactly two observed interventions per episode and the same exogenous context/noise streams. Action IDs and actual outcomes differ appropriately by decisions; evidence is *not falsely described as matched observations*. Each policy uses identical native and causal learner architecture/source capacity, no owner runtime authority. Extra algorithmic planning compute differs and is measured as total work (no efficiency equivalence claim).

To avoid selecting easy on-policy examples, every eight episodes after the common first-48 stream, an **independent evaluator** reads all 16 common combinations of (context, first action, already observed next state, second action) and computes the EXACT expected two-stage Brier from the source world's private probabilistic transition and terminal laws. Its output is not trained, is never added to any source ledger or causal model, and includes no actual reward/control signal to the policy. This fixed oracle *scorer*, not the learner, assigns phase labels and compares the same hidden truths for all six policies. Parallel metrics for the unchanged native learner guard against benefiting only the separate causal sidecar.

## Frozen thresholds and first-use fence

New DEV seeds **45111/45112**; disjoint held pilots **45211/45212**, primaries **45311/45312/45313** never executable. CKAD37–44 original development cohorts are not rerun.

On **each** DEV seed, the candidate must reach pooled late-B + late-return expected examiner Brier ≤0.145, beat the **best** of five source-trained control policies by ≥0.010, not worsen pooled original native examiner versus best original-native control by more than 0.005, not worsen early-return A by more than 0.010 versus best, and improve late-return A versus exact Bayesian information gain by ≥0.010. Its actual intervention choices must differ from exact information gain on ≥10% of intervention decisions, preventing false gains when two algorithms choose the same actions. Strict original 48-source ledger, cold-byte exactness, duplicate/conflicting event atomicity, equal genuine action/source counts, counterfactual evaluator read purity and no held first-use are mandatory.

**Any threshold failure is `DEV_NO_GO`, no same-seed tuning;** source-integrity failure is engineering failure. Even all DEV gates passing would mean `DEV_FEASIBLE_NOT_SCIENTIFIC`, *not* independent scientific qualification. An owner-authorized, preregistered unfamiliar-action and broader structure held experiment plus full required-platform regression would still be mandatory.

## Source-only DEV reproduction

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-45 -p test_ckad45.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-45/campaign.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-45/screen_dev.py
```

The dedicated workflow runs tests before any two DEV seeds, on the exact SHA on Ubuntu and Windows. It does not use any scheduled tasks, external paid APIs, official Forge/Yggdrasil autonomous owner/runner, model resets, `main` changes, merges or deployments. Full numeric evidence, negative controls, SHA custody, time/cost and scientific stop are persisted under `CKAD-45/dev_screen_report.json` on GitHub; no chat attachments or File Library clutter.
