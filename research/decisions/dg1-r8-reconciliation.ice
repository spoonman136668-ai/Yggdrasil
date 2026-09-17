TITLE: DG-1 R8 Reconciliation Decision
DATE: 2026-09-17
STATUS: ACCEPTED
TRACK: DG-1
CONFIDENCE: SUPPORTED

DECISION ID
DG1-DEC-R8-001

PURPOSE
Reconcile YG-R8 findings with the earlier DG-1 Initial Architecture Decision and YG-R7 First Prototype Recommendation without erasing their historical state.

SUPERSEDES
This decision supersedes only the implementation-readiness/status portions of:
- research/decisions/dg1-initial-architecture.ice
- research/experiments/dg1a/dg1a-p0-prototype-recommendation.ice

All technical content in those records remains historical design evidence unless explicitly changed below.

R8 INPUTS
- research/foundations/yg-r8-gap-closure.ice
- research/architecture/functional-regeneration.ice
- research/architecture/structural-plasticity.ice
- research/architecture/measurement-framework.ice

R8 CONCLUSIONS
1. The canonical 2D NCA remains the correct first implementation control.
2. Functional recovery must be evaluated separately from visual regeneration.
3. Graph-based functional development should move earlier, immediately after the first stable grid functional-recovery experiment.
4. Specialization claims require functional/causal evidence, not latent clustering alone.
5. Open-ended growth remains prohibited; growth and compaction must later be paired under hard ceilings.
6. Capacity accounting must distinguish genome, resident phenotype, active phenotype, and development/regeneration cost.
7. Repair telemetry must record full recovery trajectories and matched controls.

IMPLEMENTATION GATE REVIEW
CELL REPRESENTATION: IDENTIFIED.
Shared latent-state cells; initial 16-32 channels.

DEVELOPMENTAL UPDATE MECHANISM: IDENTIFIED.
Shared residual local neural update rule with randomized horizon and optional stochastic firing.

COMMUNICATION TOPOLOGY: IDENTIFIED FOR P0.
Fixed 2D 3x3 Moore/local perception.
Graph-based topology explicitly scheduled for P1G after initial functional-recovery validation.

TRAINING OBJECTIVE: IDENTIFIED FOR P0.
Task/morphology loss + stability as needed; damage curriculum for regeneration variant.

RESOURCE OBJECTIVE: IDENTIFIED FOR P0.
Hard limits plus measurement first; no soft resource-pressure optimization required for canonical reproduction.

FIRST BASELINE: IDENTIFIED.
Growth-only, persistence-trained, damage/regeneration-trained NCA variants.

FIRST EXPERIMENT: IDENTIFIED.
DG-1A-P0 canonical NCA reproduction.

MEASUREMENT SCHEMA: IDENTIFIED AND EXPANDED.
Use DG-1 Measurement Framework; P0 minimum subset plus recovery trajectory instrumentation.

SUCCESS CONDITION: IDENTIFIED.
Reproduce canonical growth/persistence behavior and materially better damage recovery for the regeneration-trained variant across multiple seeds/configurations, with reproducible telemetry.

FAILURE CONDITION: IDENTIFIED.
Fail if validated implementation cannot reproduce known behavior under bounded parameter search; if damage effect is meaningless; if recovery relies on state reload; or if telemetry cannot separate retained state and recomputation.

R8 CLOSEOUT VERDICT
YG-R8 PASS 1 has closed the research gaps required to begin the bounded DG-1A-P0 implementation.

This does NOT close the broader YG-R8 research theme permanently. Further targeted literature/research passes should be triggered by experimental evidence, not open-ended reading.

AUTHORIZED IMPLEMENTATION SCOPE
Only:
- DG-1A-P0 canonical NCA substrate;
- deterministic configuration and seeding;
- damage operators needed by P0;
- metrics/resource instrumentation needed by P0;
- tests for cell update, damage, metrics, and hard limits;
- experiment runner/configuration;
- machine-readable evidence output.

NOT AUTHORIZED BY THIS DECISION
- pretrained language-model seed integration;
- LoRA/adapters/micro-expert cells;
- ancestor extraction/inheritance;
- open-ended cell replication;
- mutable graph growth;
- autonomous deployment;
- external execution authority;
- claims of general intelligence;
- claims of sublinear capability scaling.

P0 IMPLEMENTATION CONSTRAINTS
- one shared update network across cells;
- fixed maximum grid size;
- no hidden full-state repair oracle;
- damage does not silently restore from checkpoint;
- all random seeds explicit;
- narrative interpretation only in .ice;
- generated metrics/configs may use JSON/JSONL/CSV;
- unit tests may not be disabled, skipped, or weakened to pass behavior.

EARLY ROADMAP AFTER P0
P0 -> P1 grid functional recovery -> P1G graph functional generation/maintenance -> P2 causal specialization -> P3 targeted specialist regeneration.

DECISION
DG-1A-P0 status is now READY FOR BOUNDED IMPLEMENTATION under the R8 measurement and regeneration contracts.

NEXT ACTION
Create the P0 experiment specification and implementation scaffold only. Do not begin P1 in the same work packet.
