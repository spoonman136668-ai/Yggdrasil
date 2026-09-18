TITLE: DG-1A-P0-STAB-18-R1 — LIFE4 Gradient-Topology / Repair-Asymmetry Audit
DATE: 2026-09-18
STATUS: PRE-EXECUTION CODE-BACKED MECHANISTIC AUDIT — NOT A CANDIDATE RESULT
TRACK: DG-1A
PARENT_CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

PURPOSE
Explain why damage-conditioned population recruitment collapsed after LIFE4 decoupling even though regeneration examples remain present in training, and determine how that mechanism should affect interpretation of frozen STAB-18-R1.

THIS RECORD DOES NOT
- change or execute STAB-18-R1;
- prove that gradient topology is the sole cause of the observed recruitment gap;
- add a repair controller;
- change the 113 floor or 800 ceiling;
- authorize coefficient tuning;
- preregister STAB-19.

FROZEN SOURCE INSPECTED
Scientific implementation lineage:
e7710a29768ebc852a19796ea42eba4c10629412

Current branch source blobs inspected:
src/yggdrasil/nca.py
blob 7b15017b7f5c6f9b507bcf43f4545a3c972f40d1

src/yggdrasil/training.py
blob af610c4334d2dd16415b39dd344ae2ed82ddd931

src/yggdrasil/damage.py
blob 79dc0aa64deeac6597da259444387a6e488b7d1a

OBSERVATION 1 — DAMAGE TRAINING IS ALREADY PRESENT
TrainingConfig defaults:
- variant supports regeneration
- damage_probability = 0.5
- damage_height_fraction = 0.35
- damage_width_fraction = 0.35
- damage_min_active_cells = 16
- rollout length = 64..96 steps

In regeneration training:
- states are sampled from the persistent pool;
- states[0] is reset to the seed;
- with probability 0.5, eligible sampled candidates receive center_lesion;
- center_lesion zeros all state channels inside the lesion;
- the damaged states then undergo the normal 64..96-step NCA rollout;
- the resulting states receive the training objective and return to the pool.

Therefore the STAB-16/17 recovery deficit is not adequately explained by lack of damaged training examples.

OBSERVATION 2 — LIVENESS IS A HARD, NONDIFFERENTIABLE GATE
NeuralCellularAutomaton.alive_mask:
- takes model.config.alive_channel;
- 3x3 max-pools that channel;
- compares the result to alive_threshold with a hard boolean > test.

NeuralCellularAutomaton.step:
- computes pre_alive;
- computes the learned delta;
- applies stochastic fire mask;
- forms next_state = state + delta;
- computes post_alive;
- forms living = pre_alive & post_alive;
- returns next_state * living.

The hard threshold itself carries no derivative.

A frontier dead cell can still be updated while it lies inside the live neighborhood, but the learning system receives no derivative for the discrete fact:
"if LIFE4 crosses 0.1 here, this site becomes a new source of future liveness."

That threshold-crossing value must be learned indirectly unless an explicit surrogate provides it.

OBSERVATION 3 — PRE-DECOUPLING ALPHA PROVIDED A DIRECT GRADIENT BRIDGE
Before LIFE4 decoupling:
alive_channel = visible alpha channel 3.

The same continuous scalar therefore had two roles:
1. visible target morphology variable;
2. liveness variable used by the hard gate.

Foreground/background morphology losses directly optimized alpha.
Although the hard alive threshold was itself nondifferentiable, visible-alpha training pressure acted directly on the same scalar whose threshold controlled life.

This creates an incidental gradient bridge:
visible morphology objective
-> alpha magnitude
-> probability of crossing/maintaining the liveness threshold through learned updates
-> continued developmental support.

The historical recovery series is consistent with a strong injury-responsive population process under this coupled representation.

OBSERVATION 4 — LIFE4 REMOVED THAT DIRECT BRIDGE
After LIFE4 decoupling:
- visible morphology remains channels 0..3;
- liveness becomes hidden channel 4;
- target channel 4 is zero / has no direct life target;
- morphology losses remain visible-only.

Therefore direct visible target error does not itself provide a first-order loss derivative on the LIFE4 state scalar.

Any useful positive LIFE4 recruitment must arise through:
- recurrent multi-step consequences of LIFE4 on later visible state;
- shared learned dynamics;
- or explicit LIFE4 surrogate losses.

This is a much longer and less direct credit path than the pre-decoupled alpha/liveness path.

OBSERVATION 5 — THE EXPLICIT POSITIVE LIFE4 SURROGATE IS A STATIC FLOOR
FRONTIER-FLOOR-113:
- identifies currently dead cells in the immediate 3x3 hard-life frontier;
- uses a straight-through correction on LIFE4 values at those frontier cells;
- applies a one-sided deficit loss only when hard LIFE4 count is below 113.

Exact structural form:
normalized_deficit =
ReLU(113 - STE_life_count) / 113

Thus, when hard LIFE4 count >=113:
- forward floor loss = 0;
- positive floor gradient = 0.

Measured canonical recovery starts:
- STAB-16 post-lesion LIFE4 = 795
- STAB-17 post-lesion LIFE4 = 650

The positive frontier surrogate is therefore inactive at the beginning of both recovery trajectories.

