TITLE: YG-R8 — Developmental Intelligence Gap-Closure Study
DATE: 2026-09-17
STATUS: ACTIVE — PASS 1 COMPLETE
TRACK: DG-1
CONFIDENCE: SUPPORTED

QUESTION
What recent evidence and adjacent architectures materially change Yggdrasil's first experiments, and what gaps must be closed before substantial implementation?

SCOPE
This pass targets six gaps:
1. functional regeneration;
2. graph/topology generalization;
3. cell differentiation and functional specialization;
4. growth/pruning structural plasticity;
5. continual specialization and compact expansion;
6. resource and developmental-cost measurement.

EVIDENCE CLASSIFICATION
MEASURED YGGDRASIL RESULTS: NONE.
SIMULATED YGGDRASIL RESULTS: NONE.
ESTIMATED YGGDRASIL RESULTS: NONE USED AS CONFIRMATORY EVIDENCE.
EXTERNAL PUBLISHED RESULTS: USED AS DESIGN EVIDENCE ONLY.
YGGDRASIL ARCHITECTURAL CLAIMS BELOW: HYPOTHESES OR RECOMMENDATIONS UNLESS EXPLICITLY MARKED OTHERWISE.

OBSERVATION YG-R8-OBS-001 — SELF-ASSEMBLING NEURAL DEVELOPMENT IS NOW A DIRECTLY RELEVANT FIELD
STATUS: OBSERVED
EVIDENCE:
Najarro's 2026 thesis, Self-Assembling Intelligence: Self-Organisation, Development, and Control in Artificial Neural Systems, consolidates work on decentralized growth, local learning, indirect encodings, and Neural Developmental Programs in which identical cells communicating locally construct neural systems.
ANALYSIS:
This reduces uncertainty that Yggdrasil's developmental framing is technically coherent, but it also raises the bar: Yggdrasil must distinguish itself through continual development, resource pressure, regeneration, and inherited capability rather than merely demonstrating that a network can be grown.
CONFIDENCE: SUPPORTED.

OBSERVATION YG-R8-OBS-002 — LOCAL DEVELOPMENTAL RULES CAN ORGANIZE FUNCTIONAL WEIGHTS ACROSS ARCHITECTURES
STATUS: OBSERVED
EVIDENCE:
Architecture Generalization with MetaNCA (2026) introduces a graph-based Neural Cellular Automata approach that self-organizes neural-network weights and reports generalization to architectures not seen during meta-training, with architectural diversity during training strengthening generalization.
ANALYSIS:
This is highly relevant to Yggdrasil's genome/phenotype distinction. A developmental rule need not be tied to a single fixed grid phenotype. Graph-local weight development should therefore move earlier in the roadmap, after the canonical NCA reproduction establishes implementation correctness.
CONFIDENCE: SUPPORTED AS EXTERNAL RESULT; YGGDRASIL TRANSFER UNKNOWN.

OBSERVATION YG-R8-OBS-003 — FUNCTIONAL SELF-ORGANIZATION CAN TARGET LOGIC, NOT JUST SHAPE
STATUS: OBSERVED
EVIDENCE:
Self-Organising Digital Circuits (2026) frames functional logic generation and maintenance as a graph self-organization problem. A learned topology-aware local policy configures Boolean gate lookup tables to satisfy computational tasks rather than merely reconstructing a fixed image.
ANALYSIS:
This directly supports the decision to separate functional regeneration from visual morphology. It also suggests a useful future DG-1B benchmark family: small Boolean circuits or graph-structured logic tasks where functional equivalence admits many valid phenotypes.
CONFIDENCE: SUPPORTED.

OBSERVATION YG-R8-OBS-004 — DECENTRALIZED IDENTICAL MODULES CAN CLASSIFY GLOBAL STRUCTURE AND RESPOND TO DAMAGE
STATUS: OBSERVED
EVIDENCE:
Smart cellular bricks for decentralized shape classification and damage recovery, Nature Communications (2026), demonstrates a physical modular system in which each module executes the same neural network, uses local communication without global state or position, collectively infers global shape class, and supports damage-related behavior.
ANALYSIS:
Yggdrasil should preserve a strict decentralization test for early functional experiments: no privileged global controller state may be silently added to make local cells succeed. Global loss during training is acceptable as a training signal; global privileged state at phenotype execution is a separate design choice and must be declared.
CONFIDENCE: ESTABLISHED FOR THE PUBLISHED SYSTEM; YGGDRASIL GENERALIZATION UNKNOWN.

