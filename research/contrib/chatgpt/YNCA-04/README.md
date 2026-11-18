# YNCA-04 — cost-aware probes against unfamiliar causal laws

**RESULT: DEVELOPMENT_NO_GO.** The native tokenless source-free prototype was compared against fixed, random, trained-global and four-known-law exact Bayesian value/information-gain controls. The experiment is separate from CKAD's integrated Yggdrasil learner.

## Proof and chronology

- Accepted-main fork `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, unchanged.
- Frozen corrected source `b8bb54b41f8849cfdc3e768edff9f76049fdd53b`, SHA-256 `78cb7150bddc215b07422073b8df9100fda05f36cea57ad1219f99a819c596bc`.
- Original preflight caught a **real sign error in Bayesian expected terminal value**, and stopped before heldout use. The comparator was repaired, its source/prereg frozen, then focused 8/8 tests passed each OS: [run 44279514580](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44279514580).
- Train-grammar DEV: 512 worlds, Linux and Windows matched, [run 44279758792](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44279758792). Native development performance was negative against Bayes; no tuning followed.
- Prospective shifted/novel-law source-free heldout: 1024 worlds with unseen MAJ3 and MUX3 laws, Linux and Windows independent replay from identical frozen source. [Run 44279969568](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44279969568), both jobs PASS and result bytes identical.
- Original result preserved in `result.json`, SHA-256 `a20772dccf3354f341207ec300fcbb17a1d41b9d19c93e6836670a26e9c1a498`. Full provenance in `provenance.json`.

## Heldout metrics — lower is better

| Policy | Total causal decision regret + probe cost | Mean probe count |
| --- | ---: | ---: |
| Four-law Bayesian value planner | **0.297554687** | 0.394531 |
| No probe / trained-global abstention | 0.298476562 | 0 |
| **Native learned action-value memory** | **0.303251953** | 0.315430 |
| Shuffled-reward negative | 0.303218750 | 0.203125 |
| Random probes | 0.395199219 | 2.000000 |

Native / strongest eligible baseline = **1.019146953**, which fails the preset required <=0.95. Paired 95% interval for strongest-control-minus-native is **[-0.020068359, +0.009515625]**. The shuffled-reward control is effectively tied with native. The model did not discover new laws; its Bayes readout remains restricted to four training laws.

**Plain English:** The native policy did learn a nonrandom, low-cost probing behavior, but it did not improve terminal decisions beyond either avoiding probing or applying a simple exact Bayesian planner. Additional probes are not inherently useful.

## Controls and limits

- All arms saw the same 12 passive observations, action menu and maximum two probes/four sampled outcomes, with total allowed probe cost <=0.085.
- Independent fixed actions (all eight), random probing, trained global action values, no probe, four-law Bayesian value/entropy planning, shuffled-reward control, privileged oracle diagnostic. Actual probe cost is included in the score.
- Persistent native memory was serialized/restored within the same Python process. A cold **new-process** retention result is not established.
- Source-free toy development, not native Yggdrasil owner model learning; neither SCIENTIFIC_PASS nor deployment. Accepted `main`, CKAD, Wingless, other projects and controllers were untouched.
- Full exact-final-head Linux/Windows regression and G29 atlas companion must qualify separately before any engineering acceptance.

## Reproduce

From the pinned research branch on Python 3.12+:

```bash
python -B -m unittest discover -s research/contrib/chatgpt/YNCA-04 -p 'test_*.py' -v
python -B research/contrib/chatgpt/YNCA-04/experiment.py --dev
```

Heldout source was already consumed. Do not treat a fresh rerun as new evidence; original GitHub Actions artifacts and original result file are authoritative.

**Next falsifiable hypothesis:** Instead of learning a context-to-probe lookup, explicitly estimate causal identifiability and whether any available intervention has positive value given terminal goals. Compare with the strongest cost-aware no-probe and Bayesian baselines. No retuning of this consumed cohort.
