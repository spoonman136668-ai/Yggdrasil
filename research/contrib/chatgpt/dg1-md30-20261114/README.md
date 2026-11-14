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

## MD30 six-motif distribution gate (next pre-first-use milestone)

The initial LEFT/RIGHT fixture above intentionally permits a root diagnostic to
prove charged-action bookkeeping. That fixture alone was **too easy to count as
a substantive learning challenge**: probing an actuator root previews the
irreversible choice. This is explicitly **not** the new transfer task.

The newer source-locked distribution uses `structural_catalog.py` and the
pre-first-use `task_generator_lock.json`:

- **Train topology classes:** chain, fork, collider (six fixed parent-edge
  templates, two per motif).
- **Novel transfer classes:** braided, crossfork, doublecollider (six different,
  composition-disjoint parent-edge templates).
- Gate/inhibition variants are deterministically selected using SHA-256,
  with a graph-pair construction requiring *identical ambient six-bit
  observations*, opposite winning irreversible interventions, changed parent
  structure **and** gate, plus at least one physically identifying clamp.
- Crucially, official challenging tasks expose diagnostics **only at internal
  nodes C, D and E**. Clamping actuator A or B as a cheap action preview is
  rejected; the public action menu advertises the permitted nodes.
- The original cohorts have **not** been generated. `synthetic_pair`
  rejects seeds >=1,000,000 and only 48 synthetic preflight seeds
  (1201–1248) per motif are used to inspect task construction.
- The official four cohort ranges, motif allocation, change schedule,
  allowed physical actions, and graph-topology SHA commitments are **declared
  and frozen** in the lock file, but remain execution-disabled.