OBSERVATION YG-R8-OBS-005 — REGENERATION HAS MECHANISTIC DYNAMICS WORTH MEASURING
STATUS: OBSERVED
EVIDENCE:
Structured Fluctuations and the Information Dynamics of Self-Maintenance in Growing Neural Cellular Automata (2026) reports structured internal fluctuations, collective attracting dynamics, damage-response analysis, information-flow measurements, and distributed small updates associated with recovery.
ANALYSIS:
Yggdrasil should not reduce regeneration telemetry to endpoint accuracy. Early experiments should capture the recovery trajectory, time to recovery thresholds, state-space convergence proxies, spatial/local response to damage, and whether repair activity remains localized or system-wide.
CONFIDENCE: SUPPORTED.

OBSERVATION YG-R8-OBS-006 — CELL DIFFERENTIATION CAN EMERGE IN LATENT STATE, BUT FUNCTION MUST BE CAUSALLY VALIDATED
STATUS: OBSERVED
EVIDENCE:
Transient State Reorganization and Cell Differentiation in the Developmental Dynamics of Growing Neural Cellular Automata (2026) studies developmental trajectories and reports identifiable cell-state types, including transient early communities and more stable differentiated states associated with mature spatial regions.
ANALYSIS:
Latent clustering alone is not sufficient evidence for Yggdrasil's 'organs'. DG-1C must require functional correlation and intervention: task affinity, ablation sensitivity, communication dependence, or measurable contribution to output/recovery.
CONFIDENCE: SUPPORTED FOR DIFFERENTIATION PHENOMENA; FUNCTIONAL SPECIALIZATION CLAIM REMAINS UNPROVEN.

OBSERVATION YG-R8-OBS-007 — GROWTH WITHOUT PRUNING IS A KNOWN RESOURCE FAILURE MODE
STATUS: OBSERVED
EVIDENCE:
Self-motivated growing neural network for adaptive architecture via local structural plasticity (2026) studies online topology growth and pruning. Reported ablations indicate growth can improve adaptive performance, while removing pruning permits much larger network expansion with many low-value connections.
Additional developmental/continual-learning literature reports uncontrolled neuron splitting or expansion as a concrete limitation when structural growth lacks effective size control.
ANALYSIS:
Yggdrasil must never evaluate replication/growth independently of a paired death/prune/hibernate mechanism and hard population/resource ceilings. 'Can grow' is not success. Controlled capacity is part of the task.
CONFIDENCE: SUPPORTED.

OBSERVATION YG-R8-OBS-008 — DEVELOPMENTAL GROWTH/PRUNING IS RELEVANT TO CONTINUAL LEARNING, BUT NOT PROOF OF YGGDRASIL'S THESIS
STATUS: OBSERVED
EVIDENCE:
Recent continual-learning systems use dynamic growth, pruning, adapters, routing, or hypernetwork-generated task parameters to reduce interference and reuse existing capacity. Examples include task-conditioned hypernetwork/PEFT systems, dynamic adapter composition, and brain-inspired temporal growth/pruning approaches.
ANALYSIS:
These establish strong conventional competitors. If Yggdrasil later obtains retention merely by allocating a new module per task, it has not demonstrated a developmental advantage. Required comparisons must include static adapters, adapter routing, hypernetwork generation, and dynamic modular expansion.
CONFIDENCE: SUPPORTED.

OBSERVATION YG-R8-OBS-009 — ARCHITECTURE-AGNOSTIC DEVELOPMENT AND REGENERABLE FUNCTION ARE DISTINCT RESEARCH AXES
STATUS: OBSERVED / ANALYTIC CONCLUSION
EVIDENCE:
MetaNCA emphasizes architecture generalization. Self-Organising Digital Circuits emphasizes functional self-organization and maintenance. Classical Growing NCA emphasizes growth and regeneration. No reviewed result establishes the full combination required by Yggdrasil: architecture-flexible developmental generation + functional regeneration + continual specialization + resource-bounded growth + ancestor inheritance.
ANALYSIS:
Yggdrasil's novelty target should remain the conjunction, not any one ingredient.
CONFIDENCE: SUPPORTED AS LITERATURE SYNTHESIS.

