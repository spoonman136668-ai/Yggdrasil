# CKAD41–49 evidence audit — stop repeating the wrong experiment

**2026-11-19 · Read-only research qualification audit · NO new scientific first-use, model modification, training reset, main edit or promotion.**

This consolidates nine **original source- and outcome-qualified** Yggdrasil-sidecar experiments using their **committed `dev_screen_report.json` receipts**, not old assistant assertions or recollection. Each study's original report is under `../CKAD-41/ ... ../CKAD-49/`. Run `run_audit.py` for machine-checked, provenance-pinned numbers. The reproducible audit never imports or executes the scientific campaigns, consumes no original DEV/pilot/primary seed, and has eight engineering-only archive tests.

## Decision

**Scientific DEV_PASS: 0/9. Scientific DEV_NO_GO: 9/9. Engineering-scoped PASS: 8/9; CKAD42 engineering UNQUALIFIED because the learned weight-checkpoint SHA differed across Ubuntu/Windows.** Every study's original exact-source GitHub Actions run ended in workflow `success`, but that is *not* a synonym for engineering/scientific acceptance. CKAD42's score means matched while one learned checkpoint digest did not. CKAD43 separately had an immaterial `2.7755575615628914e-17` cross-platform floating score difference while its source checkpoint digests agreed; avoid calling that exact floating-point parity.