The synthetic distribution check uses a **motif-aware blind fixed-actuator**
comparator and a privileged physics oracle. This is a task-difficulty
sanity check, **not a policy evaluation** and not proof Yggdrasil beats a
trained conventional learner. Any actual learner or trained control has to
consume the same paid observations, work under identical action/compute
budgets and obey the independent registered first-use gate.

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-md30-20261114 -p test_structural_catalog.py -v
```

**Stop conditions:** mixed hidden graphs becoming publicly distinguishable
without a paid diagnostic; train/transfer topology overlap; headroom below
0.35 in any motif; failures of cross-OS determinism or inherited regression;
or a strong conventional trained controller already saturating this task. The
last condition is **unverified** until conventional baselines are implemented
and trained, and cannot be waived by successful synthetic preflight.

## Conventional causal filter — synthetic control qualification

The next step implements a **standard, explicitly non-novel** Bayesian
causal-response filter in `bayesian_control.py`. It is a *control* against
which the later unconventional learner must compete, not an intelligence
achievement on its own.

- Source prior: 768 distinct observable response hypotheses, drawn from a
  universal seeded six-node binary-DAG grammar rather than from privileged
  hidden episode graphs. The policy has no seed, motif label, graph object,
  lookahead environment clone or future-action access.
- Training: 240 previously unused **synthetic** train-motif episodes, seeds
  3301–3540, with 1,920 charged world actions. Every stage produces three
  paid internal diagnostic responses and one actual physical actuator
  consequence. Training fits a graph prior for three preregistered
  expectation-maximization passes.
- Adaptation: a conventional posterior filter scores observed public
  sensor/action receipts, and carries an explicit 50% change-point mixture
  after the first irreversible act. The action planner evaluates its **own
  learned hypotheses** to determine if one additional diagnostic is worth
  its physical cost; a real action is never simulated for free.
- Synthetic diagnostic-only transfer: seeds 5301–5360 from the three
  unseen motif classes; the separate fixed-actuator comparator gets a new,
  independently paid episode per matched seed.
- Negative controls: no official seed access; source-locked data and
  budget checks; cross-platform graph-model and physical-receipt parity;
  immutable original preregistration; mandatory full inherited regression.
  Model fitting and toy evaluation are *not* registered original scientific
  first-use.

A model that beats a fixed blind action is **not enough** to establish a
strongest conventional baseline, scientific improvement or AGI. The remaining
mandatory work includes sufficiently trained recurrent and model-based RL
controllers, matched online physical information and compute, heldout
nonregression, cold retention, and separately authorized original science.
Preserve all null/negative results; do not change frozen parameters after
observing synthetic transfer diagnostics.

## New conventional controls (MD30, frozen before source)

The independent `conventional_controls_lock.json` was committed before
`recurrent_control.py`, `model_rl_control.py`, and any new-model toy results.
Both controls receive the same existing 240 charged training episodes
(1,920 total physical actions), with a fixed chronological 192-episode fit
/ 48-episode validation split. Evaluations use only the already declared
60 synthetic transfer seeds. These are **not** MD30 official or registered
scientific first-use cohorts.

- **Recurrent world model:** A conventional fully trainable 16-input,
  32-hidden, 6-output Elman recurrent neural network (1,766 trainable
  scalars), fitted with full eight-step BPTT and Adam. Its input combines
  a physical-action one-hot, preceding observed six-bit sensor vector,
  and public stage. Validation-best selection is restricted to the 48
  charged training-holdout episodes, with fixed 80-epoch maximum and
  12-epoch patience. The policy may simulate only its own learned dynamics,
  never free `World.step` calls or actual graph lookahead.
- **Empirical model-based RL:** Fits a conventional categorical MDP
  transition and terminal reward model from *the same* paid public
  experiences. The state includes the public stage and sensed C/D/E/F
  bits; the model interpolates empirical state-action frequencies with
  a frozen phase/action backoff. A Bellman information-value backup
  can choose up to one paid internal diagnostic before a physical
  irreversible actuator choice. A disjoint 48-episode validation split
  reports categorical log-loss.
- **Qualification:** `test_conventional_controls.py` enforces fully
  trainable recurrent weights, data-custody limits, model loss/parameter
  sanity, valid physical action menus, no private-graph access, official
  seed fences, and equal physical training. The CI workflow runs both
  conventional controls on Windows and Linux and compares all portable
  model/checkpoint/action receipts on the exact committed SHA.

These conventional controls are a **development benchmark**. A passing
training test alone does not prove they are the *strongest* recurrent or RL
baseline, matched whole-process compute, intelligence improvement, or
scientific superiority. Numeric performance, full CI and cross-OS parity
must be reported from the actual run, including failures. Do not retune
frozen hyperparameters after seeing synthetic transfer outcomes.

## Native persistent causal tournament — frozen synthetic comparison

The native candidate in `native_tournament.py` was preregistered in
`native_tournament_lock.json` at commit
`242dd9f6c46ca895ec5a7e279a975ea5e980b087` **before** candidate
source or numerical results. It is an independent non-token, non-gradient,
persistent physical hypothesis-tournament research mechanism, not a
reimplementation of the conventional Bayesian probability filter.

- It **shares** the existing 768 universal response signatures with the
  Bayesian control (same hypothesis information; no privileged real
  episode graph). It learns *integer* match/contradiction credits from
  exactly the existing 240 physically charged training episodes. All
  learners receive the same action consequences, and it never observes
  a private graph, seed, change flag or future.
- Its protected two-bank memory keeps stage-0 and stage-1 explanatory
  hypotheses separately. At a possible unannounced graph change, it
  recalls the stage-1 bank, preserves earlier high-ranking hypotheses
  and reopens alternatives contradicted by paid observations. The
  bounded 32-hypothesis active tournament votes on irreversible actions
  and chooses an internal diagnostic only when its own expected gain
  exceeds the *actual* 0.05 physical charge.
- Two separately frozen ablations test (a) no persistent trained
  credits and (b) no stage-specific change-aware bank. Cold checkpoint
  restoration must reproduce identical physical action/reward traces.
- The already-observed synthetic 5301–5360 cohort is used for
  reproducibility **only**. The separately frozen **new synthetic**
  6301–6360 cohort gets a one-shot paired, full-action-cost comparison
  with all three tournament arms, the previously frozen Bayesian
  controller and fixed action A. Per-motif comparisons and actual
  charged physical action counts are retained.
- These cohorts are not the official MD30 DEV, cold, or registered
  first use. Passing engineering tests does **not** confer
  `SCIENTIFIC_PASS`; a positive or null result is retained without
  changing thresholds, training rules, or controls after outcomes.

Qualification runs the new focused negative controls plus the complete
54-test inherited suite on Windows and Linux, source-pinned G29 atlas
acceptance and byte-identical action, memory and checkpoint parity.
The branch remains draft and isolated from Yggdrasil main/native weights.