RECOMMENDATION YG-R8-REC-001 — RETAIN DG-1A-P0 AS A CANONICAL IMPLEMENTATION CONTROL
STATUS: ADOPTED
RATIONALE:
The simplest grid NCA remains the fastest way to validate local shared update mechanics, damage injection, randomized development horizons, and deterministic telemetry against known behavior.
LIMIT:
P0 is not evidence for cognitive or functional development.

RECOMMENDATION YG-R8-REC-002 — MOVE GRAPH DEVELOPMENT EARLIER
STATUS: RECOMMENDED
RATIONALE:
After P0 and one bounded grid functional task, introduce a graph substrate before module/LoRA stages. Candidate benchmark: graph logic or circuit-style functional generation where many weight/configuration phenotypes can realize the same function.

RECOMMENDATION YG-R8-REC-003 — DEFINE FUNCTIONAL REGENERATION AS RECOVERY OF TASK PERFORMANCE, NOT STATE RESTORATION
STATUS: ADOPTED
REQUIREMENTS:
- damage must cause a statistically meaningful function drop;
- recovery must occur without loading a saved full phenotype;
- recovered function must exceed a matched no-repair/no-damage-training control;
- retained bytes/state and recomputation/development cost must be reported;
- endpoint equivalence must not require exact pre-damage hidden-state reconstruction.

RECOMMENDATION YG-R8-REC-004 — DEFINE SPECIALIZATION CAUSALLY
STATUS: ADOPTED
A cell type/cluster qualifies as functionally specialized only when at least one intervention-based measure links it preferentially to a task/function and the relationship replicates across seeds.
Candidate evidence:
- task-conditioned activation affinity;
- causal ablation delta;
- routing/communication centrality specific to a task;
- recovery contribution after targeted damage;
- reuse or transfer benefit on related tasks.
Latent clustering alone is descriptive, not sufficient.

RECOMMENDATION YG-R8-REC-005 — REQUIRE PAIRED GROWTH AND COMPACTION
STATUS: ADOPTED FOR LATER STRUCTURAL PHASES
Every REPLICATE/CONNECT operation must eventually have a paired pressure or operation capable of reducing active/resident structure: PRUNE, DISCONNECT, HIBERNATE, MERGE, or equivalent.
Hard population, memory, and communication ceilings remain mandatory even when soft resource penalties are used.

RECOMMENDATION YG-R8-REC-006 — EXPAND TELEMETRY BEFORE CLAIMING REGENERATION
STATUS: ADOPTED
Add:
- pre-damage performance;
- immediate post-damage performance;
- recovery curve;
- area under recovery curve;
- steps/time to declared recovery thresholds;
- fraction of mutable state destroyed;
- retained-state bytes;
- changed/reactivated cell fraction;
- communication/update cost during repair;
- state-space convergence proxy;
- localized versus distributed repair-response proxy.
Information-theoretic measures such as transfer entropy are exploratory because compute cost may be disproportionate on home hardware.

RECOMMENDATION YG-R8-REC-007 — SEPARATE FOUR CAPACITY NUMBERS
STATUS: ADOPTED
Every later modular experiment should distinguish:
1. GENOME PARAMETERS — persistent shared developmental rule/encoding;
2. RESIDENT PHENOTYPE PARAMETERS/BYTES — instantiated but not necessarily active structure;
3. ACTIVE PHENOTYPE PARAMETERS/BYTES — structure participating in current work;
4. REGENERATION COST — steps/FLOPs/time/energy proxy required to recreate unavailable phenotype.
Without this separation, 'compact AI' claims are uninterpretable.

RECOMMENDATION YG-R8-REC-008 — USE FUNCTION-PRESERVING PHENOTYPE EQUIVALENCE
STATUS: RECOMMENDED
Regeneration and inheritance should usually be judged by functional equivalence classes, not exact weights or cell states. Many different phenotypes may implement the same useful function. Exact-state restoration should be a diagnostic only where scientifically relevant.

