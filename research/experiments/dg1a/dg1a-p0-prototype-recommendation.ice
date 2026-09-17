TITLE: YG-R7 — First Prototype Recommendation
DATE: 2026-09-17
STATUS: READY FOR BOUNDED IMPLEMENTATION
TRACK: DG-1A -> DG-1B/D
CONFIDENCE: SUPPORTED AS FIRST EXPERIMENT

QUESTION
What first implementation gives the highest-confidence developmental signal per unit engineering and compute?

RECOMMENDATION
Use a two-step prototype rather than jumping directly to pretrained models.

STEP 1 — DG-1A-P0 CANONICAL NCA REPRODUCTION
Purpose:
Validate the cell/update implementation, training stability, randomized developmental horizon, damage injection, and telemetry against an understood developmental system.

Task:
Grow and maintain a small 2D target morphology from a seed, then recover after structured damage.

Recommended implementation characteristics:
- Python + PyTorch unless existing repository constraints later justify another stack
- 2D grid
- 16-32 channels per cell
- fixed 3x3 neighborhood
- one shared update network
- residual updates
- randomized update step count during training
- stochastic firing option matching canonical NCA behavior
- explicit alive/activity masking
- small target images generated or vendored in a reproducible way

Required variants:
A. GROWTH ONLY
B. PERSISTENCE TRAINING
C. DAMAGE/REGENERATION TRAINING

Required damage protocols:
- random rectangular lesion
- random cell dropout/erasure
- central lesion or task-relevant lesion

Required outputs:
- machine-readable run config
- loss curves
- target error before/after damage
- recovery curve over development steps
- active cell count over time
- update-rule parameter count
- peak RAM/VRAM when measurable
- timing per developmental step
- deterministic seed metadata

P0 SUCCESS CONDITION
- at least one small target reliably grows from seed across multiple random seeds;
- persistence-trained model remains stable over a longer horizon than growth-only control;
- damage-trained model recovers target function/morphology materially better than growth-only control after the same lesion;
- telemetry is reproducible and sufficient for P1.

P0 FAILURE CONDITION
- numerical instability persists after validated implementation and bounded hyperparameter search;
- damage has no measurable effect, making regeneration metric meaningless;
- recovery result depends on restoring a saved pre-damage state;
- instrumentation cannot distinguish active cells, retained state, and recomputation.

STEP 2 — DG-1B/D-P1 FUNCTIONAL REGENERATION
Begin immediately after P0 is stable. This is the first Yggdrasil-specific scientific probe.

PRIMARY TASK RECOMMENDATION
Distributed shape classification with local consensus, beginning with synthetic connected glyphs/shapes and then an MNIST-style self-classification task.

Why this task:
- known evidence exists that NCA can perform distributed classification;
- cells must integrate non-local shape information through local communication;
- damage can impair both information propagation and computation;
- recovery can be measured functionally rather than visually;
- compute requirements are small enough for CPU/8 GB GPU research.

P1 CELL STATE
Suggested 24-channel starting point:
- immutable input/liveness channel(s)
- 8 communication channels
- 8 private state channels
- output/class channels sized to the chosen task
Adjust width only through declared sweeps.

P1 TRAINING
Train local shared update dynamics to reach distributed classification consensus after a randomized number of developmental steps.

Variants:
1. no damage exposure
2. random damage exposure
3. targeted damage exposure after influence metric exists

Damage acts on mutable cell state and/or live cells. Immutable task input corruption must be a separate experiment because that changes the task evidence rather than only damaging the organism.

P1 FUNCTIONAL METRICS
- global classification accuracy
- per-cell agreement
- time to consensus
- immediate post-damage accuracy/agreement
- recovered accuracy/agreement
- steps to 50%, 90%, and 95% of pre-damage performance where attainable
- run-to-run variance

P1 RESOURCE METRICS
- active cells over time
- active parameters
- resident state bytes
- communication operations/messages proxy
- development steps
- wall-clock recovery latency

P1 BASELINES
B0: same NCA architecture, no damage training.
B1: damage-trained NCA.
B2: recurrent local convolution/message-passing model with comparable shared parameter budget but without developmental alive/repair behavior where feasible.
B3: fixed classifier matched for approximate parameter budget as a task-performance reference, not as a regeneration-equivalent model.

P1 SUCCESS CONDITION
Evidence for functional developmental regeneration requires all of:
- task accuracy above predeclared threshold before damage;
- damage creates a statistically meaningful functional drop;
- damage-trained developmental model recovers materially more function than B0 under identical damage;
- recovery occurs without loading a saved full phenotype;
- the result survives multiple random seeds;
- recovery cost and retained-state cost are reported.

P1 DOES NOT YET PROVE
- emergent specialization
- continual learning
- sublinear capability growth
- ancestor inheritance
- usefulness around a language model
- general intelligence

FOLLOW-ON IF P1 PASSES
DG-1C-P2:
Introduce two to four task families and test whether cell roles specialize under task demand.

Then DG-1D-P3:
Target the most functionally important cells/clusters and quantify regeneration.

IMPLEMENTATION SHAPE
Suggested initial repository layout once implementation begins:
experiments/
  dg1a/
    configs/
    run.py
  dg1b/
    configs/
    run.py
src/
  yggdrasil/
    cells.py
    nca.py
    damage.py
    metrics.py
    resources.py
tests/
  test_cells.py
  test_damage.py
  test_metrics.py
evidence/
  generated run artifacts only

Narrative experiment interpretation remains in .ice under research/experiments/.

TEST DISCIPLINE
- Never disable, skip, or comment out failing unit tests.
- Fix root causes rather than weakening assertions merely to pass a feature.
- Numerical tolerances must be justified by the computation, not enlarged until green.

DECISION
DG-1A-P0 is the recommended first implementation. It is intentionally small. Its job is to make the developmental substrate trustworthy. DG-1B/D-P1 is the first decisive probe of whether that substrate can recover useful computation rather than only reconstruct pictures.

NEXT ACTION
Implement only the bounded P0 infrastructure and experiment first. Do not add module cells, ancestor inheritance, pretrained seeds, or open-ended structural growth in the same implementation step.

PROVENANCE
- Mordvintsev et al., Growing Neural Cellular Automata, Distill 2020, DOI 10.23915/distill.00023.
- Randazzo et al., Self-classifying MNIST Digits, Distill 2020, DOI 10.23915/distill.00027.002.
- Najarro et al., Towards Self-Assembling Artificial Neural Networks through Neural Developmental Programs, arXiv:2307.08197.
