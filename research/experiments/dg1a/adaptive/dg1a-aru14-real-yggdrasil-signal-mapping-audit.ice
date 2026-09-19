TITLE: DG-1A-AR-U14 — Real-Yggdrasil Signal Mapping / Observability Audit
DATE: 2026-09-18
STATUS: ANALYTIC / SOURCE-AUDIT BRIDGE — NO NEW TRAINING
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-adaptive-research-frontier-r4-20260918.ice

PURPOSE
Map the synthetic adaptive-rule variables from AR-U1..U12 onto signals that the CURRENT Yggdrasil implementation can actually produce.

Primary question:

CAN CURRENT YGGDRASIL LATENT DYNAMICS SUPPLY
THE LOCAL INFORMATION VARIABLES
THAT THE SYNTHETIC META-RULES REQUIRE?

This audit is deliberately prior to:
- explicit role registers;
- lifetime meta-rule implementation;
- functional-regeneration execution.

BOUNDARY
This audit:
- does not modify source;
- does not execute STAB-18-R1;
- does not train a new candidate;
- does not reserve hidden channels;
- does not claim latent variables exist merely because they are measurable externally.

EVIDENCE
ANALYTIC
SOURCE_AUDIT
HISTORICAL_MEASURED_SANDBOX_CONTEXT where explicitly identified

CURRENT NCA STATE
Source:
src/yggdrasil/nca.py

State width:
16 channels

Canonical R1 visible:
0..3

Canonical R1 LIFE4:
4

Other latent channels:
5..15
= 11 channels

Shared perception:
for every one of 16 state channels:
- identity;
- Sobel x;
- Sobel y.

Total local perception width:
16 x 3
= 48 features.

The same shared local update network is used for every cell.

CURRENT UPDATE PIPELINE
For each step:

1.
pre_alive =
3 x 3 max-pooled thresholded alive channel

2.
perception =
identity / Sobel x / Sobel y
over all state channels

3.
raw_delta =
update_net(perception)

4.
stochastic fire mask
with canonical fire rate 0.5

5.
masked delta

6.
next_state_raw =
state + masked delta

7.
post_alive =
3 x 3 max-pooled alive mask
from next_state_raw

8.
returned state =
next_state_raw
*
(pre_alive AND post_alive)

This ordering matters for signal mapping.

MAPPING 1 — LOCAL PERCEPTION
SYNTHETIC VARIABLE
local state / local context evidence

CURRENT YGGDRASIL OBSERVABLE
YES.

Direct read-only quantity:
model.perceive(state)

Contains:
- local channel values;
- horizontal local gradients;
- vertical local gradients.

No source change is needed for an observational diagnostic.

STATUS
DIRECTLY OBSERVABLE TO ANALYST
AND
ALREADY CONSUMED BY THE SHARED CELL RULE.

MAPPING 2 — INTENDED LOCAL ACTION
SYNTHETIC VARIABLE
what local action did this cell attempt?

CURRENT YGGDRASIL OBSERVABLE
YES TO ANALYST.

Read-only diagnostic can compute:

raw_delta =
model.update_net(
    model.perceive(state)
)

before stochastic fire masking.

This is the exact deterministic update proposal from the shared local rule for the current state.

STATUS
DIRECTLY RECONSTRUCTABLE IN DIAGNOSTIC.

IMPORTANT
The cell state itself does not currently retain:
"my last raw_delta"

as an explicit eligibility/action tag.

Therefore:
ANALYST OBSERVABILITY
does not imply
ONLINE CELL MEMORY.

MAPPING 3 — REALIZED LOCAL ACTION
SYNTHETIC VARIABLE
what actually changed?

CURRENT YGGDRASIL OBSERVABLE
YES.

From a recorded trajectory:

realized_delta =
state[t+1] - state[t]

However realized_delta mixes:
- intended update;
- fire-mask gating;
- alive/death gating.

Therefore it is NOT equivalent to raw_delta.

EXACT DIAGNOSTIC FIRE MASK
Because NCA.step samples the fire mask from an explicit torch.Generator,
a read-only diagnostic can:

1.
clone generator state immediately before step;
2.
sample the same random field from a temporary generator;
3.
reconstruct the exact fire mask;
4.
execute the real step with the untouched original generator.

This allows exact analyst-level separation of:

raw intended update
from
stochastic execution.

No model source mutation is required.

STATUS
EXACTLY RECONSTRUCTABLE OFFLINE.

ONLINE ACTION TAG
NOT PRESENT.

MAPPING 4 — LOCAL TEMPORAL STATE DELTA
SYNTHETIC VARIABLE
recent local change / temporal evidence

CURRENT YGGDRASIL OBSERVABLE
YES.

