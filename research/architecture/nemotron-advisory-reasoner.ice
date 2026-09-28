TITLE: Nemotron Advisory Experiment Reasoning Interface
DATE: 2026-09-28
STATUS: QUALIFIED_NOT_ACTIVATED
TRACK: DG-1
CONFIDENCE: QUALIFIED

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
The Yggdrasil GitHub repository is public. The staged reasoner therefore uses the free Nemotron endpoint only for packets reconstructed exclusively from public Yggdrasil or Wingless repository content. The free endpoint may log prompts and completions for NVIDIA security/product-improvement purposes. Do not transmit Mind-Palace records, local-only evidence, credentials, personal data, or any future private/unpublished material through this route.

MODEL
Default and staged-only route: nvidia/nemotron-3-ultra-550b-a55b:free

ACTIVATION GATE
This interface is not active merely because the branch exists.

QUALIFICATION RESULT
GitHub Actions run 36483722629 qualified the pinned free route at Wingless source head 212ca3031977da808a1416065599f65992f3f17f.

Deterministic qualification: PASS.
Full Wingless regression: PASS.
Historical blind replay: PASS.
Fixtures: 7 total, spanning Wingless and Yggdrasil.
Repetitions: 2.
Decisions: 14/14 matched the frozen historical continuation.
Scientific-boundary violations: 0.
Returned model: nvidia/nemotron-3-ultra-550b-a55b:free.
Returned provider: Nvidia.
Evidence artifact: 10998885130.
Artifact SHA-256: 19f5943efde3c2169a0b3d3fa1dc8def581dce41afa9e3266f2e335887471073.

ACTIVATION GATE
Qualification does not itself activate the reasoner.
Still required:
- explicitly integrate through the existing ckb-plane research boundary;
- keep Nemotron advisory-only;
- keep the free route public-repository-only;
- preserve the dedicated research credential;
- do not interrupt active KTRADE work;
- resume Mind-Palace context selection only after its mailbox path is healthy.

KTRADE PRIORITY GUARD
Current KTRADE work must not be paused, restarted, reordered, or have its queue altered to qualify or activate this reasoner. Setup and qualification must remain isolated until research execution authority can be exercised without production interference.

DECISION
Adopt one shared bounded reasoner contract across Wingless and Yggdrasil. Do not create a Yggdrasil-local autonomous agent or competing orchestration path.

CREDENTIAL ISOLATION
The shared research reasoner must use a credential dedicated to research reasoning, exposed only as WINGLESS_REASONER_OPENROUTER_API_KEY on the research runner. It must not reuse any OpenRouter credential used by CKB repair, orchestration, or other plane functions.


FREE-ROUTE PUBLIC-SOURCE GATE
Every Nemotron request must be classified public-repository.
Public repository source hashes and qualification identity remain part of provenance.
If a required fact exists only in Mind-Palace or local/private evidence, Nemotron must not receive that fact through the free route. Mind-Palace may identify a relevant historical decision, but the reasoner packet must be rebuilt from public GitHub evidence before transmission.

MIND-PALACE ROLE
Mind-Palace remains in the research architecture as durable historical context. It does not get replaced by Nemotron. It may support context selection and post-result durable ingestion. Nemotron remains an advisory reasoner over bounded public evidence only.
