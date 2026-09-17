TITLE: YG-R6 — Ancestor Inheritance Research Plan
DATE: 2026-09-17
STATUS: PLANNED
TRACK: DG-1I
CONFIDENCE: PLAUSIBLE

QUESTION
Can useful behavior from previous models become compact developmental information that enables descendant phenotypes to recover those capabilities without permanently carrying every ancestor checkpoint?

BOUNDARY
Ancestor inheritance is not checkpoint averaging by default. The object of inheritance is useful function and developmental bias, not identical weights.

ANCESTOR ROLES
An ancestor may act as:
- teacher
- behavioral demonstrator
- specialist adapter donor
- micro-expert donor
- curriculum generator
- failure generator
- repair-example generator
- trajectory generator
- activation/representation probe source

INHERITABLE ARTIFACT CLASSES

A. BEHAVIORAL DEMONSTRATIONS
Input -> output pairs, preference comparisons, execution traces, intermediate plans where legally/technically available.
Persistent cost: dataset/examples.
Advantage: model-agnostic.
Risk: regeneration may secretly require large replay corpora.

B. ADAPTER / LOW-RANK DELTAS
Extract task-specialized LoRA or adapter parameters from a shared seed.
Persistent cost: adapter bytes.
Advantage: compact and directly measurable.
Risk: simply storing one adapter per task does not demonstrate developmental inheritance.

C. MICRO-EXPERT MODULES
Extract bounded specialist subnetworks or heads.
Advantage: explicit functional units.
Risk: descendant becomes conventional routed expert library.

D. ACTIVATION SIGNATURES
Store compact target statistics or representational anchors.
Advantage: may supervise regenerated function without full weights.
Risk: signatures can be insufficient or become large hidden state.

E. SUCCESS / FAILURE / REPAIR TRAJECTORIES
Store examples of state transitions leading to success and recovery.
Advantage: directly relevant to developmental repair policy.
Risk: expensive corpus growth.

INHERITANCE LEVELS

I0 — BEHAVIORAL DISTILLATION BASELINE
Train descendant directly from ancestor outputs. No developmental claim.

I1 — STATIC DONOR BASELINE
Keep ancestor adapters/experts and route to them. Strong conventional baseline.

I2 — GENOME CONDITIONING
Use ancestor-derived compact codes to condition a shared developmental rule that generates task phenotype.

I3 — DEVELOPMENTAL ASSIMILATION
After exposure to multiple ancestors, remove direct donor access and test whether the shared genome can regenerate capabilities using bounded capability codes.

I4 — CROSS-ANCESTOR COMPOSITION
Request tasks requiring combined ancestor capabilities and test whether development composes structures rather than selecting one donor.

I5 — REPAIR INHERITANCE
Damage a descendant specialist and test whether developmental dynamics recover function using genome + compact ancestor-derived information.

RECOMMENDED FIRST ANCESTOR EXPERIMENT
Do not begin with large language models.
Use one small shared base network and 3-5 independently trained specialist adapters on clearly separable synthetic or small benchmark tasks.

Example task families:
- symbolic transforms
- sequence parity/counting
- small arithmetic operator families
- compact image classification subsets

Protocol:
1. Train/freeze common seed.
2. Train one small adapter per task; these are ancestors/donors.
3. Establish static adapter-router baseline.
4. Train developmental genome to generate or assemble descendant adapter cells from task/context code.
5. Remove donor adapter access at evaluation.
6. Evaluate recovered task function, persistent information, development cost, and interference.
7. Damage generated adapter-cell population and evaluate regeneration.

CORE METRICS
- task performance retained from each ancestor
- persistent genome bytes
- capability-code bytes per ancestor/task
- donor bytes required at evaluation: target = zero for assimilation claim
- active phenotype parameters
- development steps / latency
- cross-capability interference
- compositional generalization
- regeneration recovery
- full phenotype storage baseline
- static adapter-router baseline
- hypernetwork generator baseline

SUCCESS CONDITION — I2/I3
A result is evidence for developmental inheritance only if:
- descendant recovers multiple useful ancestor behaviors above declared thresholds;
- full ancestor/adaptor weights are not required at evaluation;
- retained developmental information is materially smaller than storing all recovered phenotypes at equivalent quality OR provides an additional demonstrated benefit such as regeneration/composition;
- performance is compared to a static router and generator baseline.

FAILURE CONDITIONS
- one capability dominates and others collapse;
- code size approaches phenotype size;
- generated descendants memorize task IDs without reusable developmental structure;
- full donor replay is required for every wake;
- cross-capability composition fails despite individual recovery;
- static adapter routing is strictly simpler and equal on all relevant metrics.

ANTI-CHEATING TESTS
- randomize capability-code labels and retrain only readout: should not preserve inherited mapping trivially.
- reduce code dimensionality and map performance/storage frontier.
- withhold one task combination during training and test compositional development.
- compare generated phenotype parameter similarity versus functional similarity; identical weights are not required.
- test donor removal explicitly.

LARGE-MODEL MIGRATION GATE
Move to pretrained language-model ancestors only after small-model inheritance shows:
- stable multi-capability recovery;
- bounded code size;
- measurable advantage over static routing on at least one Yggdrasil-specific axis;
- reproducible regeneration or composition.

DECISION
Treat previous models as capability sources, not permanent residents. Begin inheritance with adapters around a common small seed because they provide clean byte accounting and strong conventional baselines.

OPEN QUESTIONS
- Can a genome learn reusable developmental motifs across adapters rather than generating independent copies?
- Can capability codes be inferred from demonstrations rather than supplied as task IDs?
- How much donor behavior must be retained to repair a generated phenotype later?
- Can multiple ancestors contribute to one organ without destructive interference?

NEXT EXPERIMENT
After DG-1F establishes module cells, train three specialist low-rank modules around one frozen seed and compare static routing versus developmental regeneration of those modules from compact codes.