The existing latent-injury diagnostic already preregisters:
- per-channel update RMS;
- local state-change magnitudes;
- lag-1 temporal autocorrelation;
- regional post-lesion dynamics.

Complete state recording is already scientifically compatible with current diagnostic practice.

STATUS
DIRECTLY OBSERVABLE.

MAPPING 5 — LOCAL INJURY / NOVELTY EVIDENCE
SYNTHETIC VARIABLE
unexpected local state-transition violation

CURRENT YGGDRASIL OBSERVABLE
PARTIALLY.

Existing preregistered R1 latent diagnostic already plans:
- per-channel injury ROC AUC;
- pooled multi-channel injury AUC;
- EnsembleGain;
- maintenance covariance;
- participation ratio;
- effective cue-count diagnostic;
- spatial response around lesion.

Therefore Yggdrasil already has a frozen diagnostic path to test:

does latent state contain distributed injury information?

STATUS
PREREGISTERED OBSERVATIONAL TEST EXISTS.

NOT YET MEASURED ON CANONICAL R1
because R1 remains unexecuted.

MAPPING 6 — LOCAL DISTURBANCE REFERENCE
SYNTHETIC VARIABLE
what changed locally that was probably shared/environmental rather than caused by my action?

CURRENT YGGDRASIL RAW MATERIAL
YES.

Candidate raw observations:
- neighbor state deltas;
- neighbor hidden-channel deltas;
- local 48-feature perception field;
- neighborhood covariance;
- temporal covariance across nearby cells.

BUT:
a valid causal control is NOT guaranteed.

CRITICAL SOURCE-DERIVED CAUSAL-CONE RESULT

The update network sees a Chebyshev-radius-1 neighborhood.

Additionally:
post_alive at cell j depends on next_state_raw in a radius-1 neighborhood.

Each next_state_raw[k] already depends on the prior state within radius 1 around k.

Therefore one prior local perturbation can structurally influence the returned state out to:

Chebyshev radius <= 2
after one complete NCA step

through the post-alive gating path.

Conservative full-state causal support bound:

radius <= 2H
after H steps.

At the existing causal horizon:

H = 16

conservative bound:
radius <= 32.

The canonical grid is:
40 x 40.

Therefore a strict same-organism reference guaranteed to be action-decoupled for a 16-step horizon may not exist for many cell positions.

THIS IS IMPORTANT.

It means AR-U10..U12:
- action-leakage estimation;
- freshness/confidence;
- recalibration

are likely not optional conveniences when mapped to the real NCA.

Nearby cells can be:
DISTURBANCE-COUPLED
but also
ACTION-EXPOSED.

STATUS
RAW REFERENCE SIGNALS AVAILABLE.
VALID CONTROL NOT GUARANTEED.

MAPPING 7 — ACTION LEAKAGE
SYNTHETIC VARIABLE
how much did my action contaminate the local disturbance representation?

CURRENT YGGDRASIL SUPPORT
PARTIAL.

Current R1 source already contains:
- domain-separated pseudorandom probe construction;
- explicit probe mask;
- latent intervention;
- intact future;
- counterfactual future;
- per-sample causal delta.

This proves the codebase can perform controlled read-only causal interventions at evaluation/training-analysis time.

However:
current R1 probe is a group latent-dropout mechanism,
not a cell-lifetime role-action leakage estimator.

STATUS
CAUSAL-PROBE INFRASTRUCTURE EXISTS.
ONLINE LOCAL LEAKAGE ESTIMATE DOES NOT.

MAPPING 8 — LOCAL CONSEQUENCE
SYNTHETIC VARIABLE
did my recent action improve something locally useful?

CURRENT YGGDRASIL
NO ACCEPTED ENDOGENOUS LOCAL CONSEQUENCE VARIABLE YET.

AVAILABLE BUT INVALID FOR LIFETIME SELF-CREDIT
Target-based morphology losses exist:
- global morphology MSE;
- foreground morphology MSE;
- background alpha MSE;
- ATTRACT-16 future visible loss.

These use experimenter target geometry.

They are valid scientific/training objectives.

They are NOT acceptable as a future organism-local consequence signal if the goal is autonomous developmental adaptation,
because giving the cell target loss would leak global supervision.

DIRECT TARGET-FREE CANDIDATES
Current trajectories can provide:
- local state persistence;
- LIFE4 survival;
- local birth/death/turnover;
- local visible-state change;
- local hidden-state change;
- neighborhood support change;
- temporal predictability.

NONE IS YET VALIDATED AS:
"local functional utility."

CRITICAL HISTORICAL WARNING
STAB-16 / STAB-17 show that:
more persistence
or
more structure

is not automatically more useful.

Historical MEASURED_SANDBOX examples:

STAB-16:
pre-damage LIFE4 count 1082
post-damage 795
final recovery 797

