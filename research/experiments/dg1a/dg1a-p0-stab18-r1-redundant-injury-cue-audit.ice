TITLE: DG-1A-P0-STAB-18-R1 — Redundant Injury-Cue Reliability Audit
DATE: 2026-09-18
STATUS: ANALYTIC / SYNTHETIC INFORMATION-RELIABILITY AUDIT — NOT A CANDIDATE RESULT
TRACK: DG-1A
PARENT: SPATIOTEMPORAL INJURY-GATE AUDIT

PURPOSE
Test whether the repair-associated increase in informational redundancy reported in recent GNCA work has a concrete reliability advantage for Yggdrasil's injury-state problem.

The prior wound-memory stress tests found:
- one raw analog cue can detect wounds;
- persistent structured noise can produce rare catastrophic false repair;
- spatial and temporal consensus help but do not solve highly persistent noise.

This audit asks:
If several local state channels carry overlapping injury evidence with partially independent noise, how much can false injury decisions fall at fixed true-injury sensitivity?

THIS RECORD DOES NOT
- alter or execute STAB-18-R1;
- measure Yggdrasil channel covariance;
- claim Yggdrasil already has redundant injury channels;
- select a number of repair channels;
- reserve hidden channels;
- treat raw channel correlation as equivalent to PID redundancy;
- preregister STAB-19.

CURRENT CAPACITY
Yggdrasil state width = 16.
Visible = 4 channels.
LIFE4 = channel 4.
Eleven additional hidden channels remain available for emergent state.

The current shared local update rule receives all channels through the same identity/Sobel perception and 128-unit local MLP.

LITERATURE CONTEXT
Structured Fluctuations and the Information Dynamics of Self-Maintenance in Growing Neural Cellular Automata (2026) reports:
- synergy-dominant resting computation;
- increased redundancy during recovery;
- spatially differentiated repair information flow;
- hidden fluctuations as functional parts of repair.

This audit tests one possible engineering reason such a regime shift could be useful:
redundant evidence can improve reliability if the signal is shared but noise is not perfectly shared.

IMPORTANT DEFINITION BOUNDARY
The analytic toy below uses several scalar observations of the same injury event.

That is an engineering redundancy model.
It is NOT the same mathematical object as partial-information-decomposition redundancy.

The connection to the published GNCA result is hypothesis-generating only.

GAUSSIAN SIGNAL-DETECTION TOY
Each cue observes:
NO INJURY:
X_i = noise_i

INJURY:
X_i = 2 + noise_i

Each cue individually therefore has standardized signal separation d' = 2.

Decision statistic:
arithmetic mean of K cues.

Decision threshold:
set separately for each K/correlation condition to retain exactly 90% true-injury detection in the Gaussian model.

Noise:
unit variance per cue;
equal pairwise correlation rho.

The analytic variance of the cue mean is:
Var(mean) = [1 + (K-1) rho] / K

Define diagnostic effective independent cue count:
N_eff = K / [1 + (K-1) rho]

This is a variance-equivalence diagnostic only.

FALSE-POSITIVE RATE AT FIXED 90% TRUE-POSITIVE RATE

rho = 0.00:
K=1:  23.624%
K=2:   6.095%
K=4:   0.328%
K=8:   0.000606%
K=12:  0.000000818%

rho = 0.25:
K=1:  23.624%
K=2:  10.597%
K=4:   4.074%
K=8:   1.660%
K=12:  1.083%

rho = 0.50:
K=1:  23.624%
K=2:  15.201%
K=4:  10.597%
K=8:   8.301%
K=12:  7.551%

rho = 0.75:
K=1:  23.624%
K=2:  19.585%
K=4:  17.432%
K=8:  16.325%
K=12: 15.952%

rho = 0.90:
K=1:  23.624%
K=2:  22.053%
K=4:  21.245%
K=8:  20.835%
K=12: 20.698%

rho = 0.99:
K=1:  23.624%
K=12: 23.341%

KEY RESULT
Redundant injury evidence is highly valuable only when its noise retains meaningful independence.

Twelve perfectly independent equal-quality cues reduce the false-alarm probability by many orders of magnitude at fixed 90% detection.

Twelve cues with rho=0.25 still reduce false alarms from 23.6% to about 1.08%.

But twelve cues with rho=0.90 behave like only:
N_eff approximately 1.10

and barely outperform one cue.

Therefore:
MORE CHANNELS IS NOT THE SAME AS MORE ROBUSTNESS.

