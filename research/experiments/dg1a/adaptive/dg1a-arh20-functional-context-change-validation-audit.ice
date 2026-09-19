TITLE: DG-1A-AR-H20 — Functionally Grounded Context-Change Validation Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE CAUSAL-CONTEXT VALIDATION + WEAK-EFFECT HOLD REGION
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh19-temporal-context-change-point-audit.ice

PURPOSE
H19 showed that source provenance plus temporal persistence can reject:
- family-local context corruption;
- brief globally coherent false-context bursts.

But a persistent false context is observationally indistinguishable from a genuine sustained context transition.

H20 adds the next identifiability source:

FUNCTIONAL CAUSAL VALIDATION OF THE CONTEXT CHANGE.

QUESTION
When context observations propose a persistent transition,
can a bounded randomized local challenge ask:

DID THE LOCAL CAUSAL ECONOMY ACTUALLY CHANGE?

BOUNDARY
This is synthetic.

It does not:
- prove real Yggdrasil has these exact challengeable local mechanisms;
- freeze a Bayesian threshold;
- freeze a challenge budget;
- authorize global semantic context labels;
- solve all causal confounding;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CONTEXT PROPOSAL
The observational context system uses the H19 hierarchy:

source-aware context evidence
+
temporal persistence.

A persistent proposed context switch reaches the functional validator only after the observational gate says:

NEW CONTEXT MAY BE REAL.

The validator does not receive:
A
or
B
as semantic labels.

It receives:

CURRENTLY TRUSTED LOCAL ADAPTIVE MECHANISM
vs
MECHANISM PREDICTED BY THE PROPOSED CONTEXT.

STRONG CAUSAL WORKING POINT
Old-context mechanism:
H0.

Proposed-context mechanism:
H1.

If the causal regime genuinely changes:

H0 success probability:
0.10

H1:
0.85.

If the context observation is a persistent global artifact
but the causal regime actually remains unchanged:

H0:
0.90

H1:
0.20.

The context observation is identical in both cases.

Only local functional consequence differs.

RANDOMIZED PAIRED CHALLENGE
One challenge pair samples:

one H0 outcome
and
one H1 outcome.

Order is randomized / paired conceptually so shared time drift can be controlled locally.

The controller maintains:

Beta(1,1)

success beliefs for each challenged mechanism.

After each pair,
estimate:

P(
  proposed_context_mechanism
  >
  current_context_mechanism
  |
  observed local outcomes
).

ACCEPT proposed context if:

posterior probability >= 0.95.

REJECT proposed context if:

posterior probability <= 0.05.

Otherwise:

continue challenging
up to:

12 pairs.

If still unresolved at the cap:

HOLD CONTEXT UNCERTAIN.

This is a synthetic discriminating policy.

Do not freeze:
0.95
or
12 pairs.

PRIMARY MONTE CARLO
50,000 fresh challenge episodes per condition.

STRONG GENUINE CAUSAL TRANSITION

H0 = 0.10
H1 = 0.85.

ACCEPT proposed context:
99.792%.

REJECT:
0.024%.

HOLD unresolved:
0.184%.

mean challenge pairs:
3.325.

median:
2.

STRONG PERSISTENT FALSE CONTEXT

true causal regime remains A.

H0 = 0.90
H1 = 0.20.

FALSE ACCEPT proposed context:
0.036%.

CORRECT REJECT:
99.434%.

HOLD:
0.530%.

mean pairs:
3.716.

median:
2.

PRIMARY POSITIVE
The persistent false context and genuine transition are deliberately identical under observational context evidence.

A small functional challenge separates them.

Thus:

CONTEXT PERSISTENCE
CAN PROPOSE A TRANSITION.

FUNCTIONAL CAUSAL CONSEQUENCE
CAN VALIDATE WHETHER THAT TRANSITION DESERVES CONTROL AUTHORITY.

This is stronger than additional smoothing.

FIXED-SAMPLE CONFIRMATION
Posterior threshold:
0.95.

Probability of accepting proposed context after exactly N paired challenges.

STRONG GENUINE

N = 2:
58.52%.

N = 4:
73.65%.

N = 6:
84.60%.

N = 8:
96.11%.

N = 12:
99.47%.

N = 16:
99.97%.

STRONG FALSE CONTEXT

false accept:

N = 2:
0.0400%.

N = 4:
0.000848%.

N = 6:
0.000120%.

N = 8:
0.0000168%.

N = 12:
approximately 0.0000004%.

Thus repeated causal evidence rapidly separates the strong cases.

WEAK-EFFECT STRESS
A context transition may be real
but functionally subtle.

Moderate genuine transition:

old mechanism:
0.40

proposed:
0.65.

Moderate false / reversed case:

old:
0.65

proposed:
0.40.

Same sequential challenge.
Maximum:
12 pairs.

50,000 episodes.