and damage improved visible morphology.

STAB-17:
pre-damage 1038
post-damage 650
final recovery 681

and damage again improved visible morphology.

Therefore a consequence proxy such as:
"preserve more living support"

can reinforce harmful/redundant substrate.

STATUS
MAJOR UNSOLVED MAPPING.

MAPPING 9 — LOCAL PREDICTION RESIDUAL
SYNTHETIC VARIABLE
unexpected state transition

CURRENT YGGDRASIL
NOT EXPLICITLY STORED.

Important distinction:

raw_delta from update_net
is the rule's proposed action.

It is not an independent prediction of:
what the environment would have done without the action.

Comparing:
raw_delta
to
realized_delta

would mainly reflect:
- fire masking;
- life gating;
- interaction effects;

not necessarily useful environmental surprise.

Therefore:
CURRENT UPDATE NETWORK OUTPUT
must not automatically be reinterpreted as a forward model.

A separate diagnostic predictor or latent predictive state must be justified.

STATUS
DERIVABLE RESEARCH TARGET
NOT CURRENTLY AN ACCEPTED SIGNAL.

MAPPING 10 — CONFIDENCE / FRESHNESS
SYNTHETIC VARIABLE
how trustworthy is my current model/calibration/evidence?

CURRENT YGGDRASIL
NO EXPLICIT CONFIDENCE VARIABLE.

Possible observational proxies:
- prediction residual variance;
- disagreement across hidden channels;
- local covariance shift;
- novelty z-score relative to maintenance;
- age/freshness since last tagged perturbation.

Existing latent diagnostic provides maintenance baselines and z-scores,
which are sufficient for OFFLINE confidence research.

But there is no current persistent online confidence state.

STATUS
OFFLINE DERIVABLE.
ONLINE STATE ABSENT.

MAPPING 11 — SOFT FUNCTIONAL ROLE
SYNTHETIC VARIABLE
relay / repair / inhibitor / growth / dormant role expression

CURRENT YGGDRASIL
NO EXPLICIT ROLE REGISTER.

This is scientifically desirable at this stage.

Channels 5..15 remain free latent state.

Do NOT assign:
channel 5 = relay
channel 6 = repair
etc.

Instead test whether functional specialization is already latent.

Candidate observational methods:
- cluster local latent/perception trajectories;
- decode future local response from hidden state;
- identify spatially stable functional subpopulations;
- selectively perturb latent-state-defined groups;
- test whether perturbation affects a specific function more than matched controls.

STATUS
POTENTIALLY EMERGENT.
NOT YET DEMONSTRATED.

MAPPING 12 — ENVIRONMENTAL CONTEXT
SYNTHETIC VARIABLE
season / exogenous objective context

CURRENT YGGDRASIL
ABSENT FROM CURRENT NCA INPUT.

AR-01 is preregistered but unexecuted.

Therefore:
explicit seasonal conditioning still requires an architecture/input-path experiment.

STATUS
NOT PRESENT.

OBSERVABILITY MATRIX

VARIABLE:
local perception
ANALYST NOW:
YES
CELL RULE NOW:
YES

raw intended update
ANALYST NOW:
YES
CELL MEMORY:
NO

realized update
ANALYST NOW:
YES
CELL MEMORY:
implicit in next state only

fire/update identity
ANALYST NOW:
YES with generator reconstruction
CELL MEMORY:
NO

temporal local delta
ANALYST NOW:
YES
CELL RULE:
only current state/perception unless latent memory learned

injury discriminability
ANALYST:
preregistered
MEASURED CANONICAL R1:
NO

neighbor disturbance evidence
ANALYST:
YES
VALID ACTION-DECOUPLED CONTROL:
UNKNOWN / often impossible at long horizon

action leakage
ANALYST:
causal infrastructure exists
ONLINE:
NO

local target-free consequence
ANALYST:
candidate proxies exist
VALIDATED:
NO

prediction residual
ANALYST:
can be constructed with auxiliary model
CURRENT LATENT VARIABLE:
UNKNOWN

confidence/freshness
ANALYST:
derivable
CURRENT ONLINE STATE:
NO

soft functional role
ANALYST:
can search for latent specialization
EXPLICIT REGISTER:
NO

seasonal context
CURRENT ARCHITECTURE:
NO

MINIMAL REAL-YGGDRASIL DIAGNOSTIC
Before engineering adaptive-rule state,
run a NON-GATING observational signal-availability diagnostic.

It should require no new training.

INPUT
A saved trained checkpoint.

Prefer:
canonical R1 only after canonical classification is complete,
because the existing latent diagnostic is already frozen around that checkpoint.

Historical sandbox checkpoints may be used only as:
MEASURED_SANDBOX exploratory diagnostics
if their actual checkpoint bytes are available and identity is verified.