The repair representation must avoid collapsing into near-identical noisy copies.

MODULAR-REDUNDANCY TOY
Recent GNCA work also reports hidden-channel modularization.

A second analytic diagnostic used 12 cues partitioned into:
3 modules of 4 cues each.

Within-module noise correlation:
0.8

Between-module correlation varied.

All cues still carry the same injury signal.

between-module rho | effective cue count | false alarm at 90% detection
0.00               | 3.53                | 0.665%
0.05               | 3.16                | 1.153%
0.10               | 2.86                | 1.791%
0.20               | 2.40                | 3.462%
0.40               | 1.82                | 7.850%

Interpretation:
strong redundancy inside modules can coexist with useful reliability if modules retain partially independent error modes.

This suggests a more nuanced repair architecture than "copy the same wound bit into many channels."

POTENTIAL ARCHITECTURAL READING
Maintenance and repair may favor different information organizations:

MAINTENANCE
- compact/synergistic state;
- efficient specialized latent computation;
- minimal unnecessary substrate.

REPAIR
- several partially independent local cues converge on the same injury state;
- increased redundancy raises robustness to channel-specific fluctuation or signal degradation;
- transient repair coordination can then recruit local support.

POST-REPAIR
- redundant repair evidence decays;
- state returns toward economical maintenance.

This is compatible with the published synergy-to-redundancy observation, but Yggdrasil has not measured such a regime shift.

RELATION TO PRIOR ROBUSTNESS NEGATIVE
The raw SupportMemory mechanism failed because one analog cue could occasionally wander into a false strong-injury state and then self-amplify.

This audit shows a principled alternative to simply increasing that cue's threshold:

require agreement among MULTIPLE PREDICTIVE ERRORS whose noise is not fully correlated.

A real lesion has a useful property:
center_lesion coherently removes all state channels in the damaged region.

Therefore local neighbors can, in principle, observe simultaneous violations in:
- LIFE4 support;
- visible state;
- latent cell-type/state channels;
- local dynamical expectations.

Ordinary fluctuations need not align across all of those representations.

That is the core multi-cue hypothesis.

CAUTION
A training objective that directly forces hidden channels to duplicate each other would be a poor interpretation of this result.

It could:
- destroy useful synergy;
- increase correlated noise;
- waste hidden capacity;
- recreate the rho -> 1 failure case.

The desired object is:
REDUNDANT INFORMATION ABOUT INJURY
with
DIVERSE ERROR MODES,
not redundant raw state values.

MEASUREMENT CONSEQUENCE
Before a future injury-state candidate is designed, real Yggdrasil trajectories should measure:

1. Per-channel / per-module injury discriminability.
2. Cross-channel noise covariance during undamaged persistence.
3. Cross-channel injury-response covariance immediately after lesion.
4. Effective dimensionality / participation ratio of hidden fluctuations.
5. Whether injury increases the number of channels carrying overlapping lesion information.
6. Whether candidate cue groups have partially independent maintenance noise.
7. Spatial range and temporal persistence of each cue/module.

These measurements can distinguish:
- useful redundant evidence;
from
- duplicated correlated noise.

FUTURE GATING IDEA — NOT A SCIENTIFIC GATE
A repair-state experiment should eventually prove BOTH:
- injury evidence becomes more mutually redundant / reliable after lesion;
- maintenance false-trigger rate remains bounded.

Do not add these to R1.

RELATION TO STAB-18-R1
R1 remains frozen and prior.

The causal-pruning experiment addresses maintenance substrate quality.

If R1 later establishes useful economical LIFE4 support but repair recruitment remains absent, the contingency sequence is now:

1. measure real latent maintenance/injury dynamics;
2. identify partially independent local injury cues;
3. test learned multi-cue predictive error;
4. only then test an excitable transient repair state.

This avoids jumping directly from a synthetic wound-memory success to an unsafe hard-coded repair signal.

CONCLUSION
The synthetic result gives a concrete reason why a repair state might become redundancy-enhanced:

redundancy can convert a noisy local injury decision into a reliable distributed decision,
BUT ONLY if the redundant evidence carries sufficiently independent noise.

This turns the 2026 synergy-to-redundancy observation into a testable Yggdrasil hypothesis rather than a metaphor.

PROVENANCE
evidence_class = ANALYTIC_REDUNDANT_CUE_RELIABILITY_AUDIT
canonical_scientific_execution = false
new_yggdrasil_training_run = false
signal_separation_dprime = 2
fixed_true_positive_rate = 0.90
