TITLE: DG-1A-AR-U11 — Action-Leakage Freshness / Online Recalibration Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE FRESHNESS AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru10-action-leakage-correction-poc.ice

PURPOSE
AR-U10 showed that subtracting estimated action leakage from local disturbance references improves causal credit,
but a stale leakage estimate can become harmful when local coupling changes.

AR-U11 asks:

Can sparse local re-probing detect and recalibrate changed action-to-neighborhood coupling without global supervision?

BOUNDARY
Synthetic only.

This does not:
- prove real Yggdrasil can estimate action leakage;
- authorize permanent probing;
- alter or execute STAB-18-R1;
- define the final meta-rule.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SYNTHETIC LOCAL CREDIT SETUP

Parallel local learners:
12,000

reference signals:
8

no-action history:
48 observations

common environment SD:
0.15

reference noise SD:
0.03

target noise SD:
0.03

causal target effect:
+/-0.04

Initial action-leakage estimate:
8 signed microprobes

microprobe observation noise:
0.02

The first 50 adaptation episodes use the calibrated coupling:

factor = 1.

At episode 50,
ALL action-to-reference leakage strengths change abruptly.

Test factors:

0
0.5
2
3

The environment/reference disturbance relationship remains otherwise unchanged.

METHODS

NO CORRECTION
Use local neighborhood disturbance estimate without action-leakage subtraction.

STALE CORRECTION
Continue subtracting the original pre-change leakage estimate forever.

PERIODIC RECALIBRATION
Every 8 episodes after the change:
- run two local signed microprobes;
- estimate current action leakage;
- update stored leakage estimate with:
  50% old
  50% new estimate.

CONTINUOUS RECALIBRATION
Use one signed microprobe each episode.

Leakage estimate EWMA:
15% new observation.

No global score is supplied.

PRE-CHANGE BASELINE

no correction:
approximately 84.6..84.8% causal-sign accuracy

leakage-corrected methods:
approximately 88.8..88.9%

This reproduces AR-U10.

COUPLING DISAPPEARS
factor:
0

First 8 post-change episodes:

no correction:
88.88%

stale correction:
84.53%

periodic recalibration:
87.30%

continuous:
87.00%

Late / final:

no correction:
89.0%

stale:
84.6%

periodic:
88.8%

continuous:
88.9%

Stable 5-episode >=88% recovery latency after change:

periodic:
10 episodes

continuous:
7 episodes

INTERPRETATION
When leakage disappears,
the best correction is eventually:
no subtraction.

The stale correction invents false opposite action leakage.

Sparse re-probing learns to stop subtracting it.

COUPLING HALVES
factor:
0.5

Late:

no correction:
approximately 87.9%

stale:
87.8%

periodic:
88.9%

continuous:
88.95%

>=88% stable recovery:

periodic:
3 episodes

continuous:
4 episodes

COUPLING DOUBLES
factor:
2

First 8 post-change:

no correction:
74.30%

stale:
84.59%

periodic:
87.30%

continuous:
87.10%

Final:

no correction:
74.29%

stale:
84.59%

periodic:
88.81%

continuous:
88.85%

stable >=88% recovery:

periodic:
10 episodes

continuous:
6 episodes

COUPLING TRIPLES
factor:
3

First 8 post-change:

no correction:
63.50%

stale:
74.33%

periodic:
83.35%

continuous:
82.32%

Final:

no correction:
63.48%

stale:
74.40%

periodic:
88.84%

continuous:
88.86%

stable >=88% recovery:

periodic:
18 episodes

continuous:
10 episodes

PRIMARY POSITIVE
A leakage estimate does not need to be permanently correct.

Sparse action-tagged recalibration can restore a useful causal baseline after substantial structural coupling changes.

This is important because a developmental organism will naturally change:

- neighbors;
- roles;
- morphology;
- communication routes;
- damage state.

Any causal-control calibration tied to those structures must therefore be treated as temporary knowledge.

PRIMARY DESIGN RULE

CAUSAL CALIBRATION
must carry:

VALUE

+
FRESHNESS / CONFIDENCE

+
RECALIBRATION PATH.

A scalar estimate with no age/confidence is unsafe.

PERIODIC VS CONTINUOUS TRADEOFF

CONTINUOUS
advantages:
- faster recovery after large coupling changes.

cost:
- constant exploratory perturbation / measurement overhead.

PERIODIC
advantages:
- lower probe burden;
- eventually restores approximately the same asymptotic accuracy in this toy.

cost:
- slower recovery under very large changes.

For factor 3:
periodic 8-episode probing:
18-episode stable recovery.

continuous:
10.

Do NOT freeze the interval from this synthetic experiment.

EVENT-TRIGGERED IMPLICATION
The better future architecture may be neither fixed-period nor continuous probing.

A cell could increase recalibration when:
- prediction residual suddenly increases;
- neighborhood membership changes;
- damage is detected;
- role state changes strongly;
- reference confidence falls.

Then reduce probing in stable maintenance.

This would connect:
INJURY / NOVELTY DETECTION

to

CAUSAL-CREDIT RECALIBRATION.

CAUTION
A prediction residual cannot by itself prove which calibration changed.

It can only justify:
confidence reduction / renewed probing.

Do not update the leakage estimate from unexplained residual alone.

META-RULE CONSEQUENCE
The emerging local meta-rule now requires TWO timescales:

FAST:
role perturbation / functional adaptation.

SLOWER:
calibration of how the cell's actions influence local reference signals.

This is still below the proposed heritable micro-genome timescale.

CURRENT TIMESCALE STACK

FASTEST:
ordinary NCA activation/state.

FAST:
functional role expression.

MEDIUM:
eligibility / consequence memory.

MEDIUM-SLOW:
action-leakage / disturbance-model calibration.

SLOW:
future heritable micro-genome adaptation.

This hierarchy was not assumed at the beginning of AR research;
it is emerging from causal-identifiability constraints.

NEXT
AR-U12 — EVENT-TRIGGERED RECALIBRATION

Compare:
- periodic probes;
- continuous probes;
- residual-triggered confidence drop + temporary probe burst.

Measure:
- causal accuracy;
- probe budget;
- recovery latency;
- false recalibration during ordinary noise.

PARALLEL
AR-C2:
multi-sensor distributed context consensus with serial ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
parallel_learners = 12000
coupling_change_episode = 50
