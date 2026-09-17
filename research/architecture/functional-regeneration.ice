TITLE: Functional Regeneration Protocol
DATE: 2026-09-17
STATUS: ADOPTED FOR DG-1B/D DESIGN
TRACK: DG-1B / DG-1D
CONFIDENCE: SUPPORTED

QUESTION
What evidence is sufficient to claim that a developmental neural phenotype has regenerated useful function after damage?

DEFINITION
FUNCTIONAL REGENERATION = recovery of declared task capability after a controlled lesion through the system's own developmental dynamics, without restoring a saved full phenotype.

Functional regeneration does not require exact reconstruction of pre-damage weights, latent state, geometry, or activation patterns unless the experiment explicitly studies exact restoration.

MANDATORY PRECONDITIONS
1. The task metric must be defined before damage.
2. The undamaged phenotype must exceed a preregistered task threshold.
3. The lesion must produce a statistically meaningful task-performance drop.
4. Damage magnitude and target must be recorded.
5. The system must not reload the full pre-damage phenotype.
6. A matched control must establish how much apparent recovery occurs without the repair mechanism being tested.

DAMAGE CLASSES
D0 — STATE LESION
Erase or perturb mutable cell state while preserving immutable task evidence.

D1 — CELL LESION
Deactivate/remove a declared fraction or region of cells.

D2 — CONNECTION LESION
Remove or corrupt communication links/edges.

D3 — SPECIALIST LESION
Remove cells/modules identified by a predeclared influence or specialization metric.

D4 — PERSISTENT-STATE LESION
Damage compact retained state while leaving genome parameters intact.
Use only after persistent state exists as a separate mechanism.

D5 — GENOME LESION
Damage shared developmental parameters.
This is a later robustness question and must not be conflated with phenotype regeneration.

EARLY EXPERIMENT RULE
DG-1A/P0 may use morphology loss as its task metric because its purpose is canonical reproduction.
DG-1B and beyond must use functional task metrics.

REQUIRED CONTROLS
C0 — UNDAMAGED CONTROL
Same phenotype, no lesion.

C1 — DAMAGED / NO REPAIR EXPOSURE
Same architecture trained without regeneration/damage curriculum where possible.

C2 — DAMAGED / FROZEN DYNAMICS
Stop developmental updates after lesion when task semantics permit. Measures passive residual robustness.

C3 — MATCHED NON-DEVELOPMENTAL MODEL
Fixed/recurrent/message-passing comparator with comparable active parameter budget when scientifically meaningful.

REQUIRED PRIMARY METRICS
P_pre = task performance immediately before damage.
P_drop = task performance immediately after damage.
P_t = task performance after t repair/development steps.

LostFunction = P_pre - P_drop.
RecoveredFunction(t) = P_t - P_drop.
RecoveryFraction(t) = RecoveredFunction(t) / LostFunction, where LostFunction is positive and materially nonzero.

Record threshold times for at least:
T50 = steps/time to recover 50% of lost function.
T90 = steps/time to recover 90% where attainable.
T95 = optional stricter threshold.

Also record area under the normalized recovery curve over a fixed horizon.

RESOURCE METRICS DURING REPAIR
- developmental update steps;
- wall-clock repair latency;
- active cells/modules over time;
- resident phenotype bytes;
- active phenotype bytes/parameters;
- messages/neighborhood operations or declared communication proxy;
- changed/reactivated cell fraction;
- peak RAM/VRAM where measurable;
- approximate FLOPs or operation count if practical;
- persistent state retained across lesion.

MECHANISTIC DIAGNOSTICS
Tier 1 — REQUIRED WHEN CHEAP
- per-cell update magnitude distribution;
- spatial/graph distance from lesion versus update magnitude;
- state-space distance to pre-damage and post-recovery attractor proxies;
- localization versus system-wide repair activity;
- seed-to-seed variance.

Tier 2 — EXPLORATORY
- transfer-entropy/information-flow estimate;
- causal communication ablations;
- dynamical dimensionality reduction;
- attractor-basin perturbation sweeps.
These must not become mandatory if their compute cost materially impairs home-hardware feasibility.