All experiments stopped after frozen development thresholds failed, never ran their reserved scientific pilots or primaries, and did **not** run the required full final repository regression for an accepted candidate. No original Yggdrasil accepted `main` model weights or native API were updated. The accepted `main` observed at audit time is `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.

### Original frozen development margins

A **positive gain** below means candidate has lower (better) Brier than the named trained comparator **within that same experiment only**; a negative gain means candidate is worse. The gain is `comparator − candidate`, in absolute Brier units. Every threshold applies to **both** original DEV seeds. **Do NOT compare or average Brier levels/gains across experiments:** CKAD41–44 use late-phase observed synthetic A→B→A outcomes, CKAD45 uses common off-policy causal probes after different chosen interventions, CKAD46 uses prequential unfamiliar-action source Brier, and CKAD47–49 use different exhaustive terminal-composition worlds. Strongest baselines differ.

| Gate | Mechanism and actual comparator for frozen margin | DEV seed 1 gain | DEV seed 2 gain | Minimum on both | Engineering |
|---|---|---:|---:|---:|---|
| CKAD41 | Native 16-episode recall vs best original native / fitted Beta / 32-episode memory | **−0.030633** | **−0.008663** | ≥0.015 | PASS |
| CKAD42 | Two causal bases vs already-trained discount93 / original native / fitted Beta | **−0.000082** | **−0.003285** | ≥0.010 | **UNQUALIFIED** |
| CKAD43 | Persistent expert routing vs best discounted causal/native | **−0.001267** | +0.000350 | ≥0.010 | PASS |
| CKAD44 | Contradiction/evidence retrieval vs strongest original-native or discounted causal | +0.003114 | +0.004212 | ≥0.010 | PASS |
| CKAD45 | Learned source-aware action chooser vs fully trained exact Bayesian information gain | **−0.003354** | +0.004517 | ≥0.010 | PASS |
| CKAD46 | Unseen action-token grounding vs exact balanced-map posterior | **−0.011111** | **−0.002058** | ≥0.015 | PASS |
| CKAD47 | Four-way XOR composition vs independently fully fitted unrestricted tabular | +0.001795 | +0.001848 | ≥0.010 | PASS |
| CKAD48 | State-partition action effects vs independently fully fitted unrestricted tabular | +0.000802 | +0.000613 | ≥0.010 | PASS |
| CKAD49 | Unknown singleton exception and addition/XOR operator vs unrestricted tabular | +0.000976 | +0.004121 | ≥0.010 | PASS |

These are **control-gap margins**, not the entire frozen acceptance rules. In addition CKAD42 violated early-phase and deterministic-source controls, CKAD43 broke early return, CKAD44 missed a late-return and one absolute Brier bound, CKAD46 also violated unfamiliar-action early prediction, CKAD47 violated early novel transfer in one seed. Every original experiment report includes its own complete prereg, seed custody, phase gates, CI receipt, control scores, negative controls and full caveats.

### Exact original evidence and qualification runs

| Gate | Original source SHA (prefix) | Evidence | GitHub Actions |
|---|---|---|---|
| CKAD41 | `4458be879af0` | [CKAD41 receipt](../CKAD-41/dev_screen_report.json) | [44442044268](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44442044268) |
| CKAD42 | `290b9a7f0ccd` | [CKAD42 receipt](../CKAD-42/dev_screen_report.json) | [44445368631](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44445368631) |
| CKAD43 | `e5dda4e582bc` | [CKAD43 receipt](../CKAD-43/dev_screen_report.json) | [44495061873](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44495061873) |
| CKAD44 | `4f8dc305f3b1` | [CKAD44 receipt](../CKAD-44/dev_screen_report.json) | [44497581168](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44497581168) |
| CKAD45 | `89081c51a101` | [CKAD45 receipt](../CKAD-45/dev_screen_report.json) | [44500365682](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44500365682) |
| CKAD46 | `49f52a79405e` | [CKAD46 receipt](../CKAD-46/dev_screen_report.json) | [44504915242](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44504915242) |
| CKAD47 | `dc99602f8f96` | [CKAD47 receipt](../CKAD-47/dev_screen_report.json) | [44507998278](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44507998278) |
| CKAD48 | `86075fb964ef` | [CKAD48 receipt](../CKAD-48/dev_screen_report.json) | [44510045592](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44510045592) |
| CKAD49 | `2802bdad9f3f` | [CKAD49 receipt](../CKAD-49/dev_screen_report.json) | [44519725256](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44519725256) |

All nine listed original runs were re-read from GitHub and show GitHub Actions completion `success`. CKAD49 staged a separate fixture-only [successful run 44519577472](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44519577472) before the first original scored DEV source. The automated unrelated proxy-fanout failures are not evidence that a research hypothesis failed.

## Mechanistic findings: what actually worked, and what did not

**1. Native causal continuity exists inside some studies, not across the research program.** Original source IDs, observable action→transition→terminal outcomes, cold checkpoint byte identity, nonreplay and retained source histories were deliberately tested in many experiments. However each CKAD study creates a **separately constructed learner or research-sidecar and new synthetic source stream**. Stacking code/PR history is **not** the cumulative trained-parameter trajectory of one accepted Yggdrasil model. CKAD47–49 are even new four-state/four-action research implementations; the accepted `NativeEpisodeExperience/PublicCausalCells` binary-action interface is unchanged. There is no proof that native accepted production learning progressed from CKAD41 through CKAD49.

**2. Having a learned hypothesis among available candidates is not discovering unknown physics.** CKAD42 used a finite causal grammar, CKAD46 assumed the unseen names mapped to two familiar actuator classes, CKAD47 hard-coded XOR-group structure, CKAD48 enumerated both true state partitions, and CKAD49's expanded 16-hypothesis grammar already included both true causal feature/operator combinations. Observational evidence selected the right candidate, which is meaningful bounded system identification, but it has not demonstrated construction of genuinely *out-of-grammar* causal operators.

**3. Extra memory, routing and posterior collapse rarely add predictive value.** CKAD41's more accessible memory worsened baseline native forecast. CKAD43 experts falsely switched; CKAD44 showed small but insufficient advantage. CKAD48 and CKAD49 almost perfectly equaled their **full exact Bayesian model-average** controls. The added hard-gate decisions contributed no demonstrated prediction improvement once source evidence already concentrated. Do not declare a scientific improvement by outperforming a deliberately restricted predecessor while a stronger conventional/structural comparator performs nearly as well.

**4. Active action selection is distinct from passive prediction.** CKAD45 genuinely chose interventions and learned from their consequences; it changed roughly 21% of actions versus exact information gain. Yet its policy was worse on one seed and improved by only 0.004517 on the other. Selection diversity by itself is not better *intervention value*. A future qualifying experiment must measure held causal uncertainty reduction, downstream action utility, robust unfamiliar-world adaptation, and process cost under equal intervention budget against trained exact information gain and random/coverage.

**5. Entire-process cost, independent held transfer and learned knowledge accumulation are not proven.** Many sidecars increase learned counts, hypotheses, checkpoints, update and readout work. Equal observed source does not mean equal compute. Two development seeds per gate with reused synthetic contracts are NOT independent broad transfer evidence. A correct cold restore preserves bytes, but does not necessarily prove *old capability retention under interference* or recovery without task-specific scripts.

## Binding recommendation: stop mechanism churn until the missing capability is tested

**No CKAD41–49 implementation is ready for scientific promotion.** This audit does **not** ask to halt the independent Yggdrasil research owner or any other authorized research track. It rejects the specific assumption that more small synthetic wrappers automatically turn into cumulative native intelligence.

The next eligible **development** program should first verify the canonical owner-qualified **trained-state continuity contract**: authoritative accepted source/tree, owner/runner, immutable snapshot/ledger and original knowledge baseline; identify how a safe, isolated research candidate will load the *same prior trained state* without erasing it, then measure source receipt continuity, true learned retention, and whole-process CPU/GPU/wall/checkpoint growth. Treat unavailable owner state as **UNVERIFIED**, not restart a model or secretly call a new training owner.

Only then preregister a **truly disjoint unfamiliar-physics transfer** across multiple mechanisms **not expressible in the candidate's starting grammar** (for example, state-dependent nonpermutation transition operators, relational resource interactions, hidden action affordances that require novel factor discovery). Freeze sources, seeds, matched interventions and compute, strong independently fully trained tabular/symbolic/adaptive controls, negative and random-action baselines, unknown-family cold transfer, old-domain interference/recovery and reproducibility. Require a clear **precommitted predictive/utility gain over the strongest fully trained control on every held seed**, independent custody, and exact checkpoint cross-platform parity. Predefine a small bounded development budget and stop when falsified. No pilots/primaries or final promotion without separately verified scientific owner acceptance and mandatory full final regression.

In plain English: **the missing evidence is not whether Yggdrasil can select a rule from examples. It is whether a persistent Yggdrasil model learns a relationship it did not already know how to represent, retains past relationships, and uses it to act better than strong alternatives at worthwhile cost.**

## Audit execution — no new training

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-41-49-AUDIT -p test_audit.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-41-49-AUDIT/run_audit.py --pretty
```

The evidence verifier loads original receipts only, validates exact original source/CI IDs, negative scientific classifications, qualification exceptions and matched within-study margins. It never executes `campaign.py` or `screen_dev.py`, never consumes a study's original seeds, invokes no model, and does not mutate any trained state. All evidence remains in GitHub, no chat attachments or user File Library clutter.
