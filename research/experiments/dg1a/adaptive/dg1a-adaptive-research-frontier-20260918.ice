TITLE: DG-1A Adaptive-Rule Research Frontier — 2026-09-18
DATE: 2026-09-18
STATUS: ACTIVE RESEARCH FRONTIER
TRACK: DG-1A / ADAPTIVE RULES
BRANCH: dg1a-ar
CANONICAL_P0_BRANCH: dg1a-p0
CANONICAL_P0_HEAD_UNCHANGED: b45703418a7097782a032a142665c4642c2945fa

PURPOSE
Consolidate the current adaptive-rule evidence after the first AR-01 through AR-05/06 synthetic research batch.

This file is a research-navigation record.
It does not alter canonical STAB-18-R1 authority.

R1 STATUS
STAB-18-R1 remains:
- frozen;
- unexecuted;
- scientifically prior;
- seed-0 / 200-iteration run unspent.

No adaptive-rule experiment in this frontier may modify or bypass R1.

CURRENT ADAPTIVE BRANCH
dg1a-ar

BASE:
b45703418a7097782a032a142665c4642c2945fa

CURRENT RESEARCH CHAIN

1.
dg1a-ar01-seasonal-context-synthetic-control.ice

Result:
explicit compact context strongly outperformed a parameter-count-matched fixed-rule control in the synthetic local-policy task.

Evidence:
SYNTHETIC

2.
dg1a-ar01-context-encoding-ablation.ice

Result:
CIRCLE-2:
cos(phi), sin(phi)

was the smallest tested strong context representation.

3.
dg1a-ar01-explicit-seasonal-modes-spec.ice

AR-01 is preregistered and unexecuted.

4.
dg1a-ar01-context-corruption-robustness-audit.ice

New finding:
CIRCLE-2 tolerates modest analog corruption.

Fresh 8-seed measured sandbox benchmark:

clean context MSE:
0.003735

fixed zero-context control:
0.043589

Context remained better than the fixed-control mean through tested:
- phase jitter ±45 degrees;
- 25% context dropout;
- Gaussian sigma 0.40;
- 50% signal amplitude.

Danger class:
confident semantically wrong mode.

Noise-augmented training improved missing/noisy context robustness without adding parameters,
but did not solve wrong-mode corruption.

5.
dg1a-ar01-local-context-propagation-audit.ice

Major negative:
passive local diffusion is too slow for organism-wide seasonal switching.

113-cell body:
8 sensors:
172 median steps.

613-cell body:
64 sensors:
729 median steps.

Major positive:
a freshness/change-sensitive local relay can propagate a single mode change much faster.

613 cells:
1 sensor:
26 median steps clean;
36 with 50% message dropout;
59.5 with 75% dropout.

Hard limit:
a disconnected component with no sensor and no new-context memory cannot acquire the new exogenous context through local communication.

6.
dg1a-ar01-redundant-sensor-consensus-audit.ice

Major result:
sensor redundancy helps only when error modes retain independence.

At 10% marginal sensor error:

1 sensor:
about 10.0% wrong-mode consensus.

9 independent sensors:
about 0.20%.

9 sensors with strongly common-mode errors:
little benefit.

Cross-domain pattern:
the same partially-independent-redundancy requirement appeared previously in injury-cue research.

7.
dg1a-ar02-mode-identifiability-audit.ice

Major analytic correction:

AR-02 must NOT mean:
"infer every desired regime with no exogenous information."

If identical observation histories require different actions,
the desired objective is not identifiable from state alone.

Revised AR-02:

infer modes whose causes are observable.

Best first endogenous transition:
MAINTENANCE
<->
REPAIR

because injury has a real observable cause and existing Yggdrasil temporal wound-cue evidence.

Dormancy/reactivation remain exogenous/environment-coupled unless tied to a real observable variable such as:
resource state;
temperature;
energy;
threat;
external demand.

8.
dg1a-ar05-role-homeostasis-synthetic-poc.ice

Hard categorical local role quotas:
poor default.

3 x 3:
either chattering
or
ratio-resolution dead zones.

Soft role vectors:
better match to current Yggdrasil local perception.

Synthetic relay-role mass recovery using 3 x 3 local soft-role feedback:

50% ablation:
~47 steps

70%:
~47.5 steps

90%:
~215 steps

100%:
~325 steps

Important:
this restored a toy role fraction,
not real function.

9.
dg1a-ar05-seasonal-role-mixture-negative-audit.ice

Major negative:
do not map:

season
->
fixed global role histogram.

Neither:
- multiplicative soft-role updates;
- static plasticity floors;
- additive updates;
- 96..384-step dwell increases

produced reliable tracking of all six changing hand-declared role mixtures.

Interpretation:
global role quota is the wrong control object.

Roles should be selected from local functional demand.

10.
dg1a-ar05-utility-driven-relay-role-market-poc.ice

Strongest new synthetic precursor.

Role:
relay propensity.

Function:
reduce communication cost on a local graph.

No global relay quota.

Local signal:
message traffic handled by the cell.

Local cost:
relay energy/maintenance cost.

After selective removal of established relay mass:

50% loss:
damaged communication cost:
61.563

final adaptive:
29.389

median functional recovery:
36 steps

70%:
damaged:
69.060

final:
29.155

median:
38.5 steps

90%:
damaged:
78.292

final:
29.257

