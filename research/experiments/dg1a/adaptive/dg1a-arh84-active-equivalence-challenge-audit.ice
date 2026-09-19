TITLE: DG-1A-AR-H84 — Active Equivalence Challenge / Information-Gain Program Discrimination Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE ACTIVE-DISCRIMINATION RESULT + COST/POWER TRADEOFF
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh83-functional-equivalence-discovery-audit.ice

PURPOSE
H83 showed that:
repeated evidence from the same common functional regime
cannot detect:
context-limited false equivalence.

H84 asks:

CAN THE ORGANISM CHOOSE
A SMALL FUNCTIONAL CHALLENGE
THAT IS ESPECIALLY INFORMATIVE
ABOUT WHETHER TWO PROGRAMS ARE REALLY EQUIVALENT?

This is an equivalence-specific value-of-information problem.

BOUNDARY
This is synthetic.

It does not:
- freeze an active-learning algorithm;
- prove the local consequence predictor is available;
- freeze 12 contexts;
- freeze challenge costs;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CONTEXT SET
12 synthetic functional contexts.

COMMON CONTEXTS
0..7.

DISCRIMINATING CONTEXTS
8..11.

The false-equivalent program matches the reference program in:
contexts 0..7.

It diverges:
moderately
in contexts 8..9

and:
strongly
in contexts 10..11.

REFERENCE PROGRAM A
Success probabilities remain:
approximately 0.84..0.92
across contexts.

TRUE PRACTICAL EQUIVALENT B
Differs from A only:
slightly,
approximately 0.01
per context.

FALSE-EQUIVALENT C
Matches A in:
the first eight contexts.

Then falls to approximately:

0.64
0.62
0.34
0.30

while A remains:
approximately 0.84..0.88.

BASELINE EVIDENCE
Before H84 begins,
program pairs are tested in:

four ordinary contexts:
0..3.

30 trials / program / context.

Only pairs that:
PASS
this baseline equivalence screen
enter the active challenge experiment.

Thus:
H84 measures:
how much new information the challenge adds.

EQUIVALENCE DECISION
Diagnostic threshold:

maximum observed context-wise difference
>
0.22

means:
reject equivalence.

The exact threshold is synthetic.

CHALLENGE BUDGET
At most:
3 additional context challenges.

Each challenge collects:
30 trials
for each program
in the selected context.

CONTEXT COSTS
Ordinary contexts:
0.5 synthetic challenge units.

Moderately discriminating contexts:
1.0.

Strong rare contexts:
2.0.

POLICIES

REPEAT ORDINARY CONTEXT
Keep testing:
context 0.

RANDOM CONTEXT
Choose randomly among:
all 12.

COVERAGE / UNCERTAINTY
Prefer:
least-tested contexts.

No prediction of functional difference.

PREDICTED DISAGREEMENT
Each program has an imperfect local consequence predictor.

Predicted pair difference:

true latent difference
+
Gaussian prediction noise
SD:
0.10.

Choose the context with:
highest predicted disagreement
discounted mildly by:
existing sample support.

This is a synthetic stand-in for:
learned local forward consequence models.

VALUE / COST CHALLENGE
Choose using:

predicted disagreement
/
challenge cost

with the same support correction.

PRIMARY MONTE CARLO
10,000 baseline-passed episodes
per:
program pair
and
policy.

FALSE-EQUIVALENT A/C

REPEAT ORDINARY

challenge rejection rate:
0%.

mean challenges used:
3.0.

mean cost:
1.50.

PRIMARY REDUNDANT-EVIDENCE NEGATIVE
Once the pair has passed:
ordinary context evidence,

more of:
the same evidence

adds:
no discrimination.

The full challenge budget is wasted.

RANDOM CONTEXT

false-equivalence rejection:
57.02%.

mean challenges:
2.31.

mean cost:
1.923.

median challenges when rejected:
2.

COVERAGE

rejection:
81.11%.

mean challenges:
1.98.

mean cost:
2.074.

median rejection:
2 challenges.

PRIMARY COVERAGE POSITIVE
Simply seeking:
functional-domain coverage

is much better than:
repeating ordinary evidence.

But:
coverage does not know:
which untested context is actually discriminating.

PREDICTED DISAGREEMENT

rejection:
100%.

mean challenges:
1.002.

mean cost:
2.003.

median:
1.

PRIMARY INFORMATION-GAIN POSITIVE
An imperfect consequence predictor can direct:
the challenge budget

toward:
where the two programs should behave differently.

The hidden false equivalence is detected:
essentially immediately
in the tested model.

VALUE / COST

rejection:
93.84%.

mean challenges:
1.527.

mean cost:
2.077.

median rejected:
1.

This cost heuristic sometimes prefers:
cheaper moderately discriminating contexts

and therefore:
needs more challenge rounds.

It gives up:
some detection power

for:
a more conservative discrimination policy.

