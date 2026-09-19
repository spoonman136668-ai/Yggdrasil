TITLE: DG-1A-AR-H3 — Inherited Prior + Fast Local Utility Integration Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE INTEGRATION AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh2-spatial-niche-inheritance-audit.ice

PURPOSE
Integrate the slow inheritance lane with the fast utility-driven role lane.

Question:
Can inherited developmental bias behave as a useful prior
without becoming a command that blocks fast reassignment when local evidence changes?

This is the decisive integration test for:

SLOW HERITABLE PRIOR
+
FAST LOCAL ROLE ADAPTATION.

BOUNDARY
This is synthetic.

It does not:
- implement a real Yggdrasil micro-genome;
- update global shared network weights;
- allocate explicit role registers;
- alter or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TOY ORGANISM
Population:
512 local lineages.

Micro-genome:
4 bounded modulation dimensions.

Fast role state:
4 bounded functional-expression dimensions.

Environment:
one stable regime A,
then one abrupt switch to regime B.

A:
[0.8, 0.2, 0.2, 0.1]

B:
[0.2, 0.25, 0.8, 0.15]

Global prior:
mean(A,B).

Episodes:
500

Switch:
episode 250

Reproduction:
every 10 episodes.

Observation noise:
sigma = 0.18

Fast role update:
eta = 0.12

Micro-genome mutation:
sigma = 0.03

Micro-genome parent retention:
h = 0.95

Selection strength:
25.

FAST LOCAL UTILITY
Every episode the fast role state moves toward a noisy local observation of the current useful regime.

Conceptually:

r <- r + eta * (local_evidence - r)

This represents fast role plasticity.

The micro-genome is NOT allowed to replace this update.

CONTROL A — UTILITY ONLY
At every birth:
fast role state resets to the common prior.

Inherited micro-genome does not initialize the role.

CONTROL B — UNCONDITIONAL INHERITED BIRTH PRIOR
At every birth:
fast role state is initialized directly from inherited micro-genome.

This is the strongest simple inheritance bias.

CONTROL C — CONFIDENCE-GATED INHERITED PRIOR
Maintain a local exponential moving estimate of recent environmental/utility evidence.

At birth:
compare inherited micro-genome g
with recent evidence estimate m.

Discrepancy:

d =
RMS(g - m)

Inherited-bias weight:

w =
sigmoid(
    (threshold - d)
    /
    scale
)

Then:

role_birth =
global_prior
+
w * (g - global_prior)

Thus:
- if inherited state agrees with current local evidence,
  it strongly initializes the fast role;
- if inherited state conflicts with sustained local evidence,
  its influence is suppressed.

This is inheritance as prior,
not inheritance as command.

PRIMARY CONTROL RESULTS
12-16 fresh synthetic seeds depending on condition.

UTILITY ONLY

pre-switch steady loss:
0.01638

mean first 50 episodes after switch:
0.01619

late post-switch loss:
0.01619

Interpretation:
excellent reversibility,
weak stable specialization under repeated role-state reset/turnover.

UNCONDITIONAL FULL BIRTH PRIOR

pre-switch:
0.01238

first 50 after switch:
0.02386

late:
0.01226

Interpretation:
strong steady specialization,
large transient canalization cost.

This reproduces H2 in a turnover/fast-role setting.

SMOOTH CONFIDENCE GATE
Primary useful working point:

threshold:
0.20

scale:
0.02

RESULT

pre-switch steady loss:
0.01318

first 50 after switch:
0.01744

late post-switch loss:
0.01263

RELATIVE TO UTILITY ONLY

steady pre-switch improvement:
approximately 19.5%

late improvement:
approximately 22.0%

first-50 post-switch penalty:
approximately 7.7%.

RELATIVE TO UNCONDITIONAL INHERITANCE

steady-state cost is slightly higher,
but transition cost is reduced by approximately:

