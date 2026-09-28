TITLE: Nemotron Advisory Experiment Reasoning Interface
DATE: 2026-09-28
STATUS: STAGED_NOT_ACTIVATED
TRACK: DG-1
CONFIDENCE: UNQUALIFIED

PURPOSE
Allow Yggdrasil experiments to use the shared Wingless Nemotron/OpenRouter reasoning adapter for bounded scientific planning, critique, and interpretation without creating a second scheduler, executor, or acceptance authority.

IMPLEMENTATION SOURCE
Repository: spoonman136668-ai/Wingless
Branch: research/nemotron-openrouter-reasoner-r1
Contract schema: wingless.experiment-reasoning-request.v1
Result schema: wingless.experiment-reasoning-result.v1

AUTHORIZED ADVISORY ROLES
1. plan-next-experiment
2. critique-proposed-experiment
3. interpret-sealed-result

NON-AUTHORITY
Nemotron output does not authorize:
- experiment execution;
- queue submission;
- retry;
- threshold or seed changes;
- widening an experiment already preregistered;
- acceptance or promotion;
- accepted-ref mutation;
- ckb-plane controller changes;
- KTRADE changes or runtime interference;
- broker, credential, deployment, or production access.

SCIENTIFIC ORDERING
For planning:
current immutable evidence -> bounded reasoner request -> advisory proposal -> deterministic preregistration/freeze -> execution by existing authority.

For interpretation:
frozen preregistration -> deterministic execution -> sealed raw result and qualification -> bounded reasoner request -> advisory interpretation -> next experiment proposal.

A reasoner must never see a result and then revise the success criteria, controls, seeds, budget, or threshold for that result.

QUALIFICATION IDENTITY
Reasoning evidence is reusable only when semantically relevant identity matches, including:
- frontier SHA-256;
- qualification-contract SHA-256;
- request SHA-256;
- reasoner configuration SHA-256;
- requested and returned model identity;
- returned provider identity when supplied;
- seed;
- reasoning effort;
- response SHA-256.

Identity drift invalidates cached reasoning evidence for qualification purposes.

PRIVACY
Actual Yggdrasil frontier packets may contain unpublished research. The default route is the paid Nemotron 3 Ultra model with provider data collection denied and zero-data-retention requested. The free route may be used only with explicitly sanitized/non-confidential packets.

MODEL
Default: nvidia/nemotron-3-ultra-550b-a55b
Optional sanitized fixture route: nvidia/nemotron-3-ultra-550b-a55b:free

ACTIVATION GATE
This interface is not active merely because the branch exists.

Before activation:
- qualify the adapter unit tests;
- add historical blind replay fixtures;
- measure scientific constraint violations and redundant experiment proposals;
- compare proposed experiments against held-out future evidence;
- perform required final Wingless integration/full regression;
- explicitly integrate through the existing ckb-plane research boundary.

KTRADE PRIORITY GUARD
Current KTRADE work must not be paused, restarted, reordered, or have its queue altered to qualify or activate this reasoner. Setup and qualification must remain isolated until research execution authority can be exercised without production interference.

DECISION
Adopt one shared bounded reasoner contract across Wingless and Yggdrasil. Do not create a Yggdrasil-local autonomous agent or competing orchestration path.