median:
40 steps

100%:
damaged:
83.333

final:
28.739

median:
37.5 steps

All tested severities:
100% recovery rate across 12 seeds.

Critical spatial-placement control:

randomly shuffle the exact recovered relay-propensity profile across cells.

Same total role mass and same values,
wrong positions.

Shuffled final communication cost:
about 46.5..48.6

Adaptive placement:
about 28.7..29.4

Therefore:
the mechanism restored FUNCTIONALLY USEFUL ROLE PLACEMENT,
not merely role quantity.

This remains:
SYNTHETIC PRECURSOR
not Yggdrasil functional regeneration.

LITERATURE ALIGNMENT

Neural Cellular Automata Can Respond to Signals
ALIFE 2023
DOI:
10.1162/isal_a_00567

Relevant:
single-cell / single-timestep signals can alter NCA collective behavior.

Learning spatio-temporal patterns with Neural Cellular Automata
PLOS Computational Biology
DOI:
10.1371/journal.pcbi.1011589

Relevant:
strict locality limits communication range;
stochastic updates reduce effective propagation distance.

Smart cellular bricks for decentralized shape classification and damage recovery
Nature Communications 17, 5932 (2026)
DOI:
10.1038/s41467-026-75166-7

Relevant:
- hundreds of locally communicating modules;
- global shape self-classification;
- local damage-direction inference;
- morphogen-like signal propagation;
- robustness to communication faults.

Structured Fluctuations and the Information Dynamics of Self-Maintenance in Growing Neural Cellular Automata
Entropy 28(8), 893 (2026)
DOI:
10.3390/e28080893

Relevant:
- repair-associated information dynamics;
- structured hidden fluctuations;
- redundancy changes during recovery;
- homeostatic local dynamics.

CURRENT ARCHITECTURAL READING

The emerging adaptive-rule architecture is NOT:

one rule forever

and also NOT:

a separate network per cell.

The strongest current direction is:

one compact shared developmental engine

+
small local continuous state

+
minimal environmental context when information is truly exogenous

+
endogenous predictive-error overrides

+
soft local role utility

+
distributed context consensus/relay when global broadcast is removed

+
later bounded heritable micro-genome adaptation.

IMPORTANT DISTINCTIONS

CONTEXT
answers:
what environmental/objective regime is currently valid?

STATE ESTIMATION
answers:
what is happening locally?

ROLE UTILITY
answers:
what function is useful for this cell to perform here?

META-RULE
answers:
how should the cell alter its sensitivity/plasticity based on consequences?

Do not collapse these into one mechanism.

NEW PRIMARY RESEARCH HYPOTHESIS

Useful functional specialization may emerge from:

local demand
+
local cost
+
local consequence

rather than:
explicit global role labels or quotas.

This is now better supported synthetically than the original fixed-ratio role-homeostasis concept.

NEXT RESEARCH ORDER — BEFORE REAL FUNCTIONAL REGENERATION

AR-U1 — MULTI-ROLE UTILITY MARKET
Extend the successful relay market to simultaneous:
- relay;
- repair;
- inhibitor;
- dormant;
- growth

utilities.

No fixed global role ratios.

Question:
can several useful soft roles coexist and relocate from local demand?

AR-U2 — MOVING DEMAND
Change communication/task demand after specialization.

Ask:
do roles relocate,
or does specialization become permanently canalized?

AR-U3 — NOISY / DELAYED CONSEQUENCE CREDIT
Corrupt local utility feedback.

Measure:
- stability;
- wrong specialization;
- recovery;
- chattering.

This is a precursor to meta-rules.

AR-U4 — LOCAL UTILITY ABLATION
Remove one utility cue while retaining others.

Ask:
which cues are actually necessary for functional recovery?

AR-C1 — REPEATED CONTEXT RELAY
Replace the single-transition freshness bit with a bounded repeated-switch ordering mechanism.

Must prevent:
stale-context overwrite.

AR-C2 — SENSOR / COMPONENT DAMAGE
Damage sensor cells and split organism components.

Measure:
which components retain or reacquire context?

AR-E1 — BOUNDED ADVERSARIAL ECOLOGY
Introduce a local competitor/toxin pressure only after the utility system is stable.

Look for:
- containment;
- sacrificial boundaries;
- dormancy;
- redundancy;
- specialized defense.

AR-M1 — META-RULE CREDIT
Allow bounded lifetime changes in role sensitivity based on local consequence.

Do not modify global shared weights.

THRESHOLD FOR MOVING TO REAL FUNCTIONAL REGENERATION
Before spending a real Yggdrasil functional-role experiment,
prefer evidence for ALL:

1. explicit context works;
2. context failure modes are understood;
3. local context propagation has a plausible fast mechanism;
4. endogenous versus exogenous mode information is cleanly separated;
5. soft roles can recover from depletion;
6. fixed global role quotas are rejected;
7. utility-driven functional role placement works synthetically;
8. multi-role utility does not collapse or chatter;
9. useful roles can relocate when task demand changes.

We now have evidence through item 7.

NEXT LIVE RESEARCH FRONTIER
AR-U1:
MULTI-ROLE UTILITY MARKET.

Do not execute canonical STAB-18-R1 during this lane.

PROVENANCE
evidence_class = RESEARCH_FRONTIER_SUMMARY
canonical_scientific_execution = false
canonical_r1_execution_spent = false
