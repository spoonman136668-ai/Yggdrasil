TITLE: DG-1A Adaptive-Rule Research Frontier R2 — Utility, Relocation, and Local Causal Credit
DATE: 2026-09-18
STATUS: ACTIVE RESEARCH FRONTIER
TRACK: DG-1A / ADAPTIVE RULES
BRANCH: dg1a-ar
CANONICAL_P0_BRANCH: dg1a-p0
CANONICAL_P0_HEAD_UNCHANGED: b45703418a7097782a032a142665c4642c2945fa

PURPOSE
Seal the adaptive-rule research state after AR-U1 through AR-U5.

This is a navigation record.
It does not alter canonical DG-1A-P0 or STAB-18-R1 authority.

R1 STATUS
STAB-18-R1 remains:
- frozen;
- unexecuted;
- scientifically prior;
- canonical seed-0 / 200-iteration run unspent.

No AR-U experiment modifies or substitutes for R1.

CURRENT ADAPTIVE BRANCH
dg1a-ar

RESEARCH CHAIN ADDED IN THIS BATCH

AR-U1
research/experiments/dg1a/adaptive/dg1a-aru1-multirole-utility-market-audit.ice

Key results:
- several soft functions can coexist without a global role histogram;
- bounded factorized role gates outperform a zero-sum role simplex;
- role-state erasure recovery:
  repair 8/8;
  growth 8/8;
  inhibitor 8/8;
  relay 7/8 under the fixed <=10% criterion by 160 steps;
- frozen controls do not recover;
- strict permanent specialist unavailability exposes a structural oracle limit.

Important lesson:
functional recovery must be interpreted relative to both:
pre-lesion performance
and
post-lesion attainable capacity.

AR-U2
research/experiments/dg1a/adaptive/dg1a-aru2-moving-demand-role-relocation-audit.ice

Key results:
horizontal -> vertical communication demand switch:

pre:
20.6062 route cost

immediate after switch:
52.5396

adaptive:
20.4748

frozen:
54.0807

8/8 recovery.

Median switching latency:
60 steps.

Spatial relay expression:
H:
0.891 -> 0.358

V:
0.226 -> 0.894

Repeated H/V switching remained stable.

Important lesson:
explicit role retirement prevents canalization and permits reversible functional reorganization.

AR-U3
research/experiments/dg1a/adaptive/dg1a-aru3-local-utility-corruption-audit.ice

Key results:
- local utility delays up to 32 steps remain recoverable;
- treating missing utility as zero causes failure;
- retaining the previous utility estimate during missing observations restores near-clean behavior through 50% dropout;
- mild analog noise can be mitigated by temporal aggregation;
- semantically wrong role credit remains dangerous.

Important lesson:
MISSING EVIDENCE
must not be represented as
NEGATIVE EVIDENCE.

AR-U4
research/experiments/dg1a/adaptive/dg1a-aru4-redundant-local-credit-cue-audit.ice

Key results:
- noisy redundant credit cues help only if error modes are sufficiently independent;
- clipping each noisy cue before averaging creates rectification bias and destroys much of the redundancy benefit;
- aggregating raw signed evidence before bounding can recover the benefit;
- at sigma=0.25:
  eight independent raw cues recovered 6/6;
  correlated cue sets did not.

Important lesson:
evidence aggregation order matters.

Preferred abstraction:

raw partially independent evidence
->
aggregate
->
bounded utility / decision state.

AR-U5
research/experiments/dg1a/adaptive/dg1a-aru5-causal-local-consequence-credit-poc.ice

Major result:
cells do not need to be handed a role-specific analytic utility in the toy.

A bounded derivative-free local meta-rule:

perturb one role gate
->
observe only own local scalar consequence
->
keep/reverse perturbation

learned spatial specialization and relocated it after demand moved.

Clean 8-seed result:

pre-switch local consequence:
0.105368

immediate after demand switch:
0.244970

final:
0.105884

recovery:
8/8

mean switching latency:
87 steps

relay spatial state:

before:
H 0.860
V 0.370

after:
H 0.377
V 0.857

This is the strongest current synthetic meta-rule precursor.

It remains synthetic because:
the local consequence scalar is hand-designed.

NOISE LESSON FROM AR-U5
Relative recovery can conceal absolute degradation.

At larger observation noise,
the perturb-and-observe system can recover to its own degraded noisy baseline.

Therefore future gates must report BOTH:

relative recovery

and

absolute consequence quality.

CURRENT ARCHITECTURAL MODEL

SHARED DEVELOPMENTAL ENGINE
one compact shared local rule

FAST STATE
ordinary NCA state

