TITLE: DG-1A-AR-01 — Redundant Seasonal Sensor Consensus Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX SENSOR-RELIABILITY AUDIT — NOT A YGGDRASIL SCIENTIFIC RESULT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-ar01-local-context-propagation-audit.ice

PURPOSE
The context-corruption audit found that confident wrong-mode context is substantially more dangerous than modest analog noise.

This audit asks:
Can multiple local environmental sensors reduce semantically wrong seasonal mode decisions, and how much does correlated sensor error limit that benefit?

BOUNDARY
This is a Monte Carlo reliability toy.
It does not:
- add Yggdrasil sensors;
- reserve channels;
- alter AR-01;
- execute STAB-18-R1;
- establish biological sensor independence.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TRUE MODES
Six equally likely discrete seasonal modes.

Each sensor reports one of the six modes.

MARGINAL SENSOR ERROR
Each sensor is wrong with probability p.

When wrong:
it reports one of the other five modes uniformly.

SENSORS TESTED
K:
1
3
5
9

ERROR CORRELATION MIXTURE
q = common-mode fraction.

For each trial:

with probability q:
all K sensors share one common report event:
- correct with probability 1-p;
- all wrong together with probability p;
- if wrong, all report the same randomly selected wrong mode.

with probability 1-q:
the K sensors fail independently at marginal probability p.

This preserves each sensor's marginal error rate p while varying the amount of common-mode failure.

CONSENSUS
Each reported mode is converted to the frozen CIRCLE-2 unit vector.

The K vectors are summed.

The consensus mode is the nearest of the six discrete seasonal phase points to the resultant vector.

TRIALS
100,000 Monte Carlo trials per condition.

RESULTS

MARGINAL SENSOR ERROR p = 0.10

common-mode q | K=1    | K=3    | K=5    | K=9
0.00          | 10.03% | 6.08%  | 2.44%  | 0.20%
0.25          | 10.02% | 7.02%  | 4.09%  | 2.60%
0.75          | 9.93%  | 9.07%  | 8.03%  | 7.53%
1.00          | 10.06% | 10.18% | 10.06% | 10.12%

MARGINAL SENSOR ERROR p = 0.25

common-mode q | K=1    | K=3    | K=5    | K=9
0.00          | 24.96% | 18.91% | 13.04% | 4.23%
0.25          | 25.15% | 20.58% | 15.96% | 9.51%
0.75          | 25.18% | 23.43% | 22.01% | 19.84%
1.00          | 25.08% | 24.89% | 25.24% | 25.34%

MARGINAL SENSOR ERROR p = 0.40

common-mode q | K=1    | K=3    | K=5    | K=9
0.00          | 40.02% | 35.13% | 29.32% | 17.09%
0.25          | 40.11% | 36.13% | 32.06% | 22.93%
0.75          | 39.82% | 38.70% | 37.47% | 34.27%
1.00          | 39.88% | 40.24% | 39.92% | 40.15%

KEY RESULT
Redundant seasonal sensing can strongly suppress wrong-mode errors only when sensor errors retain meaningful independence.

Example:
at 10% marginal per-sensor error:

one sensor:
about 10.0% wrong mode

nine independent sensors:
about 0.20% wrong mode

nine sensors with q=0.75 common-mode mixture:
about 7.53% wrong mode

nine fully common-mode sensors:
about 10.1% wrong mode

Therefore:
MORE SENSORS != MORE RELIABLE CONTEXT
unless their failure modes differ.

RELATION TO PRIOR INJURY-CUE AUDIT
This independently reproduces the same architectural principle found in:
dg1a-p0-stab18-r1-redundant-injury-cue-audit.ice

For both:
- injury sensing;
- environmental mode sensing;

useful redundancy requires partially independent errors.

This is now a cross-domain pattern in the Yggdrasil research program.

SENSOR-LOSS ANALYTIC NOTE
If each of K independent sensor cells is destroyed with probability d,
the probability all K are destroyed is:

P(all lost) = d^K

Example:
d = 0.25

K=1:
25%

K=4:
0.390625%

K=8:
0.0015259%

This only addresses independent physical loss.
A spatial lesion can correlate sensor loss, and a disconnected component can still become sensorless.

DESIGN CONSEQUENCE
A future decentralized context system should prefer:
- multiple spatially separated sensor cells;
- partially independent environmental transduction paths;
- local consensus;
- confidence or disagreement state;
- temporal consistency.

It should not simply clone one sensor signal into many identical channels.

WRONG-MODE SAFETY
Because confident wrong-mode signals are more dangerous than modest analog noise, a future organism should be permitted to detect context disagreement and delay a global regime switch rather than immediately amplifying inconsistent reports.

This suggests:
sensor observations
->
local consensus / confidence
->
freshness relay
->
seasonal rule modulation

rather than:
single sensor
->
unconditional organism-wide relay.

DECISION
Preserve redundant, spatially distributed sensing as a future decentralized-context hypothesis.

Do not add it to first AR-01 execution.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
monte_carlo_trials_per_condition = 100000