(0.02386 - 0.01744)
/ 0.02386
=
about 26.9%.

PRIMARY POSITIVE
A novelty/confidence gate preserves most of the long-run benefit of inheritance while substantially reducing the cost of obsolete inherited bias after an environmental switch.

This is the first synthetic result where:
- slow inherited memory;
- fast role plasticity;
- confidence/novelty

work together coherently.

GATE SWEEP
Representative sigmoid gates:

threshold 0.18
scale 0.02

pre:
0.01361

first 50:
0.01703

late:
0.01336

threshold 0.20
scale 0.02

pre:
0.01318

first 50:
0.01744

late:
0.01263

threshold 0.22
scale 0.02

pre:
0.01254

first 50:
0.01818

late:
0.01278

As expected:

higher tolerance for inherited mismatch
->
deeper inherited specialization
but
more transition drag.

Do not freeze these synthetic thresholds.

EXPONENTIAL GATE ABLATION
A smoother exponential confidence function was also tested.

It showed the same tradeoff:
more inheritance improves stable specialization
while increasing switch cost.

The exact nonlinear form is therefore less important than the principle:

INHERITED INFLUENCE SHOULD FALL
WHEN LOCAL EVIDENCE PERSISTENTLY CONTRADICTS IT.

WHY THIS MATTERS
H1 showed:
inheritance helps only when useful conditions persist.

H2 showed:
strong inheritance canalizes spatial niches.

U13 showed:
novelty/confidence can be shared as a magnitude while event identity remains typed.

H3 now connects these:

LOCAL NOVELTY
can control
HOW MUCH inherited prior to trust.

The semantic local utility still controls:
WHAT role to express.

PREFERRED TIMESCALE STACK

FAST:
role expression r

MEDIUM:
local utility/consequence estimate
+
novelty/confidence

SLOW:
heritable micro-genome g

Conceptual update:

FAST ROLE:
f(local state, local utility, inherited bias)

INHERITED BIAS WEIGHT:
decreases under sustained mismatch/novelty

MICRO-GENOME:
changes only through slow bounded inheritance/mutation.

IMPORTANT NEGATIVE
A continuously applied inherited pull was also tested.

It generally worsened fast adaptation because the stale micro-genome kept fighting current local utility.

Therefore do NOT implement:

every step:
role <- role + inherited_pull

as the default.

A better interpretation is:

inheritance initializes / biases developmental propensity

while current local evidence controls realized function.

This preserves reversibility.

ROLE-STATE MEMORY CONDITION
When fast role state itself persists perfectly through lineage replacement,
the added micro-genome provides little benefit in the toy.

Inheritance is most useful when:
- role state is partially reset by birth/turnover;
- local sensing is noisy;
- stable niche structure recurs;
- developmental bootstrapping matters.

This is scientifically important.

Do not add a slow genetic copy of information already durably represented in fast state.

MICRO-GENOME VALUE TEST
Before adding any real inherited parameter,
ask:

does this slow state retain useful information
that is NOT already available in:
- fast latent memory;
- current context;
- local utility?

If not:
inheritance is redundant state.

COMMON-MODE / LINEAGE CONNECTION
Confidence-gated inheritance also limits:
lineage-wide persistence of a wrong bias.

It does NOT create independence among descendants.

C4 provenance rules still apply.

NEXT
AR-H4 — MULTI-NICHE / TEMPORARY-INJURY PRIOR

Test the integrated mechanism under:
- several simultaneous local niches;
- lineage migration;
- temporary injury-created repair niche;
- niche disappearance;
- noisy/missing local utility.

Critical question:
can inherited prior speed repeated familiar specialization
without making temporary repair states heritable long after injury is gone?

This is especially important:
REPAIR SHOULD PROBABLY NOT BECOME A PERMANENT LINEAGE IDENTITY.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
population = 512
episodes = 500
switch_episode = 250
micro_genome_dimensions = 4
