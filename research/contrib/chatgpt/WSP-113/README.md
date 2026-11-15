# WSP-113 — Online Causal Graph Weight Programming

**Research-only isolated draft. No original heldout transfer cohort has been consumed.** Stacked on [WSP-112 draft #1079](https://github.com/spoonman136668-ai/Yggdrasil/pull/1079), exact parent `e2b715b94ece9d42d228586a66117bbdaa18c4b9`, tree `c18bda074f41278c65982dd198a1903d12831d09`. The preregistration was frozen **before any WSP-113 implementation** as first commit `57c2cd7778d3a70d149350865f170dee73a9bc81`.

## Why this is a distinct gate

WSP-112's native learner and exhaustive Bayesian control implement equivalent full Boolean hypothesis inference, making an accuracy superiority claim inherently implausible. WSP-113 discards the Boolean truth-table hypothesis enumerator and instead *programs a six-edge causal adjacency structure* from observed action consequences. A forced intervention on one node propagates causally to later nodes. The model learns the graph itself, stores numeric float32 edge weights, and predicts unfamiliar interventions and multistep consequences after cold restoration.

The environment discloses four Boolean state nodes, their ascending topological order, the XOR causal-update law and the intervention grammar. Only **edge existence/composition** is hidden. This tests online causal graph assembly and retention, not discovery of unanticipated physical primitives, broad AGI, or direct dense neural-weight learning.

## Frozen task

- 128 completely observed training worlds (0–2 hidden edges), same 16 state inputs times eight interventions per world supplied equally to every learner.
- 128 distinct transfer worlds with 3–6 hidden edges absent from training. Every learner selects eight different queries from initial states 0–7 and interventions do(node 0–3, value 0–1).
- Heldout effects cover states 8–15 with all eight interventions: 64 unseen state/action outcomes per world, **8,192 four-bit transitions per arm**. Eight 3-step intervention trajectories per world assess rollout without additional training access.
- Hidden transfer graph identities and unqueried outcomes are inaccessible until **all** selected intervention transcripts, predictions and native checkpoint hashes have been sealed. No protected WSP-112 transfer evaluator is imported or reused.

## Comparison arms

The numeric direct writer's six float32 synapses are updated by a fixed generic GF(2) causal constraint solver. A separate independently coded symbolic solver and exact Bayesian model over **all 64 graphs**, each with its own active-query policy, are strong controls. A conventional fitted nonlinear kernel-ridge model uses the complete shared training world data and eight transfer observations. Random/passive interventions, zero memory, deliberately wrong edge binding and matched-action refits are negatives/ablations. Compare exact state accuracy, density subgroup performance, multistep trajectories, graph edges, cold retention and whole-process costs. Parity with strongest independent learner is **not** scientific superiority.

## Qualification and authority

Fabricated-label fixtures must pass on Windows and Linux first. The complete inherited WSP80–113 plus Yggdrasil root regression, followed by independent G29 acceptance, must pass on identical pinned source/tree **before** a single original synthetic DEV transfer run. Every extra validation cohort requires separate original-data custody and is not implicitly activated. Do not tune test worlds, thresholds, intervention policies or baselines after seeing original results.

Full training and evaluation code lives in `research/contrib/chatgpt/WSP-113/`. First-use-only evaluator command (not permitted before qualification):

    python research/contrib/chatgpt/WSP-113/experiment.py --frozen-dense-causal-graph-primary-dev

Fixture-only command (uses no original hidden oracle):

    python -m unittest discover -s research/contrib/chatgpt/WSP-113 -p 'test_*.py' -v

**No merge, accepted ref, model promotion, FORGE/Yggdrasil controller or scheduler change, private runner, paid API, protected historical source, Wingless/Hybrid integration, deployment, or automatic scientific acceptance.**

## One-shot generated-source qualification

The branch-scoped GitHub CI source-pin job is armed only by this exact commit message. It may update only the three mandatory G29-generated atlas artifacts after both platform fixtures pass; the scientific generator and learner files stay unchanged. The resulting generated-only companion commit then activates mandatory complete dual-platform regression, without running the original heldout experiment.

## Original DEV first-use fence

After the one-shot generated G29 commit, CI must pass the **entire** inherited and root regression on Linux and Windows and a separate two-platform independent G29 atlas job at the exact candidate HEAD. Only then, and only on the original non-rerun attempt, does the single new original synthetic 128-world transfer evaluation run. The original WSP112 heldout cohort is never accessed. This experiment never merges, deploys or declares SCIENTIFIC_PASS on its own.

## Final pre-first-use qualification source

The original G29 acceptance job itself passed all code-atlas tests but its strict clean-source guard failed on generated test bytecode. The repaired isolated G29 job disables Python bytecode generation while preserving all source and science constraints; the frozen scoring now reports per-node precision/recall and graph-edge precision/recall before original first-use. The stale prior candidate and its incomplete qualification are not eligible for original transfer. This new source pin must be accompanied by full exact-tree Linux and Windows regression and independent atlas acceptance.