TRUE-EQUIVALENT A/B CONTROL
All rates below are:
false equivalence rejection
after:
the baseline has already accepted A/B.

REPEAT ORDINARY:
0%.

RANDOM:
2.19%.

COVERAGE:
4.01%.

PREDICTED DISAGREEMENT:
1.98%.

VALUE / COST:
1.02%.

PRIMARY TRUE-EQUIVALENCE RESULT
Active challenge does not need to:
destroy
the useful equivalence class.

The best discriminating policy in the false-pair test:

predicted disagreement

still falsely splits:
only approximately 2%
of baseline-passed true-equivalent episodes.

The cost-aware policy lowers that to:
approximately 1%.

INFORMATION-GAIN PRINCIPLE
The organism should not ask:

HOW MUCH MORE DATA CAN I COLLECT?

It should ask:

WHICH LOCAL CONDITION
WOULD MAKE THESE TWO HYPOTHESES
DISAGREE MOST?

This is:
active causal discrimination.

PREDICTOR LIMIT
H84 gives the predicted-disagreement policy:
an imperfect consequence model
for all candidate contexts.

That is still privileged.

Real Yggdrasil must:
learn
or
construct

those counterfactual consequence predictions.

Thus:
H84 validates:
the challenge-selection principle

not:
its final implementation.

SAFETY / COST
The strongest discriminating context can also:
be more expensive.

The value/cost policy shows:
challenge selection should consider:

INFORMATION GAIN

and

FUNCTIONAL / RESOURCE COST.

A dangerous perturbation should not be selected merely because:
it is maximally informative.

RELATION TO H21 / H52
H21:
context challenge should be value-gated.

H52:
scarcity challenge should be value-gated.

H84:
equivalence challenge should also be:
information-value-gated.

Again:
one generic evidence economy
can allocate:
diagnostic experiments.

RELATION TO H83
H83:
equivalence must remain:
context-bounded.

H84:
the context boundary can be:
actively expanded

by choosing:
maximally discriminating tests.

Thus:
equivalence confidence can mature
through:
targeted challenge.

GENERAL PRINCIPLE
WHEN TWO INTERNAL MODELS LOOK THE SAME:

DO NOT ONLY
OBSERVE THEM LONGER.

PERTURB THE SYSTEM
WHERE THEY PREDICT
DIFFERENT CONSEQUENCES.

This is a stronger route toward:
autonomous internal science.

OUTSIDE-STATUS-QUO IMPLICATION
A developmental intelligence may not merely:
learn from experience.

It may perform:
small internal experiments

to identify:
which of its own programs,
models,
or causal hypotheses

are genuinely interchangeable.

That moves Yggdrasil toward:
self-experimenting developmental cognition.

DECISION
AR-H84 is POSITIVE WITH A COST/POWER TRADEOFF.

Supported synthetically:

- repeated ordinary evidence cannot resolve context-limited equivalence;
- random context challenge provides partial discrimination;
- systematic coverage is substantially better;
- predicted-disagreement challenge can identify the hidden difference with very few tests;
- true-equivalent programs are mostly retained;
- cost-aware challenge reduces false splitting but can sacrifice discrimination power;
- equivalence testing is naturally an active value-of-information problem.

Not demonstrated:

- learned counterfactual consequence prediction;
- safe real perturbation design;
- continuous context optimization;
- multi-program equivalence classes;
- delayed / long-horizon functional differences;
- challenge sharing across cells.

NEXT HIGH-VALUE MOVE
AR-H85 — NEUTRAL FUNCTIONAL DRIFT / CRYPTIC IMPLEMENTATION DIVERSITY

H82-H84 make it possible to maintain:
a confidence-bounded functional equivalence class.

A more radical question:

SHOULD YGGDRASIL ALLOW
FUNCTION-PRESERVING IMPLEMENTATIONS
TO DRIFT
EVEN WHEN THE CURRENT BEST PROGRAM ALREADY WORKS?

Candidate idea:

small program variations
that remain within:
the current functional equivalence envelope

can persist:
dormant or low-authority.

They may explore:
different resource metabolism
or
failure modes.

Later:
a resource shock
or
structural failure

may make one cryptic variant:
valuable.

Compare:

A.
always keep only current best;

B.
identical redundant copies;

C.
bounded neutral drift inside functional canary constraints;

D.
resource shock;

E.
implementation-family failure;

F.
memory price limiting cryptic diversity.

Desired:

CURRENT FUNCTION
stays stable

while

IMPLEMENTATION DIVERSITY
quietly explores:
future options.

This is inspired by biological ideas around:
neutral networks,
degeneracy,
robustness,
and
evolvability.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
candidate_contexts = 12
challenge_budget = 3
trials_per_challenge = 30
predicted_disagreement_false_pair_detection = 1.0
predicted_disagreement_true_pair_false_split = 0.0198