MODERATE GENUINE

ACCEPT:
50.12%.

REJECT:
2.98%.

HOLD:
46.90%.

mean pairs:
8.631.

median:
11.

MODERATE FALSE

FALSE ACCEPT:
3.03%.

REJECT:
49.77%.

HOLD:
47.20%.

mean pairs:
8.639.

median:
11.

PRIMARY WEAK-EFFECT RESULT
When the causal consequence difference is small,
the validator often refuses to make a confident context decision within the bounded evidence budget.

This is appropriate.

The mechanism does not force every persistent context proposal into:
TRUE
or
FALSE.

It can represent:

OBSERVATION SAYS CONTEXT CHANGED,
BUT FUNCTIONAL CAUSAL EVIDENCE IS NOT YET STRONG ENOUGH.

Thus:

UNCERTAINTY
IS A VALID STATE.

RESOURCE TRADEOFF
The strong cases often resolve after only:

2 to 4 paired trials.

The weak cases consume most of the allowed budget
and still frequently remain unresolved.

Therefore context validation itself is an adaptive evidence-allocation problem.

This connects H20 directly to:
S4-S9 value-of-information research.

A future controller should not challenge every ambiguous context indefinitely.

FUNCTIONAL VALIDATION AUTHORITY
H20 does NOT say:

functional microprobe result
=
semantic context identity.

It says:

A proposed context change should gain adaptive routing authority
only when the local mechanisms expected to differ under that context
actually show changed consequence.

The controller can remain context-agnostic.

RELATION TO H12
H12 established:

persistent candidate structure
must demonstrate functional causal value
before permanent structural growth.

H20 establishes the context analogue:

persistent candidate context
should demonstrate functional causal relevance
before receiving routing authority.

RELATION TO S7-S9
S7-S9 established that:
- functional outcome after an intervention can be confounded;
- valid causal control matters;
- control trust is reversible.

H20 therefore inherits those requirements.

The randomized paired challenge is intended to reduce common time drift,
but it is not a complete production causal-control solution.

A real implementation still needs:
- action identity;
- disturbance control;
- control trust;
- provenance.

CURRENT CONTEXT-AUTHORITY STACK
SOURCE / FAMILY PROVENANCE

+

INDEPENDENT SOURCE COUNT

+

INTER-SOURCE AGREEMENT

+

TEMPORAL CONTINUITY

+

CHANGE-POINT PERSISTENCE

->

CONTEXT CHANGE PROPOSAL

then

BOUNDED RANDOMIZED FUNCTIONAL CHALLENGE

+

LOCAL CONSEQUENCE

+

CAUSAL CONTROL

+

CHALLENGE CONFIDENCE

->

ACCEPT CONTEXT AUTHORITY
or
REJECT
or
HOLD UNCERTAIN.

GENERAL PRINCIPLE
Observational context should be allowed to:

NOMINATE

but not automatically:

AUTHORIZE.

This mirrors H14:

cheap weak structural evidence nominates candidates,
while expensive causal evidence authorizes permanent write.

The same weak-evidence / strong-evidence hierarchy now appears in context control.

DECISION
AR-H20 is POSITIVE WITH A WEAK-EFFECT HOLD REGION.

Supported synthetically:

- functional causal challenge can distinguish a genuine causal context transition from a persistent observational context artifact;
- strong genuine transitions can be accepted with very high reliability using a small bounded challenge;
- strong false contexts can be rejected with very low false-accept probability;
- weak causal differences often remain unresolved rather than being forced into a bad decision;
- context authority can be separated from context observation.

Not demonstrated:

- real Yggdrasil functional context challenge;
- safe challenge actions in mature high-value structures;
- optimal posterior model;
- optimal challenge budget;
- causal-control integrity under complex drift;
- multi-context / continuous-context transitions.

NEXT CLEAN QUESTION
AR-H21 — VALUE-OF-INFORMATION-GATED CONTEXT CHALLENGE

H20 can spend up to 12 paired functional challenges whenever a persistent context proposal appears.

That is still too expensive as a universal rule.

Question:

Can the organism decide whether context validation is worth probing at all?

Use:

observational context confidence
+
predicted policy divergence
+
functional stakes
+
challenge cost
+
deadline

to decide:

ACCEPT OBSERVATION,
HOLD,
or
SPEND CAUSAL CHALLENGE BUDGET.

Desired:

low-impact context ambiguity
->
do not spend many probes.

high-impact policy divergence
->
challenge aggressively.

strong existing causal evidence
->
stop early.

urgent context shift
->
act before maximal confidence.

This should reuse the S4-S9 local evidence economy
rather than create a separate central scheduler.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
strong_monte_carlo_episodes = 50000
weak_monte_carlo_episodes = 50000
max_challenge_pairs = 12
posterior_accept_threshold = 0.95
posterior_reject_threshold = 0.05
