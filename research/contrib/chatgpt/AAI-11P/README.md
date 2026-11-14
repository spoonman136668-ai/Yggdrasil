# AAI-11P — harder, identifiable causal task with fully trained conventional controls

Independent *new benchmark* branch based directly on frozen Yggdrasil `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, not a modification of the AAI-10C learner. The protocol was **frozen before code** at commit `c74de47446bcd14923c0b1d95db8119d96ed6b81` in `prereg.json`.

## Why this benchmark

The earlier AAI-10D fixture headroom check [run 43637988498](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43637988498) found the AAI-10C learner was 0.63125 reward *below* the strongest conventional, with oracle headroom only 0.121875 (<0.15). It would have been irresponsible to consume the reserved science cohorts on such a small near-saturated problem. AAI-09A and AAI-10A/10B negatives remain frozen and unreplayed. Faster source-only computation is not a scientific learning gain.

This new six-bit world has 64 public inputs, 3 mediator outputs, 8 public goals, 12 set-bit interventions and up to two persistent actions per episode. Its six different hidden structural laws make m2 depend on composed nonlinear functions of m0/m1 and other input bits. A/B are familiar training laws; C/D/E/F are unfamiliar recombinations. The simulator knows the law; **none of the conventional controls receives that law or source formula**. A learner sees only actual public input/mediators/goal/reward/action count, and receives feedback only for the *do-action it actually took*. This is a finite causal mechanism-transfer test, not an open-world AGI benchmark, a new native model or a claim about general intelligence.

## Fully trained controls and admissibility

All **eight eligible conventional models** train on identical 16 A + 16 B one-action trials (64 common public pre/post rows) and 2 or 4 common one-action challenge trials in an unfamiliar law, after which they take at most two actual self-selected do-actions with real consequence feedback. Models include all-history and recency-16 Beta tabular, all-history and recent-32 k-nearest-neighbor, all-history and recent-16 45-hypothesis pairwise grammar posterior, deterministic ID3 depth-4 tree, and a 42-feature triple-interaction logistic regression fitted for 160 full-batch epochs at the public checkpoint, with eight online SGD steps per later observed row. All use **the same deterministic two-action public-information planner**. Oracle from true hidden equations is **diagnostic only**, never a learner/baseline. Public state includes current actual mediator readings, and STOP uses the actual public reward, not an imagined value.

**Frozen mechanical source-only admission:** Precisely three `mechanical:alpha/beta/gamma` fixture strings, 12 unique x/goal contexts per law, four unfamiliar C/D/E/F laws and N=2,4. Select strongest fully trained conventional by its own C/D/E/F aggregate reward. Require oracle minus strongest **>=0.25** overall and **>=0.10 per fixture**, plus best conventional familiar A/B mean reward **>=1.70**. Before scoring, every law pair must be one-step do-action distinguishable from every input; each law must admit helpful consequential intervention on at least 20% of input-goal cases. Failures are preserved as `BENCHMARK_INADEQUATE_NO_SCIENCE` without editing thresholds, equations or rerunning consumed cohorts. This admission is a deterministic **synthetic development diagnostic**, not scientific first use or statistical transfer-gain evidence.

A future unconventional candidate would require a **new separate preregistration**, capacity-matched strongest conventional controls, cold retention, information parity, negative controls and whole-process resource cost. Only **separate explicit scientific first-use authorization** could allow any future science trial; no autonomous script or workflow here can consume cohorts.

## Isolation and provenance

New science-world DEV 994000–994015, TRANSFER 995000–995063, NEGATIVE 996000–996031 are **reserved and untouched**. This repository branch's CLI has no science experiment API: `--primary` fails closed and the only permitted synthetic data labels are the three `mechanical:` fixture strings. No model-source edits, native Yggdrasil/Wingless/Hybrid change, FORGE loop, scheduler, controller, queue, runner installation, accepted reference, merge, deployment, paid API or user ChatGPT Library files.

Qualification evidence and candidate commits live only on GitHub. Standard generated G29 `.ice/code-atlas.*` files must be refreshed and exact-head full Linux/Windows repository regression run before saying engineering final PASS.
