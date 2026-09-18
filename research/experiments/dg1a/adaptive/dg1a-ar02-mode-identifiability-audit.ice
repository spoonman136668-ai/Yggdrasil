TITLE: DG-1A-AR-02 — Endogenous Mode Identifiability Audit
DATE: 2026-09-18
STATUS: ANALYTIC RESEARCH AUDIT — AR-02 SCOPE CORRECTION
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: DG-1A-AR-01 Explicit Seasonal Modes

PURPOSE
Determine which AR-01 regime switches can, in principle, be inferred from endogenous/local state and which require some genuinely exogenous information.

This audit prevents AR-02 from becoming an impossible requirement:
"remove the explicit mode signal even when the desired objective changes without any observable cause."

EVIDENCE
ANALYTIC
with literature-supported feasibility anchors.

CORE IDENTIFIABILITY RESULT
Let:
H = all local observation/history available to the shared rule
M = desired mode
A*(H,M) = desired action

Suppose there exist two modes:
M1
M2

such that for a set of histories H:

P(H | M1) = P(H | M2)

but:

A*(H,M1) != A*(H,M2)

Then no policy of the form:

A = f(H)

can perfectly implement both objectives.

The missing mode information is not recoverable from H.

BALANCED TWO-MODE LOWER BOUND
If M1 and M2 are equally likely and induce the identical observation history H:

best possible mode classification accuracy from H alone:
50%

For squared action loss with desired action vectors:
a
b

the optimal state-only compromise is:
(a+b)/2

and the irreducible expected squared Euclidean loss is:

||a-b||^2 / 4

For mean-squared error across D action components:

||a-b||^2 / (4D)

This is the mathematical reason a parameter-count-matched fixed-rule control collapses toward an across-mode compromise when the same state requires different actions.

MODE-BY-MODE IDENTIFIABILITY

EXPANSION
Potentially inferable when:
- morphology is clearly underdeveloped;
- resources permit growth;
- state history indicates active construction.

Not identifiable from internal state alone when:
the exact same undergrown state is intentionally ordered to remain dormant.

Therefore:
EXPANSION is only endogenous if the environment/state contains a growth-permission cue.

CONSOLIDATION
Potentially inferable from:
- late-development state;
- high turnover;
- near-target morphology;
- overgrowth/redundancy indicators;
- diminishing improvement.

But an arbitrary timed switch from EXPANSION to CONSOLIDATION is not inferable if nothing observable changes.

Therefore:
consolidation should eventually be triggered by a measurable saturation/homeostasis signal, not by an invisible clock objective.

MAINTENANCE
Potentially inferable from:
- stable morphology;
- low predictive error;
- mature occupancy;
- low recent damage;
- stable latent dynamics.

Maintenance is one of the most naturally endogenous regimes.

REPAIR
Strongly suitable for endogenous inference.

Existing Yggdrasil contingency research already supports:
- temporal information distinguishes acute wound boundaries from stable exterior boundaries;
- multi-cue predictive error is the preferred injury-state hypothesis;
- purely static LIFE4 geometry is insufficient.

The desired future trigger is:
unexpected local state-transition violation
across multiple partially independent cues
->
transient repair state.

REPAIR should therefore become an endogenous override candidate.

DORMANCY
NOT identifiable if dormancy is merely an arbitrary external season.

Example:
same mature intact state
same local history
same resource state
same environment

Desired action A:
MAINTAIN

Desired action B:
DORMANT

No endogenous rule can know which objective was intended.

Dormancy becomes inferable only if it corresponds to observable conditions such as:
- resource scarcity;
- temperature/environment change;
- missing external activity cue;
- energy depletion;
- threat state;
- explicit environmental season signal.

Therefore:
AR-02 must not demand endogenous dormancy without an observable cause.

REACTIVATION
Same problem as dormancy.

A dormant organism cannot infer that it should reactivate if:
- all local/internal state is unchanged;
- all environmental inputs are unchanged;
- only an external experimenter's intention changed.

Reactivation becomes endogenous only when an observable transition occurs:
- resources return;
- temperature changes;
- signal returns;
- environmental demand appears;
- damage/resource state crosses a learned threshold.

LITERATURE FEASIBILITY ANCHOR 1
Smart cellular bricks for decentralized shape classification and damage recovery
Nature Communications 17, 5932 (2026)
DOI:
10.1038/s41467-026-75166-7

The distributed NCA:
- uses only local neighbor communication and memory;
- reaches high global shape classification accuracy;
- predicts local damage direction with reported average accuracy of 94.8%;
- exhibits morphogen-like signal propagation during collective classification.

This supports the proposition that:
global/self-state information and damage information can become locally inferable through recurrent local communication.

It does NOT imply arbitrary external goals can be inferred.

LITERATURE FEASIBILITY ANCHOR 2
Neural Cellular Automata Can Respond to Signals
ALIFE 2023
DOI:
10.1162/isal_a_00567

This shows external information can be introduced sparsely and affect collective behavior.

Together these two lines suggest a hybrid architecture:
some modes inferred endogenously;
some objectives supplied by environment;
both expressed through the same shared local rule.

REVISED AR-02 HYPOTHESIS
Do NOT define AR-02 as:
"remove the explicit season flag and infer all six modes."

Define the stronger scientifically coherent question as:

Can the organism infer MODE TRANSITIONS whose causes are actually observable,
while retaining minimal exogenous input for objective changes that are not state-identifiable?

PREFERRED HYBRID CONTROL

EXOGENOUS / ENVIRONMENTAL
- true seasonal/resource context;
- externally imposed objective changes;
- reactivation cue when no internal cue exists.

ENDOGENOUS
- injury/repair override;
- consolidation from saturation;
- maintenance from stable low-error dynamics;
- dormancy/reactivation only when associated with real observable environmental/resource state.

This is not a retreat from adaptive rules.

It is a separation between:
CONTROL INFORMATION
and
STATE ESTIMATION.

AR-02 SHOULD TEST FIRST
The first endogenous-mode experiment should be:

MAINTENANCE
vs
REPAIR

because:
- their distinction has a concrete observable physical cause;
- Yggdrasil already has temporal wound-cue evidence;
- the same organism can be evaluated before and after lesion;
- no arbitrary hidden objective is required.

Candidate question:

Can local temporal predictive-error cues trigger a repair-mode modulation strongly enough to improve recovery while remaining inactive during intact maintenance?

SECOND AR-02 TEST
CONSOLIDATION
vs
EXPANSION

but only after defining an observable saturation signal.

Do not use an invisible schedule transition.

DORMANCY / REACTIVATION
Keep explicit/environment-coupled until a real environmental variable is chosen.

HARD NEGATIVE
A completely state-only controller cannot implement arbitrary contradictory policies on identical histories.

No amount of model capacity fixes missing information.

Therefore:
do not spend experimental effort trying to make a network infer an unobservable experimenter intention.

DECISION
AR-02 roadmap correction:

OLD:
remove explicit season flag globally.

NEW:
remove explicit mode control only for transitions with observable endogenous/environmental causes.

Priority:
1. endogenous MAINTENANCE <-> REPAIR inference;
2. endogenous EXPANSION -> CONSOLIDATION when saturation cues are defined;
3. environmentally grounded DORMANCY <-> REACTIVATION;
4. retain explicit minimal context for irreducibly exogenous objectives.

PROVENANCE
evidence_class = ANALYTIC
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