ENVIRONMENTAL CONTEXT
only for information that is genuinely exogenous

ENDOGENOUS STATE ESTIMATION
injury, maintenance, saturation, local demand

SOFT FUNCTIONAL ROLES
continuous reversible local specialization

ROLE RETIREMENT
explicit de-specialization when utility disappears

LOCAL CONSEQUENCE MEMORY
freshness-aware bounded consequence estimates

META-RULE
small bounded role/sensitivity changes retained only when local consequences improve

SLOW HERITABLE LAYER
future bounded micro-genome inheritance/mutation

IMPORTANT SEPARATIONS

CONTEXT
What objective/environmental regime is valid?

STATE ESTIMATION
What is happening locally?

ROLE
What function is this cell currently expressing?

CONSEQUENCE
Did a recent local action improve something locally measurable?

CREDIT
Which recent action caused that consequence?

These must not be collapsed into one scalar.

STRONGEST CROSS-DOMAIN PATTERN
Partially independent evidence has now been useful in:

1. injury sensing;
2. seasonal mode sensing;
3. local role-credit sensing.

Common-mode duplication repeatedly fails.

Therefore:
EFFECTIVE INDEPENDENT EVIDENCE
is a likely core design variable.

Do not equate it with raw hidden-channel count.

LITERATURE ALIGNMENT

Béna and Goodman
Dynamics of specialization in neural modules under resource constraints
Nature Communications 16, 187 (2025)
DOI: 10.1038/s41467-024-55188-9

Relevant:
- structural modularity alone does not guarantee functional specialization;
- separable environmental structure and resource constraints promote specialization;
- specialization changes dynamically with information flow.

Masumori, Sato, Ikegami
Structured Fluctuations and the Information Dynamics of Self-Maintenance in Growing Neural Cellular Automata
Entropy 28(8), 893 (2026)

Relevant:
- hidden state fluctuations are structured;
- repair changes information organization;
- redundancy/synergy structure is dynamic.

These works are context for hypotheses only.
They do not validate the current Yggdrasil synthetic mechanisms.

WHAT HAS NOT BEEN SHOWN
Do not claim:

- Yggdrasil has emergent roles;
- Yggdrasil regenerates computation;
- a real NCA can learn the AR-U5 meta-rule;
- local consequence is available in current Yggdrasil;
- cognition has been developmentally generated;
- functional regeneration has been achieved.

NEXT RESEARCH FRONTIER

AR-U6 — DELAYED / CONFOUNDED CAUSAL CREDIT
Stress perturb-and-observe credit with:
- delayed effects;
- multiple simultaneous role changes;
- unrelated environmental disturbances;
- correlated consequences;
- false causal associations.

Question:
does naive local consequence credit break?

If yes:
test bounded local temporal counterfactual memory or domain-separated perturbation schedules.

This should explicitly reuse the causal-confound lesson from STAB-18-R1 without touching R1.

AR-C1 — REPEATED DECENTRALIZED CONTEXT RELAY
The current freshness relay only solves one transition.

Need a local repeated-switch ordering mechanism that prevents:
old context
from overwriting
new context.

AR-E1 — ADVERSARIAL ECOLOGY
Only after AR-U6 / AR-C1 are understood.

Introduce bounded competitor/toxin pressure and observe whether the utility/meta-rule system produces:
- containment;
- defense specialization;
- sacrificial boundaries;
- dormancy;
- redundancy.

AR-H1 — HERITABLE MICRO-GENOME
Still later.

Inheritance should use modulation dimensions that have already proven useful:
- role sensitivity;
- repair responsiveness;
- update gain;
- inhibition;
- dormancy;
- relay sensitivity.

Do not evolve arbitrary per-cell networks.

READINESS FOR REAL FUNCTIONAL-REGENERATION EXPERIMENT
Current evidence now supports:

[yes] compact explicit context works synthetically
[yes] context robustness/failure modes mapped
[yes] plausible local context relay
[yes] endogenous vs exogenous mode distinction
[yes] soft role recovery from role-state erasure
[yes] fixed role quotas rejected
[yes] utility-driven functional placement
[yes] multi-role coexistence
[yes] moving-demand role relocation
[yes] bounded local causal-consequence adaptation POC

Still preferred before real functional-regeneration spend:

[ ] confounded/delayed causal-credit stress
[ ] repeated decentralized context ordering
[ ] local consequence source that can map onto real Yggdrasil latent dynamics
[ ] implementation path that does not require explicit engineered role registers

NEXT ACTION
AR-U6.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = RESEARCH_FRONTIER_SUMMARY
canonical_scientific_execution = false
canonical_r1_execution_spent = false