The repository currently records checkpoint hashes for STAB-16 and STAB-17,
but their checkpoint bytes are not stored in the Git tree inspected by this audit.

Therefore this ChatGPT/GitHub lane cannot execute a real-state signal diagnostic from repository contents alone.

Do not fabricate latent measurements.

REQUIRED TELEMETRY PER STEP

1.
full state 0..15

2.
48-feature perception

3.
raw_delta before fire mask

4.
reconstructed fire mask

5.
masked proposed delta

6.
pre_alive

7.
post_alive

8.
realized returned-state delta

9.
local neighbor state/update covariance

10.
distance-to-lesion metadata for analysis only

11.
RNG state / deterministic seed provenance

DERIVED DIAGNOSTICS

A. ACTION IDENTIFIABILITY
Can raw_delta / realized_delta be represented from existing latent state with short memory?

B. INJURY / NOVELTY
Use the already preregistered latent-injury AUC / EnsembleGain protocol.

C. DISTURBANCE STRUCTURE
For each cell:
how much of its state-change variance is predictable from nearby non-self cells?

D. ACTION LEAKAGE
After a domain-separated local/group perturbation:
how far and how fast does perturbation-correlated response spread?

Report:
response vs Chebyshev radius
for horizons:
1
2
4
8
16.

E. CONTROL-CANDIDATE QUALITY
For each candidate neighbor/ring/module reference:
measure BOTH:

shared-disturbance predictability

and

action-leakage sensitivity.

Do not select controls from correlation alone.

F. LOCAL CONSEQUENCE CANDIDATES
Test target-free candidates against an external diagnostic label:

does the candidate correlate with:
future improvement in visible morphology
WITHOUT being given target geometry as an input?

The external target may be used to SCORE the diagnostic relationship.

It must not be fed into the candidate local signal.

Candidates:
- LIFE4 survival;
- local visible stability;
- local hidden-state predictability;
- local neighbor-consistency improvement;
- future reduction in local state-transition residual.

G. ROLE-LIKE LATENT ORGANIZATION
Fit simple held-out decoders/clusters using channels 5..15 and perception.

Question:
do any stable latent subpopulations predict distinct local causal contributions?

Do not name a role unless selective perturbation supports the functional label.

H. CONFIDENCE PROXY
Test whether:
maintenance-relative z-score
+
multi-channel disagreement
+
prediction residual variance

predicts when:
- injury classification is unreliable;
- disturbance-control calibration is stale;
- perturbation causal-sign estimates disagree.

PRIMARY DECISION AFTER DIAGNOSTIC

BRANCH U14-A
Existing latent state already carries:
- action-relevant memory;
- useful local consequence proxy;
- confidence/novelty structure.

Then:
prefer decoding/modulating existing state over adding explicit registers.

BRANCH U14-B
Injury/novelty exists,
but action/consequence identity does not.

Then:
add the smallest eligibility/action-memory mechanism,
not full explicit role registers.

BRANCH U14-C
Current latent dynamics lack usable local consequence structure.

Then:
the adaptive-rule bridge requires an architectural/training change before functional regeneration.

Do not force the synthetic meta-rule onto an information-poor substrate.

PRIMARY FINDING
Current Yggdrasil is NOT blocked by lack of raw observability.

It already exposes enough trajectory/perception/action information for a rigorous read-only diagnostic.

The unresolved bridge is:

SEMANTIC LOCAL CREDIT

not:

STATE ACCESS.

SECOND FINDING
The real NCA's local causal cone is large enough over 16 steps that same-organism disturbance controls are intrinsically vulnerable to action leakage.

This strongly validates the need to carry forward:
- action identity;
- leakage calibration;
- freshness/confidence;
- event-triggered recalibration.

THIRD FINDING
The existing R1 latent diagnostic and adaptive-rule research should be joined diagnostically,
not by changing R1.

R1 latent analysis can answer:
is injury/novelty information already distributed across hidden channels?

AR-U14 adds:
can that same state support action identity, disturbance separation, and target-free local consequence?

NEXT RESEARCH
AR-U13 — SHARED NOVELTY / CONFIDENCE COMPRESSION
can one compact confidence gate control:
- injury escalation;
- context disagreement;
- causal-calibration recalibration
without erasing event identity?

AND/OR

AR-U14-DIAG — exact non-gating telemetry preregistration
for execution only after a verified checkpoint is available.

Do not execute STAB-18-R1 in this lane.

PROVENANCE
evidence_class = ANALYTIC_SOURCE_AUDIT
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
source_branch_audited = dg1a-ar
source_files_audited =
src/yggdrasil/nca.py
src/yggdrasil/training.py
src/yggdrasil/metrics.py
historical_sandbox_evidence =
STAB-16
STAB-17
