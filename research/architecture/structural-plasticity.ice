TITLE: Structural Plasticity Constraints
DATE: 2026-09-17
STATUS: ADOPTED FOR DESIGN / NOT YET IMPLEMENTED
TRACK: DG-1C / DG-1D / DG-1E / DG-1F
CONFIDENCE: SUPPORTED

QUESTION
How should Yggdrasil eventually permit neural growth without allowing uncontrolled capacity expansion or disguising ordinary dynamic architecture search as developmental intelligence?

CORE PRINCIPLE
Growth is not intrinsically beneficial. A developmental organism is resource-credible only if the mechanisms that add structure are paired with mechanisms that can reduce, consolidate, hibernate, or merge structure under explicit hard limits.

EXTERNAL EVIDENCE
Recent adaptive-architecture work reports that online structural growth can improve task adaptation, while growth without pruning can produce orders-of-magnitude larger structures containing many low-value connections. Developmental continual-learning systems likewise identify uncontrolled expansion as a concrete failure mode.

YGGDRASIL INTERPRETATION
Every structural operation must be treated as a resource transaction with measurable benefit and bounded cost.

STRUCTURAL OPERATIONS
REPLICATE
Create a new cell/module instance derived from an existing or seed representation.

DIFFERENTIATE
Change a cell/module's functional role or parameters without necessarily increasing count.

CONNECT
Add a communication or computation edge.

DISCONNECT
Remove/deactivate an edge.

MERGE
Consolidate two or more structures into one retained structure when functional equivalence/reuse supports it.

HIBERNATE
Remove a structure from active compute while retaining enough information to reactivate it cheaply.

WAKE
Return hibernating structure to active compute.

PRUNE
Delete structure judged no longer worth its resident/active cost.

REPAIR
Modify surviving structure to recover lost function.

REGENERATE
Reconstruct missing useful structure from genome + permitted compact persistent state + current context.

MANDATORY CONTRACT FOR EVERY OPERATION
Before an operation is enabled in an experiment, define:
- TRIGGER: measurable condition that permits the operation;
- LOCAL INPUTS: information available to the decision mechanism;
- COST: active compute, memory, communication, and development cost;
- HARD LIMIT: maximum population/edges/bytes/operations;
- TELEMETRY: what is recorded when operation fires;
- FAILURE BEHAVIOR: what happens if capacity is exhausted or action destabilizes function;
- REVERSIBILITY: whether and how the action can be undone;
- AUTHORITY: whether the action is genuinely local/shared-rule or depends on a centralized controller.

GROWTH RULE
No REPLICATE/CONNECT mechanism may be introduced without at least one paired capacity-reduction mechanism available in the same experimental family:
- PRUNE;
- DISCONNECT;
- HIBERNATE;
- MERGE;
- bounded replacement under fixed population.

HARD LIMITS
Soft penalties never replace hard limits.
Every structural-growth experiment must enforce declared maxima for relevant quantities:
- cell/module count;
- edge count;
- resident bytes;
- active bytes/parameters;
- communication per development step;
- total development steps;
- wall-clock or energy proxy where practical.

EARLY SAFE FORMS
Before open population growth, prefer bounded structural plasticity:
1. fixed maximum population with alive/dead occupancy;
2. fixed node set with mutable edges;
3. fixed module slots with ACTIVE/HIBERNATING/EMPTY states;
4. birth only when an unused slot exists;
5. replacement only when resource accounting proves no net ceiling violation.

These forms allow developmental decisions to be studied without unbounded memory allocation.

LOCALITY TEST
A mechanism qualifies as local developmental structural plasticity only if each structural decision can be computed from:
- the cell/module's own state;
- declared neighboring messages/local graph context;
- optional globally broadcast scalar resource price or task signal when explicitly permitted.

A centralized planner that observes the full phenotype and emits arbitrary topology is a baseline/controller architecture, not automatically a Yggdrasil cell rule.

GLOBAL SCALARS
Global scalar signals may be scientifically useful without invalidating local execution. Examples:
- total resource price;
- remaining capacity fraction;
- global task reward/loss during training;
- damage alarm scalar.
Use must be explicit because global signals change the decentralization claim.

RESOURCE PRESSURE
Candidate local structural utility score:
U_i = estimated_functional_value_i - alpha * active_cost_i - beta * resident_cost_i - gamma * communication_cost_i.

This is not yet an accepted training equation. It is a design family.