HYPOTHESES CREATED BY R8
H-R8-1: A shared local graph-development rule can generalize across small computational topologies better than a topology-specific developmental rule.
STATUS: PLAUSIBLE.

H-R8-2: Training under damage will produce recovery dynamics that are measurably different from ordinary recurrent robustness, even at equal shared-parameter budgets.
STATUS: PLAUSIBLE.

H-R8-3: Functional specialization can emerge without assigning explicit cell types if task diversity plus resource pressure makes reuse and division of labor advantageous.
STATUS: SPECULATIVE.

H-R8-4: Growth paired with pruning/hibernation can produce slower active-phenotype growth than capability accumulation across sequential tasks.
STATUS: SPECULATIVE.

H-R8-5: For some capabilities, genome + compact persistent state + regeneration compute will be cheaper than permanent resident phenotype storage.
STATUS: SPECULATIVE.

WHAT R8 DOES NOT ESTABLISH
- that cellular development will outperform conventional modular networks;
- that ancestor capabilities can be compactly inherited;
- that active phenotype growth will be sublinear;
- that a developmental language-model system is practical;
- that local credit assignment will scale;
- that theoretical sparsity will produce wall-clock savings on commodity GPUs.

DECISION
The core Yggdrasil direction remains technically plausible and worth testing. R8 does not justify jumping to large pretrained models. It does justify refining the early experiment sequence so that morphology reproduction is immediately followed by functional recovery and then graph-based functional development.

UPDATED EARLY SEQUENCE
DG-1A-P0: canonical grid growth/persistence/regeneration reproduction.
DG-1B/D-P1: grid/local functional classification with controlled damage and recovery.
DG-1B-P1G: graph-based functional generation/maintenance benchmark.
DG-1C-P2: multi-task functional specialization with causal specialization metrics.
DG-1D-P3: targeted specialist damage and functional regeneration.
Only after those are stable should DG-1F module cells become the dominant substrate.

OPEN QUESTIONS
- Is a topology-masked attention/message-passing update still sufficiently local for Yggdrasil's developmental constraint?
- Which graph functional benchmark best separates developmental growth from ordinary message passing?
- Can differentiated roles survive permutation of physical position/topology?
- Does resource pressure induce useful reuse or merely degrade performance?
- What regeneration latency makes REGENERABLE preferable to COLD storage?
- How should equivalent functionality be tested for ancestor-derived capabilities?

NEXT EXPERIMENT
Complete the functional-regeneration protocol and measurement framework, reconcile the initial architecture decision, then implement only DG-1A-P0.

PROVENANCE
- Najarro, E. Self-Assembling Intelligence: Self-Organisation, Development, and Control in Artificial Neural Systems. PhD thesis, IT University of Copenhagen, 2026.
- Barot, Berenberg, Khajehabdollahi. Architecture Generalization with MetaNCA. arXiv:2607.07743, 2026.
- Barylli, Béna, Mordvintsev, Nisioti, Risi. Self-Organising Digital Circuits. arXiv:2608.02606, 2026.
- Smart cellular bricks for decentralized shape classification and damage recovery. Nature Communications 17, 2026, article s41467-026-75166-7.
- Structured Fluctuations and the Information Dynamics of Self-Maintenance in Growing Neural Cellular Automata. Entropy 28(8):893, 2026; arXiv:2607.12403.
- Transient State Reorganization and Cell Differentiation in the Developmental Dynamics of Growing Neural Cellular Automata. arXiv:2607.15726, 2026.
- Jia et al. Self-motivated growing neural network for adaptive architecture via local structural plasticity. Neurocomputing, 2026, article S092523122601979X.
- Najarro, Sudhakaran, Risi. Towards Self-Assembling Artificial Neural Networks through Neural Developmental Programs. Artificial Life Conference Proceedings, 2023; arXiv:2307.08197.
- Najarro et al. HyperNCA: Growing Developmental Networks with Neural Cellular Automata. arXiv:2204.11674, 2022.
- Araujo et al. Learning to Route for Dynamic Adapter Composition in Continual Learning with Language Models. Findings of EMNLP, 2024.
- Lv et al. HyperLoRA: Efficient Cross-task Generalization via Constrained Low-Rank Adapters Generation. Findings of EMNLP, 2024.
