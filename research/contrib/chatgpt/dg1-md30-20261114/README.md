# DG1-MD30 — structural causal transfer preflight

**Status:** Research task implementation and synthetic negative-control fixtures only. No MD30 learner, trained baselines, DEV/cold/registered cohort evaluation, model integration, or scientific gain.

## Purpose

MD27–MD29 had no established novelty advantage over strong trained conventional controls. MD30 therefore tests a more demanding prerequisite: can a learner distinguish multiple causal graph explanations that generate **identical public observations**, require **opposite irreversible actions**, and can be separated only by **paid consequential diagnostics**? It also needs to detect a truly structural, unannounced change (parent-edge relocation and changed gate arity), rather than just flip an easy known polarity bit.

The fixture pairs two six-node Boolean causal DAGs. Before intervention they show exactly the same visible six-bit sensor vector, goal, actuator availability, cost menu, and empty charged history. Setting actuator B to 1 succeeds under the left graph; setting actuator A to 1 succeeds under the right graph. A physical diagnostic clamp on A distinguishes them while charging 0.05. The known-physics single-stage oracle scores **0.98** and a fixed blind action averages **0.23**, leaving **0.75** fixture headroom. These analytic values concern the deliberately constructed *fixture pair*, **not** the distributional quality of the later held-out benchmark or any learned policy.

## Physical semantics

- Six named binary sensor nodes A–F, two exogenous actuators, four DAG gates with optional inhibiting edges.
- Four motif families for synthetic physics checks: chain, fork, collider, composed. Synthetic fixture seeds do not overlap any official MD30 cohort.
- Each step is a **charged physical pulse** against the stage ambient roots. Its downstream consequences are directly observed. The pulse is released before the next action, so diagnostic interventions do not permanently rewrite the underlying ambient roots.
- Each of two stages permits at most three paid physical diagnostic clamps on A–E, then one obligatory actuator intervention on A or B; at most eight total world steps.
- Diagnostic costs 0.05. Actuator costs 0.02 and earns +1 for the requested terminal bit or −0.5 otherwise. No diagnostic earns terminal reward. A stage boundary may change the graph without returning a rewire indicator or hidden graph ID.
- All official MD30 seed ranges (training 1080001–1080768, development 2080001–2080128, cold 3080001–3080064, registered 4080001–4080256) fail closed under the fixture-only generator; MD29 reserved seeds 1070001–1070096 are also rejected.

## Qualification

Run the independent physics and negative-control tests with:

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-md30-20261114 -p test_structural_rewire.py -v
```

Cross-platform CI is defined in `.github/workflows/dg1-md30-qualification.yml` and additionally checks the untouched MD30 preregistration, pinned inherited CPU tests, committed G29 source atlas, and byte-identical fixture receipt.

## Unfinished mandatory gates

This preflight **does not** establish that the eventual task family is information-identifiable, sufficiently challenging, and compositional across training/heldout graphs. The next source-locked addendum must freeze the exact official family generator and motif split, graph/permutation hashes, rewiring schedule, trained control capacities/convergence, candidate hyperparameters, shared physical training trajectories, compute budget, and first-use guard. Independent oracle-vs-blind headroom must then pass **across the frozen distribution**, not just the pair above. Only after all controls are qualified and separately authorized may the disjoint scientific first-use occur. Preserve preregistration and any later null outcomes; never post-result tune.
