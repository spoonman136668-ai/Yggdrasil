TITLE: DG-1A-AR-U14 — Value-of-Information / Urgency Coupling Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE RESOURCE-ALLOCATION AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru13-budgeted-active-evidence-audit.ice

PURPOSE
AR-U13 established that causal evidence behaves like a finite local adaptive resource.

This audit asks:

When several local functions compete for the same sensing/probing budget,
should evidence be allocated by:
- uncertainty alone;
- functional stakes alone;
- expected value of additional information?

BOUNDARY
This is a synthetic allocation benchmark.

It does not:
- define real Yggdrasil utility units;
- freeze repair/maintenance weights;
- prove the organism can estimate value of information;
- authorize global budgeting;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

EVENT CLASSES
20,000 local decision events per primary run.

Class distribution:

MAINTENANCE
60%

REPAIR
30%

URGENT REPAIR
10%

FUNCTIONAL STAKES
Synthetic wrong-decision cost weights:

maintenance:
1

repair:
4

urgent repair:
8

These values are experimental contrast weights only.

They are NOT proposed biological constants.

CONSEQUENCE SIGNAL QUALITY
Each event has binary beneficial/harmful local action sign.

True signal magnitude:
0.08

Observation-noise SD:

maintenance:
0.12

repair:
0.14

urgent:
0.18

Thus urgent events are both:
more valuable
and
harder to resolve.

EVIDENCE LIMIT
Every event begins with:
1 probe pair.

Maximum total probe pairs:

maintenance:
8

repair:
8

urgent:
4

The urgent cap represents a deadline:
time-critical repair cannot wait indefinitely for evidence.

CORRECT-SIGN PROBABILITY
For k independent probe pairs:

P(correct)
=
Phi(
    signal * sqrt(k)
    /
    noise
)

This analytic Gaussian relation is used only inside this synthetic allocation benchmark.

POLICIES

EQUAL / UNIFORM
Allocate evidence evenly across events.

UNCERTAINTY-ONLY
Allocate each next probe to the event with largest expected reduction in sign uncertainty,
ignoring functional stake.

STAKE-ONLY
Allocate probes to highest-stake events first,
ignoring diminishing information returns.

VALUE-OF-INFORMATION
For each possible next probe:

marginal score
=
functional stake
*
(
P_correct(k+1)
-
P_correct(k)
)

Allocate the next available probe to the event with highest marginal score.

This is a batch allocation upper-bound.

It does not prove a purely local organism can implement the exact greedy scheduler.

PRIMARY BUDGET
Extra probe budget:
2 per event on average.

Total mean probes per event:
3.

RESULTS

EQUAL
mean probes:
3.0

weighted expected wrong-decision cost:
0.44386

overall unweighted correct-sign probability:
85.52%

allocation:
maintenance 3.0
repair 3.0
urgent 3.0

UNCERTAINTY-ONLY
In the primary parameterization,
the marginal uncertainty curves are sufficiently similar that uncertainty-only allocation collapses to essentially the same 3/3/3 solution.

weighted expected error:
approximately 0.44386

PRIMARY NEGATIVE
UNCERTAINTY ALONE DOES NOT ENCODE FUNCTIONAL VALUE.

Two equally uncertain decisions can have very different biological consequences.

STAKE-ONLY
mean probes:
3.0

weighted expected error:
0.41473

overall unweighted accuracy:
80.08%

allocation:
maintenance 1.0
repair ~6.77
urgent 4.0

Stakes-only improves weighted error,
but substantially sacrifices maintenance accuracy.

VALUE-OF-INFORMATION
mean probes:
3.0

weighted expected error:
0.38164

overall unweighted accuracy:
84.01%

allocation:
maintenance ~1.86
repair 5.0
urgent 4.0

PRIMARY POSITIVE
VoI allocation reduces weighted wrong-decision cost by approximately:

14.0%
relative to equal allocation

and

8.0%
relative to stakes-only

at the same total evidence budget.

It does so by considering BOTH:
- functional value;
- diminishing return of more evidence.

REALIZED MONTE CARLO CHECK
Primary fresh realization:

equal weighted realized error:
0.4523

stakes-only:
0.4151

VoI:
0.3814

The realized ordering matches the expected ordering.

BUDGET SWEEP

EXTRA = 1
mean total probes = 2

EQUAL
weighted expected error:
0.57111

STAKE
0.55331

VoI
0.48430

VoI allocation:
maintenance 1.0
repair ~3.31
urgent 4.0

Scarce-budget improvement versus equal:
~15.2%.

EXTRA = 2
total = 3

EQUAL:
0.44524

STAKE:
0.41891

VoI:
0.38287

EXTRA = 3
total = 4

EQUAL:
0.35553

STAKE:
0.34470

VoI:
0.31617

EXTRA = 4
total = 5

EQUAL:
0.30935

STAKE:
0.31610

VoI:
0.27674

IMPORTANT STAKES-ONLY NEGATIVE
At the larger budget,
stakes-only becomes WORSE than equal allocation.

Reason:
it keeps assigning probes to high-stake classes after their marginal information value has diminished,
while lower-stake unresolved events remain under-sampled.

Therefore:

HIGH STAKE
!=
INFINITE EVIDENCE PRIORITY.

VALUE OF INFORMATION must include:
DIMINISHING RETURNS.

URGENCY
Urgent repair events are capped at:
4 probe pairs.

VoI saturates that cap early when evidence is scarce.

This reflects the tension:

high stake
pushes toward more evidence

but

deadline
limits how long evidence can be collected.

A real organism therefore needs both:

VALUE
and
TIME-TO-ACT.

ARCHITECTURAL CONSEQUENCE
The AR-U13 token budget can be extended conceptually to:

available evidence tokens

+
uncertainty

+
functional stake

+
expected information gain

+
deadline / urgency

->
how much evidence to collect now.

This is a primitive LOCAL VALUE-OF-INFORMATION controller.

It need not be a central scheduler.

Each cell or local module can estimate whether:
one more perturbation/observation
is worth its local cost.

IMPORTANT DISTINCTION
A cell should not maximize:
confidence.

It should maximize something closer to:

EXPECTED FUNCTIONAL IMPROVEMENT
PER
ADAPTIVE RESOURCE SPENT.

A low-value uncertainty may be left unresolved.

A high-value uncertainty may justify extra sensing.

A very urgent decision may require acting before confidence is maximal.

RELATION TO END GOAL
This is directly relevant to Yggdrasil's resource-constrained developmental thesis.

The desired organism should not keep:
every cell
maximally sensing
maximally updating
maximally plastic
at all times.

Instead:
adaptive resources should move toward the places where they are currently most valuable.

This offers a route toward:

active repair
+
quiet maintenance
+
localized high-effort reasoning
+
dormant low-cost tissue

under one resource economy.

LIMITATIONS
The benchmark assumes:
- functional stake is already known;
- noise level is known;
- information gains are analytically estimable;
- decisions are independent.

Real Yggdrasil violates all four assumptions.

Therefore:
this is a VALUE PRINCIPLE,
not an implementation.

NEXT
AR-U15 — LEARNED LOCAL VALUE-OF-INFORMATION

Remove known:
stake
and
noise.

Question:
Can a cell estimate whether additional evidence was worth its cost from recent local outcomes?

Compare:
- fixed evidence budget;
- hand-calculated VoI upper bound;
- bounded learned probe policy using only local history;
- failure under nonstationary stakes/noise.

PARALLEL
AR-C5 — online sensor-diversity adaptation.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_events = 20000
