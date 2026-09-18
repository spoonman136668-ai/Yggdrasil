TITLE: DG-1A-AR-01 — Explicit Seasonal Modes Synthetic Parameter-Matched Control
DATE: 2026-09-18
STATUS: SYNTHETIC POSITIVE FEASIBILITY RESULT — NOT A YGGDRASIL SCIENTIFIC RESULT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT_HEAD: b45703418a7097782a032a142665c4642c2945fa

PURPOSE
Before modifying Yggdrasil, test the minimum AR-01 claim:

Can one compact shared local neural rule express different local developmental policies when given a tiny explicit environmental mode signal, while an exactly parameter-count-matched fixed-rule control cannot?

BOUNDARY
This experiment:
- does not modify or execute STAB-18-R1;
- does not modify Yggdrasil implementation;
- does not spend the canonical R1 seed-0 / 200-iteration run;
- does not count as evidence that Yggdrasil itself can learn seasonal modes;
- does not establish endogenous mode inference, role switching, inheritance, ecology, or meta-learning.

EVIDENCE CLASS
SYNTHETIC

EXPERIMENT DESIGN
A compact shared MLP surrogate represented the local developmental engine.

Inputs:
- 8 local-state surrogate variables:
  support
  density
  boundary
  damage
  energy
  age
  stability
  recent_loss
- 6 mode/context channels

Modes:
1. EXPANSION
2. CONSOLIDATION
3. MAINTENANCE
4. REPAIR
5. DORMANCY
6. REACTIVATION

Outputs:
- growth / birth drive
- retention drive
- repair drive
- activity / update drive

Architecture for BOTH candidate and control:
14 -> 32 -> 32 -> 4
tanh hidden activations

Trainable parameter count for BOTH:
1668

CRITICAL PARAMETER-MATCHING CONTROL
Candidate:
receives the correct six-way one-hot seasonal context.

Fixed-rule control:
has the identical 14-input architecture and identical trainable parameter count, but all six context inputs are clamped to zero.

Therefore:
- same architecture;
- same parameter count;
- same initialization seed within each pair;
- same optimizer;
- same number of training samples;
- same training schedule;
- same held-out state distribution.

The only causal difference is access to the environmental mode signal.

SYNTHETIC LOCAL POLICY
The target local actions intentionally require different responses to overlapping local states.

Examples:
- EXPANSION favors growth and high activity;
- CONSOLIDATION favors retention and reduced growth;
- MAINTENANCE favors low churn;
- REPAIR favors damage/recent-loss-responsive repair;
- DORMANCY favors near-zero update activity and almost no growth;
- REACTIVATION restores high activity with bounded growth.

This creates the exact representational conflict AR-01 is intended to test:
the same local state can require different actions under different organismal regimes.

TRAINING
Seeds:
0..11

Per seed:
- 12,000 synthetic training states
- 5,000 held-out synthetic test states
- Adam
- learning rate 0.003
- 220 full-batch epochs

UNSEEN SWITCH TEST
Per seed:
- 3,000 fresh local states
- random source mode m1
- random distinct destination mode m2
- same local state evaluated before and after the mode switch

Measured:
predicted action delta versus true mode-conditioned action delta.

RESULTS — 12 MATCHED SEEDS

Overall held-out action MSE:
context candidate:
mean 0.004314
sd   0.000240
range 0.003832..0.004623

fixed-rule control:
mean 0.045966
sd   0.000619
range 0.044972..0.046751

Mean fixed/control MSE ratio:
10.680x

Range of per-seed fixed/control MSE ratio:
10.082x..11.737x

Paired MSE difference:
mean 0.041652

Paired t-test across the 12 matched seeds:
t = 311.906
df = 11
p approximately 4.62e-23

PER-MODE HELD-OUT MSE
Mode             context       fixed       fixed/context
EXPANSION        0.011336      0.069639      6.143x
CONSOLIDATION    0.002008      0.009421      4.692x
MAINTENANCE      0.001450      0.030516     21.046x
REPAIR           0.008125      0.047031      5.789x
DORMANCY         0.001895      0.082633     43.604x
REACTIVATION     0.001015      0.036621     36.068x