SUCCESS CONDITION — FUNCTIONAL REGENERATION
A run family may be described as demonstrating functional regeneration only if:
- undamaged task performance passes the declared threshold;
- lesion causes meaningful functional loss;
- developmental updates recover a declared fraction of lost function;
- recovery is materially better than matched control behavior;
- result replicates across multiple seeds;
- repair does not restore a saved full phenotype;
- retained-state and repair-resource costs are reported.

STRONGER SUCCESS CONDITION — REGENERABLE CAPABILITY
A capability may be described as REGENERABLE rather than merely robust only when a substantial portion of the functional phenotype is unavailable/destroyed and the system reconstructs enough computational structure to restore function from genome + permitted compact persistent state + current environment/input.

FAILURE MODES
F1 — DAMAGE TOO WEAK
Task metric barely changes; recovery claim is meaningless.

F2 — REDUNDANCY MASQUERADING AS REGENERATION
Performance remains because duplicate capacity survived; little or no structure is reconstructed.
This may still demonstrate robustness, but not regeneration.

F3 — STATE RELOAD
System restores saved phenotype/state.
Disqualifies regeneration claim.

F4 — GLOBAL CONTROLLER REPAIR
An undeclared privileged controller reconstructs the phenotype using global state unavailable to ordinary cells.
Disqualifies decentralized-regeneration claim.

F5 — ENDPOINT RECOVERY WITH UNBOUNDED COST
Function returns only through excessive time, communication, or memory.
Counts as functional recovery but fails resource-credible regeneration.

F6 — VISUAL/STRUCTURAL RESTORATION WITHOUT FUNCTION
Does not count as functional regeneration.

F7 — FUNCTION RETURNS THROUGH TASK RELEARNING
If the system retrains extensively on labeled data after damage, distinguish retraining from autonomous regeneration. Recovery using ordinary task labels/data may be a valid separate experiment but is not the strongest regeneration claim.

PHENOTYPE EQUIVALENCE RULE
For most DG-1B+ tasks, regenerated phenotype identity is defined behaviorally/causally rather than by exact tensor equality.
Different weights, cell states, or topologies may belong to the same functional equivalence class if they satisfy the same declared function and robustness tests.

EARLY DG-1B/D PROTOCOL
1. Develop phenotype to stable task criterion.
2. Snapshot metrics only; do not use snapshot as repair input.
3. Apply D0 or D1 lesion at preregistered severity.
4. Measure immediate functional loss.
5. Run repair dynamics for fixed horizon.
6. Record recovery trajectory and resource trajectory.
7. Compare C1 and C2 controls.
8. Repeat across seeds and lesion locations.
9. Escalate to D3 only after an influence metric exists.

DECISION
Functional regeneration is now a first-class experimental contract. Endpoint task accuracy alone is insufficient; lesion effectiveness, recovery dynamics, matched controls, retained state, and repair cost are mandatory.

OPEN QUESTIONS
- What minimum lesion severity best distinguishes redundancy from true reconstruction?
- How should RecoveryFraction be aggregated across heterogeneous task metrics?
- When graph topology is mutable, should restored communication paths count as structure regeneration even if node states remain intact?
- What repair-cost threshold makes regeneration preferable to simply retaining the phenotype?

NEXT EXPERIMENT
Use this protocol to parameterize DG-1B/D-P1 after DG-1A-P0 validates the substrate.

PROVENANCE
- Mordvintsev et al. Growing Neural Cellular Automata. Distill, 2020.
- Randazzo et al. Self-classifying MNIST Digits. Distill, 2020.
- Smart cellular bricks for decentralized shape classification and damage recovery. Nature Communications, 2026.
- Structured Fluctuations and the Information Dynamics of Self-Maintenance in Growing Neural Cellular Automata. Entropy, 2026.
- Self-Organising Digital Circuits. arXiv:2608.02606, 2026.