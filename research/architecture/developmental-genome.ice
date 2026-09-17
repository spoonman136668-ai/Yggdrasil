TITLE: YG-R2B — Developmental Genome Architecture Study
DATE: 2026-09-17
STATUS: RECOMMENDED INITIAL DESIGN
TRACK: DG-1
CONFIDENCE: PLAUSIBLE

QUESTION
What belongs in the persistent developmental genome, and how can it generate task-relevant phenotype without merely storing every phenotype verbatim?

DEFINITION
The developmental genome is the compact persistent parameterization of rules that govern cell update, differentiation, communication, structural requests, repair, and phenotype generation.

It is not synonymous with:
- a checkpoint containing all active phenotype weights;
- a table of one adapter per task;
- a global controller with unrestricted access to every cell;
- an archive of complete task networks.

INITIAL GENOME
For DG-1A/B, the genome is simply the shared parameters of the local NCA update rule plus fixed perception operators and explicit hard-coded lifecycle constraints.

GENOME INPUTS — EARLY
Allowed:
- focal cell state
- bounded-neighborhood states/messages
- immutable local task/input channels
- bounded global scalars that represent environment constraints, if explicitly ablated
Not allowed by default:
- arbitrary full-grid flattened state
- unrestricted task labels that trivially identify a stored phenotype
- direct access to evaluation targets

GENOME OUTPUTS — STAGED
Stage 0:
- residual state delta
- activity/alive update
Stage 1:
- role/differentiation logits
- communication gating
Stage 2:
- bounded structural requests: spawn/connect/disconnect/hibernate/wake/prune
Stage 3:
- compact payload-generation codes or low-rank/module parameters

GENOTYPE / PHENOTYPE SEPARATION TEST
A claimed genome should pass at least one compression-style test:
1. multiple task phenotypes are recoverable from one shared genome plus materially smaller task/context codes than the full phenotypes; or
2. damaged phenotype can be functionally regenerated from genome plus bounded retained state without replaying original optimization from scratch; or
3. a new related task develops faster/with less added persistent information because the genome reuses learned developmental motifs.

If none are true, the system may still be useful, but the genotype/phenotype claim is not established.

CANDIDATE DEVELOPMENTAL UPDATE MECHANISMS

A. SHARED RESIDUAL NCA RULE
perception -> small MLP/conv -> residual state update
Advantages: simple, differentiable, established baseline.
Risks: fixed topology; structural meaning remains implicit.
Use: DG-1A/B default.

B. MESSAGE-PASSING GRAPH DEVELOPMENTAL PROGRAM
neighbor messages -> aggregate -> shared update -> structural request
Advantages: topology can become non-Euclidean; directly suitable for neural modules.
Risks: discrete topology operations and credit assignment increase instability.
Use: after DG-1B stability.

C. GENOME-CONDITIONED MODULE GENERATOR
shared developmental state -> hypernetwork-like generator -> bounded payload weights
Advantages: strong genotype/phenotype separation; potentially regenerable modules.
Risks: generator can become centralized or memorize full module library.
Use: DG-1F/H after anti-cheating tests exist.

D. HYBRID LIBRARY + DEVELOPMENT
Genome generates/routs among a small basis of reusable payload primitives while local rules determine assembly.
Advantages: easier training and hardware realization.
Risks: may collapse into conventional MoE/router.
Use: baseline and possible practical bridge, not assumed final form.

RECOMMENDED TRAINING ORDER
1. Learn shared state dynamics with fixed topology.
2. Add damage during training and evaluate functional regeneration.
3. Introduce explicit role differentiation.
4. Add structural requests under hard budgets.
5. Add generated neural payloads.
6. Test hibernation/wake and regenerable phenotype states.
7. Only then test ancestor-derived developmental information around a pretrained seed.

PERSISTENT INFORMATION LEDGER
Every experiment claiming compact development must report persistent information in separate categories:
- genome parameters/bytes
- task/context code bytes
- retained cell state bytes
- archived phenotype bytes
- replay/example bytes required for regeneration
- optimizer state if required at regeneration time

A phenotype is not meaningfully "regenerable from the genome" if hidden storage of examples, gradients, optimizer tensors, or complete weights dominates the retained information.

DEVELOPMENTAL COST
Report:
- update steps
- active cells per step
- active payload parameters
- messages/edges processed
- wall-clock latency
- peak RAM/VRAM
- bytes read/written for wake/regeneration

TRAINING OBJECTIVE — INITIAL FORM
L = L_task
  + lambda_stability * L_stability
  + lambda_activity * C_active
  + lambda_comm * C_communication
  + lambda_steps * C_development_steps

Later structural stages may add:
  + lambda_resident * C_resident_bytes
  + lambda_growth * C_new_structure
  + lambda_interference * L_retention

Penalty weights are experimental variables. Hard safety/resource ceilings must remain hard constraints rather than learnable penalties alone.

CENTRALIZATION DIAGNOSTICS
- mutual information / probe accuracy between any global context channel and final task identity
- performance after removing global context
- performance when messages are restricted to local neighborhoods
- concentration of gradient or information flow through a small set of privileged cells
- comparison to a matched global hypernetwork/controller

DECISION
Use a shared local update rule as Genome v0. Treat hypernetwork-style weight generation as a later mechanism for creating module payloads, not as the initial definition of Yggdrasil development.

OPEN QUESTIONS
- Can one genome support multiple stable attractors corresponding to useful functional organs?
- What task/context code size causes the genome to become a disguised checkpoint index?
- Can lineage state compress developmental history enough to accelerate repeated growth?
- What persistent information is minimally necessary to wake a hibernating specialist?

NEXT EXPERIMENT
Measure whether a shared update rule can recover task function after targeted cell damage while retaining only genome parameters and surviving cell state.