MODE-SIGNATURE DIAGNOSTIC
For each held-out state, compare the predicted four-action vector with the six possible mode-specific target vectors for that same state.

Nearest-target mode identification:
context candidate:
mean 97.698%

fixed-rule control:
mean 16.688%

Six-way chance level:
16.667%

Interpretation:
the fixed-rule control collapses toward an across-mode compromise;
the contextual candidate expresses distinct mode-conditioned local policies.

UNSEEN MODE-SWITCH DELTA
Normalized RMSE of predicted mode-switch action delta:
context candidate:
mean 0.301864
sd   0.004358

fixed-rule control:
1.000000 exactly

Fraction of true switch-delta second moment captured:
context candidate:
R2-like diagnostic mean 0.908861

fixed-rule control:
0.000000

The fixed-rule control cannot change its action for the same state when only the hidden regime changes, because it receives no regime information.

DORMANCY DIAGNOSTIC
Mean predicted activity/update drive on held-out DORMANCY states:

context candidate:
0.032246

fixed-rule control:
0.547423

Fixed/control ratio:
approximately 16.99x

This is a useful AR-01-specific signal because dormancy requires deliberately suppressing activity in local states that may otherwise resemble active regimes.

PRIMARY FINDING
The minimum AR-01 mechanism is viable in the synthetic control:

one shared fixed-weight local neural engine can express sharply different developmental regimes when given a tiny explicit context signal.

The parameter-matched fixed-rule control cannot resolve mutually incompatible regime demands from local state alone.

SCIENTIFIC INTERPRETATION
This is a feasibility sanity check, not a discovery.

The result is expected in information-theoretic terms:
if two otherwise identical local states require different actions, a rule that receives no variable correlated with regime cannot uniquely select the correct action.

What the experiment establishes is narrower and operationally useful:
- exact parameter matching is practical;
- the control design is discriminative;
- the seasonal context does not require a separate network per cell;
- the signal can drive large behavioral separation with a compact shared engine;
- AR-01 is worth preregistering in real Yggdrasil.

WHAT THIS DOES NOT ESTABLISH
It does not show:
- improved Yggdrasil morphology;
- successful real lesion repair;
- stable dormancy in a learned NCA rollout;
- reactivation after long quiescence;
- resistance to context noise;
- endogenous regime inference;
- generalization to unseen modes;
- emergent adaptation.

LITERATURE CONSISTENCY
The result is consistent with prior NCA work showing that shared local rules can be modulated by compact goal or external signals.

Relevant anchors:
- Goal-Guided Neural Cellular Automata (Sudhakaran, Najarro, Risi, 2022): goal encodings control NCA behavior dynamically.
- Neural Cellular Automata Can Respond to Signals (Stovold, 2023): internal/external signals can alter NCA morphogenesis or appearance.
- Conditional Morphogenesis (Sakour, 2025): a broadcast class condition can select among multiple structural attractors in a single conditional NCA.

These references support feasibility only.
They do not substitute for the AR-01 Yggdrasil control.

DECISION
PASS SYNTHETIC FEASIBILITY GATE.

Proceed to preregister AR-01 — Explicit Seasonal Modes on the isolated adaptive-rule branch.

Do not modify or execute R1.

NEXT
Create:
research/experiments/dg1a/adaptive/dg1a-ar01-explicit-seasonal-modes-spec.ice

Then implement only the minimum AR-01 context-conditioning path required by that preregistration, preserving an exactly parameter-count-matched fixed-rule control.

PROVENANCE
evidence_class = SYNTHETIC
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
synthetic_seeds = 12
synthetic_train_samples_per_seed = 12000
synthetic_test_samples_per_seed = 5000
synthetic_switch_samples_per_seed = 3000
trainable_parameters_per_model = 1668
parameter_count_matched = true