Possible triggers:
REPLICATE if local novelty/error/value pressure exceeds threshold and capacity is available.
PRUNE/HIBERNATE if sustained utility remains below threshold and removal passes safety gate.
MERGE if two modules are functionally redundant under a declared similarity + intervention test.
WAKE if demand matches retained capability and wake cost is lower than regeneration/relearning alternatives.

ANTI-COLLAPSE CONDITIONS
Prevent trivial solutions:
- ALL-GROW: hard ceilings + resource penalties + matched growth-only control.
- ALL-PRUNE: minimum task-performance constraints and hysteresis.
- RAPID THRASHING: operation cooldown/hysteresis and switching-cost telemetry.
- CENTRALIZED ROLE ASSIGNMENT: locality audit.
- UNUSED STRUCTURE RETENTION: resident-cost accounting even for inactive modules unless truly externalized/archived.

GROWTH / PRUNE EXPERIMENT DESIGN
For each adaptive-structure experiment compare at least:
A. fixed architecture;
B. growth only;
C. pruning only where meaningful;
D. growth + pruning/hibernation;
E. same active-capacity ceiling with conventional dynamic architecture baseline where practical.

MEASURE
- task performance;
- total capacity trajectory;
- resident capacity trajectory;
- active capacity trajectory;
- births/deaths/hibernations/wakes per interval;
- average lifetime of structures;
- reuse frequency;
- churn rate;
- communication cost;
- latency;
- recovery from structural damage;
- capability retained after pruning.

FUNCTIONAL VALUE TEST
A structure's value must not be estimated only from weight magnitude or activation magnitude.
At least one causal/behavioral proxy should be available before targeted pruning claims are trusted:
- ablation delta;
- task-conditioned contribution;
- routing dependency;
- recovery dependency;
- counterfactual replacement test.
Cheap heuristics may trigger candidate pruning but should be validated periodically against causal measures.

SPECIALIZATION RELATION
DIFFERENTIATION and structural plasticity are separate axes.
A cell may differentiate without topology growth.
A system may grow without useful differentiation.
Yggdrasil succeeds only when structure changes correlate with useful functional division of labor, reuse, retention, or repair.

HIBERNATION VS ARCHIVAL VS REGENERABLE
ACTIVE: resident and participating in current compute.
HIBERNATING: resident compact state remains and wake is cheap.
ARCHIVED: full or near-full phenotype stored outside active/resident fast memory.
REGENERABLE: full phenotype absent; compact persistent information plus development recreates function.
PRUNED: no guarantee of recoverability beyond general relearning/development.

These states must have distinct byte and latency accounting.

FAILURE CONDITIONS
- active or resident structure grows without bound;
- growth-only variant performs similarly but uses much more capacity, yet no compaction mechanism works;
- resource accounting omits inactive resident structures;
- structural controller becomes effectively centralized despite local-development claim;
- pruning causes repeated relearning of the same capability without net resource advantage;
- operation churn dominates useful compute;
- theoretical sparsity does not translate to measurable resource reduction on target hardware.

DECISION
DG-1A and the first DG-1B functional experiments will not use open-ended population growth.
Structural plasticity enters only after the fixed-population developmental substrate and functional-regeneration measurements are stable.
When it enters, growth and compaction must be tested together under hard ceilings.

OPEN QUESTIONS
- Which local utility signal is sufficient to trigger useful differentiation/growth without global architectural search?
- Is HIBERNATE more practical than PRUNE for early continual-learning experiments?
- Can a fixed maximum population with slot reuse demonstrate the important developmental effects before true dynamic allocation?
- What hardware-visible sparse structure yields real speed/memory gains on consumer GPUs?

NEXT EXPERIMENT
After DG-1B-P1/P1G, introduce a bounded graph with fixed maximum nodes and mutable alive/edge state. Test fixed architecture versus growth-only versus growth+prune under identical hard capacity ceilings.

PROVENANCE
- Jia et al. Self-motivated growing neural network for adaptive architecture via local structural plasticity. Neurocomputing, 2026, S092523122601979X.
- Ding et al. A structural developmental neural network with information saturation for continual unsupervised learning. CAAI Transactions on Intelligence Technology, 2023.
- Continual learning of multiple cognitive functions with a brain-inspired temporal development mechanism. National Science Review, 2026.
- Evci et al. Rigging the Lottery: Making All Tickets Winners. ICML, 2020.
- MetaNCA. arXiv:2607.07743, 2026.