OBSERVATION 6 — R1 ADDS DOWNWARD CREDIT WITHOUT ADDING REPAIR-UPWARD CREDIT
Frozen STAB-18-R1 retains:
- visible morphology objective;
- ATTRACT-16;
- CEIL-800;
- FRONTIER-FLOOR-113.

It adds:
- 25% domain-separated latent intervention;
- future visible-loss comparison;
- one-sided causal prune pressure on probed hard-live LIFE4 cells when removing the probe does not worsen future visible loss.

The prune term provides a direct straight-through LIFE4 gradient on selected nonbeneficial mature cells.

Therefore above the 113 floor the explicit LIFE4 resource-control system is asymmetric:

DOWNWARD
- CEIL-800 above the ceiling;
- R1 causal prune on selected nonbeneficial mature LIFE4;
- hidden-state L2 remains contractive.

UPWARD
- FRONTIER-FLOOR-113 only below 113;
- otherwise no explicit positive LIFE4 recruitment surrogate.

Visible target loss can still influence LIFE4 indirectly through recurrent dynamics, so the upward path is not mathematically absent.
It is, however, substantially less direct than the explicit downward surrogates.

EMPIRICAL CONSISTENCY
This code-level asymmetry matches the measured architectural discontinuity.

Pre-decoupling viable STAB-07..14:
- median removed-population restoration after lesion = 92.13%
- minimum = 32.85%

Decoupled LIFE4:
- STAB-16 = 0.70%
- STAB-17 = 7.99%

Both decoupled post-lesion populations lie inside the historical pre-decoupling post-lesion occupancy range, so remaining population size does not explain the discontinuity well.

STAB-15 provides the complementary extreme:
without FRONTIER-FLOOR-113, hidden life repeatedly collapsed toward zero.
This demonstrates that the indirect visible-morphology path alone was insufficient to sustain LIFE4 under the tested objective.

MECHANISTIC HYPOTHESIS
LIFE4 decoupling solved a representational problem:
visible phenotype no longer has to equal the set of living computational cells.

But it simultaneously removed an accidental training advantage:
visible morphology error no longer supplies direct continuous pressure to the liveness scalar.

FRONTIER-FLOOR-113 repaired baseline viability but only as a static minimum-population mechanism.

The current architecture therefore learns:
"do not die below 113"
and
"remove excess/nonbeneficial mature LIFE4"

more explicitly than it learns:
"after injury, temporarily recruit useful LIFE4 even though total life remains above 113."

This is a plausible explanation for the measured maintenance/repair asymmetry.

RELATION TO THE 2026 GNCA LITERATURE
Recent GNCA work reports:
- spatially structured hidden-state dynamics;
- damage-induced departure from and return toward a collective attractor;
- spatially differentiated local correction and distal information broadcasting;
- increased redundancy during recovery relative to resting maintenance.

That literature supports the general expectation that repair can be a distinct dynamical regime rather than ordinary maintenance with fewer cells.

It does not establish that Yggdrasil requires any specific repair signal.

R1 INTERPRETATION CONSEQUENCE
The frozen R1 experiment remains necessary and must remain unchanged.

But its outcomes should now be interpreted on two separate axes:

AXIS A — MAINTENANCE RESOURCE QUALITY
Does causal pruning reduce harmful/redundant LIFE4 and improve occupancy/morphology?

AXIS B — REPAIR RECRUITMENT
After lesion, does the architecture re-expand useful LIFE4 and produce a valid positive damage/recovery trajectory?

A plausible R1 result is:
- Axis A improves;
- Axis B remains failed.

That would not invalidate causal pruning.
It would indicate that maintenance economy and injury recruitment require different learned control signals.

PROSPECTIVE REPAIR-SEAM REQUIREMENTS — NOT A SELECTED CANDIDATE
Only if R1 supports the need for a repair mechanism, the next mechanism class should provide a training signal that:
- is conditional on injury/state change rather than absolute count alone;
- acts locally or propagates through the shared local rule;
- can provide positive LIFE4 frontier credit while global LIFE4 remains above 113;
- is inactive during undamaged maintenance;
- does not use a permanently higher global floor;
- does not simply restore all pre-lesion cells or pre-lesion overgrowth;
- preserves autonomous contraction after repair;
- does not require a runtime global controller or target mask.

A training-time lesion-conditioned surrogate may be scientifically cleaner than another global occupancy objective because the existing training pipeline already knows which examples were experimentally damaged while the runtime NCA remains a shared local rule.

No exact surrogate, coefficient, duration, or geometry is selected here.

CONCLUSION
The current evidence supports a sharper architecture decomposition:

VISIBLE MORPHOLOGY
and
LATENT LIVENESS
should remain decoupled.

But once decoupled, liveness needs its own learned control semantics:

MAINTENANCE:
retain only causally useful substrate.

REPAIR:
temporarily recruit useful substrate in response to injury.

CONTRACTION:
return toward economical maintenance after repair.

STAB-18-R1 tests the first component.
The historical LIFE4 recovery discontinuity indicates that the second component may remain absent.

PROVENANCE
evidence_class = CODE_BACKED_MECHANISTIC_AUDIT
canonical_scientific_execution = false
new_training_run = false
