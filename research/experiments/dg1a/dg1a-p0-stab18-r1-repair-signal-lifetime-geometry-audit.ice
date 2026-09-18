TITLE: DG-1A-P0-STAB-18-R1 — Repair-Signal Lifetime Geometry Audit
DATE: 2026-09-18
STATUS: SYNTHETIC GEOMETRIC NEGATIVE — NO CANDIDATE SELECTED
TRACK: DG-1A
PARENT: WOUND-MEMORY / INJURY-STATE CONTINGENCY RESEARCH

PURPOSE
Test whether a transient local repair signal could be made safe merely by choosing a lifetime long enough to reach the deepest wound cell but short enough to expire before reaching the organism exterior.

THIS RECORD DOES NOT
- alter or execute STAB-18-R1;
- select a repair-signal lifetime;
- assume isotropic waves are the only possible repair mechanism;
- establish real trained-NCA propagation speed;
- authorize a decay parameter.

SYNTHETIC GEOMETRY
40x40 lattice.
Filled disk organisms spanning the frozen viable occupancy band:

radius | active cells
6      | 113
8      | 197
10     | 317
12     | 441
14     | 613
15     | 709
16     | 797

Centered lesion fractions tested:
0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50

Lesion geometry follows the current center-lesion bounding-box contract.

Distance metric:
8-neighbor / Moore graph distance through the original organism.

For each body/lesion pair:
D_wound =
maximum distance from the initial surviving wound boundary to any removed wound cell.

D_exterior =
minimum distance from the same initial wound boundary to any ordinary exterior-boundary cell.

A simple isotropic signal lifetime L can satisfy:
repair all wound cells before expiry
AND
never reach the exterior

only if:
D_wound <= L < D_exterior

Therefore a necessary geometric condition is:
D_exterior > D_wound.

CANONICAL 35% LESION RESULT
radius | active | removed | D_wound | D_exterior | safety margin D_exterior-D_wound
6      | 113    | 25      | 3       | 1          | -2
8      | 197    | 36      | 3       | 1          | -2
10     | 317    | 49      | 4       | 3          | -1
12     | 441    | 81      | 5       | 3          | -2
14     | 613    | 100     | 5       | 3          | -2
15     | 709    | 121     | 6       | 4          | -2
16     | 797    | 144     | 6       | 4          | -2

KEY NEGATIVE
For every tested viable body size under the canonical 35% centered lesion:
D_exterior <= D_wound.

Therefore ANY isotropic one-cell-per-step repair signal that lives long enough to reach the deepest missing wound cell can also reach the ordinary exterior boundary at least as early.

A fixed decay/lifetime cannot, by geometry alone, guarantee:
repair inward
without
outward growth.

WIDER LESION-FRACTION RESULT
A positive lifetime safety margin exists mainly for SMALL central lesions in sufficiently large bodies.

Examples:
radius 15 / 709 cells:
- 20% lesion: D_wound=3, D_exterior=6, margin +3
- 25% lesion: D_wound=4, D_exterior=5, margin +1
- 30% lesion: D_wound=5, D_exterior=5, margin 0
- 35% lesion: D_wound=6, D_exterior=4, margin -2
- 40% lesion: margin -3
- 45% lesion: margin -5
- 50% lesion: margin -7

radius 16 / 797 cells:
- 20%: margin +3
- 25%: +2
- 30%: 0
- 35%: -2
- 40%: -3
- 45%: -5
- 50%: -6

At the lower occupancy edge, even modest lesions can erase any safe lifetime window.

Thus the lack of a canonical lifetime window is not a one-body artifact.

MECHANISTIC CONSEQUENCE
A robust repair mechanism needs DIRECTIONAL or CONTEXTUAL recruitment, not merely:
- local trigger;
- isotropic propagation;
- finite TTL.

The signal must distinguish:
toward missing internal structure
from
toward ordinary external space.

Possible information sources, not selected mechanisms:
- local predictive-error gradient;
- cell-type / positional context encoded in hidden state;
- coherent multi-channel expectation violation;
- directional information flow learned from surviving neighbors;
- local attractor gradients.

This conclusion directly reinforces the preceding predictive-error research.

LITERATURE CONSISTENCY
Recent 2026 GNCA self-maintenance analysis reports spatially differentiated information flow during repair:
- corrective inward flow near the damage site;
- outward propagation of perturbation at greater distances.

That result is qualitatively consistent with the need for directional/context-sensitive dynamics rather than a uniform expanding repair wave.

It does not specify how Yggdrasil should implement that distinction.

RELATION TO BIOLOGICAL WOUND SIGNALS
Biological wound signals such as calcium waves can propagate beyond the wound edge, while downstream proliferation/migration remains spatially regulated.

This similarly suggests:
SIGNAL PROPAGATION
need not equal
CELL RECRUITMENT.

For Yggdrasil, a repair-state wave could communicate injury broadly while the actual LIFE4 recruitment decision remains locally conditional.

This is a stronger architecture than making every signal-bearing cell proliferative.

REVISED REPAIR DECOMPOSITION
1. INJURY DETECTION
local multi-cue predictive error.

2. INFORMATION PROPAGATION
transient repair-state communication may spread beyond the wound.

3. RECRUITMENT DECISION
new LIFE4 is licensed only where local context indicates missing internal support.

4. TERMINATION / CONTRACTION
repair state decays; maintenance economy resumes.

The geometry audit specifically rejects collapsing steps 2 and 3 into one isotropic growth front.

NO PARAMETER SWEEP CONSEQUENCE
Do not respond to the synthetic recurrent instability by tuning only:
- signal TTL;
- decay rate;
- wave radius;
- propagation speed.

Those parameters cannot remove the canonical geometric ambiguity.

The next high-value mechanism must add information, not just adjust duration.

RELATION TO STAB-18-R1
R1 remains frozen and prior.

If R1 later improves maintenance but leaves repair weak, the contingency mechanism should investigate directional/contextual predictive error rather than a simple temporary growth license.

PROVENANCE
evidence_class = SYNTHETIC_GEOMETRIC_NEGATIVE
canonical_scientific_execution = false
new_yggdrasil_training_run = false
distance_metric = Moore/8-neighbor graph distance
