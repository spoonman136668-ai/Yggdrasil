TITLE: DG-1A-P0 TRAIN-01 Status
DATE: 2026-09-17
STATUS: BOUNDED IMPLEMENTATION COMPLETE — SANDBOX GREEN — CONFIRMATORY EVIDENCE OPEN
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; SUPPORTED FOR SANDBOX EXECUTABILITY

WORK PACKET
DG1A-P0-TRAIN-01

BRANCH
dg1a-p0

OBJECTIVE
Add only the bounded P0 target, state-pool, training/evaluation, evidence, and exploratory-curriculum machinery required by the preregistered DG-1A-P0 specification.

IMPLEMENTED
- deterministic repository-native morphology target generator;
- deterministic target identity hash;
- finite detached phenotype state pool;
- growth-only training;
- persistence training;
- regeneration training;
- maturity-gated lesion curriculum;
- bounded optimizer/gradient clipping;
- hidden-state magnitude penalty;
- growth and recovery evaluator;
- raw and bounded RecoveryFraction;
- first-crossing and stable T50/T90;
- normalized recovery AUC;
- active-cell/resource reporting;
- fail-closed config loader and hard-limit checks;
- atomic finite JSON evidence writer;
- single bounded P0 runner;
- base, smoke, and fair exploratory probe configs.

EXPLICITLY NOT IMPLEMENTED
- graph topology;
- dynamic tensor/grid growth;
- structural replication;
- functional DG-1B tasks;
- pretrained intelligent seed;
- adapters or LoRA cells;
- ancestor inheritance;
- live deployment/external execution authority.

SANDBOX REGRESSION RESULT
Execution context: isolated ChatGPT CPU reconstruction from connected-GitHub source/test contents.
PyTorch: 2.10.0+cpu.
Result: 40 tests passed, 0 failed.

COVERAGE CLASSES
- original NCA shared-update and hard-limit tests;
- damage operator tests;
- morphology/recovery metric tests;
- resource accounting tests;
- deterministic target tests;
- state-pool tests;
- growth/persistence/regeneration training-path tests;
- recovery evaluation tests;
- config hard-limit tests;
- evidence finite/atomic-output tests;
- stable-threshold recovery semantics;
- regeneration maturity-threshold validation.

LIMITATION
The test workspace is a reconstruction rather than an authenticated repository checkout. Therefore this result is sandbox execution evidence, not authoritative commit-bound acceptance.

EXPLORATORY SCIENTIFIC STATUS
A matched single-seed CPU probe is recorded in:
research/experiments/dg1a/dg1a-p0-exploratory-probe-01.ice

Observed qualitative separation:
- growth-only: meaningful lesion followed by catastrophic instability;
- persistence: stable but lesion effect too small for strong regeneration interpretation;
- maturity-gated regeneration: meaningful lesion followed by stable T50/T90 and full bounded recovery within the declared window.

This is OBSERVED / exploratory, not SUPPORTED confirmatory evidence.

CURRENT CLAIM BOUNDARY
ALLOWED:
- the bounded P0 training/evidence implementation exists;
- its reconstructed test surface is green;
- single-seed exploratory behavior differentiates the three curricula.

NOT ALLOWED:
- H-P0-3 is confirmed;
- Yggdrasil has established general functional regeneration;
- morphology regeneration implies cognition;
- consumer-hardware scaling advantage is established.

NEXT GATE
1. Execute repository-native probe configs from an actual checkout so source_revision is captured.
2. Freeze a minimum meaningful damage-effect threshold before confirmatory interpretation.
3. Run a multi-seed probe family without post-hoc threshold changes.
4. If replicated, scale to the full 40 x 40 P0 configuration family.
5. Keep DG-1B closed until P0 closeout criteria are met.
