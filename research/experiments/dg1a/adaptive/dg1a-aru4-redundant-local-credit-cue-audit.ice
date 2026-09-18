TITLE: DG-1A-AR-U4 — Redundant Local Credit-Cue Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX INFORMATION-RELIABILITY AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru3-local-utility-corruption-audit.ice

PURPOSE
Test whether redundant local consequence measurements can rescue role adaptation under noisy utility credit.

This directly asks whether the earlier Yggdrasil pattern:

useful redundancy requires partially independent error modes

also applies to local role-credit estimation.

BOUNDARY
This is synthetic.

It does not:
- prove Yggdrasil contains redundant utility cues;
- prescribe eight channels;
- alter or execute STAB-18-R1;
- establish partial-information-decomposition redundancy;
- turn a synthetic robustness result into a Yggdrasil scientific result.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TASK
Use the AR-U2 horizontal -> vertical moving-demand transition.

Fresh seeds:
50..55
n = 6

Noise is applied to ALL FOUR active role-utility channels:

relay
repair
inhibitor
growth

Noise standard deviation:
sigma = 0.25

For each true normalized utility q_i,
generate K noisy observations.

Equal pairwise Gaussian noise correlation:
rho

tested:
0.00
0.25
0.50
0.90

K tested:
1
2
4
8

and for rho=0.25:
12

RECOVERY CRITERION
Route cost returns to within 10% of the seed's pre-switch horizontal route cost for 10 consecutive steps.

Horizon:
180 steps

IMPORTANT AGGREGATION DISTINCTION
Two pipelines were tested.

PIPELINE A — CLIP EACH CUE FIRST
For each cue:

observed_k =
clip(q + noise_k, 0, 1)

Then:

q_est =
mean(observed_k)

PIPELINE B — AGGREGATE RAW EVIDENCE FIRST
First:

raw_mean =
mean(q + noise_k)

Then:

q_est =
clip(raw_mean, 0, 1)

This distinction matters because utility is bounded and many true inactive-role utilities are near zero.

PIPELINE A NEGATIVE — RECTIFICATION BIAS
With per-cue clipping,
increasing K did NOT restore clean role relocation.

Representative mean final route costs:

rho=0.00
K=1:
25.273

K=2:
25.315

K=4:
25.225

K=8:
25.226

Recovery:
0/6 for every listed condition.

The reason is diagnostic:

for true utility near zero,
zero-mean Gaussian noise becomes positively biased after each noisy sample is clipped at zero.

Averaging many already-rectified samples preserves that false positive role-credit bias.

Therefore:

MORE REDUNDANT CUES
CAN FAIL TO HELP
IF EACH CUE IS NONLINEARLY RECTIFIED BEFORE EVIDENCE IS COMBINED.

This is an important architecture-level negative.

PIPELINE B — AGGREGATE BEFORE CLIPPING

rho = 0.00

K=1:
final 25.186
recovery 0/6

K=2:
final 24.267
recovery 0/6

K=4:
final 23.374
recovery 0/6

K=8:
final 22.703
recovery 6/6
median latency 71 steps

Independent redundant observations become useful when their zero-mean evidence is combined before the bounding nonlinearity.

CORRELATED CUES
rho = 0.50

K=1:
25.295
0/6 recovery

K=2:
24.951
0/6

K=4:
24.706
0/6

K=8:
24.370
0/6

rho = 0.90

K=1:
25.218
0/6

K=2:
25.297
0/6

K=4:
25.196
0/6

K=8:
25.044
0/6

Moderately/highly correlated copies do not rescue the noisy credit problem.

rho = 0.25

K=2:
24.550
0/6

K=4:
24.080
0/6

K=8:
23.803
0/6

K=12:
23.697
0/6

Even 12 cues with this common-noise component did not cross the fixed recovery criterion.

PRIMARY FINDING
The same cross-domain rule now appears in THREE Yggdrasil research contexts:

1. INJURY CUES
partially independent error modes are required for useful redundant injury evidence.

2. SEASONAL SENSORS
independent sensing strongly reduces wrong-mode consensus error;
common-mode failure destroys most of the benefit.

3. LOCAL ROLE CREDIT
independent raw consequence cues can rescue noisy adaptation;
correlated copies cannot.

This convergence is stronger than any one synthetic result.

SECOND FINDING
The order of operations matters.

BAD:
cue
->
hard bound / rectification
->
average

BETTER:
several signed/raw local evidence terms
->
combine
->
bound the resulting estimate

when the cue model genuinely supports signed/zero-mean evidence.

This is not authorization to expose unbounded state in Yggdrasil.

It is a warning that:
early nonlinear compression can destroy the statistical benefit of redundancy.

DESIGN CONSEQUENCE
A future local credit mechanism should distinguish:

RAW EVIDENCE LAYER
several partially independent local consequence observations

from

DECISION / BOUNDED UTILITY LAYER
one bounded role-credit state used for adaptation.

Do not simply create many clipped copies of the same utility scalar.

CAUTION
Eight independent cues succeeding here does NOT mean Yggdrasil should reserve eight channels.

The useful quantity is:

effective independent evidence

not channel count.

The existing latent diagnostic should measure:
- covariance;
- effective dimensionality;
- cue diversity

before a real channel allocation is considered.

RELATION TO EXISTING R1 CONTINGENCY RESEARCH
This result strengthens the prior hypothesis that useful repair/role decisions may require:

multiple predictive errors
with
partially independent noise

rather than a single analog control scalar.

It does NOT modify R1.

NEXT RESEARCH
Two high-value continuations are now justified:

AR-U5 — CAUSAL LOCAL CREDIT
Replace hand-labelled role utility with:
did my recent local role change measurably improve a local consequence?

AR-C1 — REPEATED CONTEXT RELAY
Solve freshness ordering for multiple seasonal switches without global broadcast.

AR-U5 is the closer precursor to meta-rules.
AR-C1 is the closer precursor to fully decentralized seasonal control.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
fresh_seeds = 6
utility_noise_sigma = 0.25
