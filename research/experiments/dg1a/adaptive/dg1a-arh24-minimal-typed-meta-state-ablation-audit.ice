TITLE: DG-1A-AR-H24 — Minimal Typed Meta-State Ablation Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX IDENTIFIABILITY ABLATION / POSITIVE COMPRESSION WITH NON-COLLAPSIBLE STATE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh23-shared-meta-rule-trust-state-audit.ice

PURPOSE
H23 showed that Yggdrasil can plausibly reuse one generic trust-update motif across several adaptive domains,
provided each domain retains distinct local trust state.

H24 asks the compression question:

WHAT IS THE SMALLEST GENERIC PER-TRUST-INSTANCE STATE THAT STILL PRESERVES THE DISTINCT DECISIONS REQUIRED BY H5-H23?

This is an identifiability / ablation audit.

It is not a claim that the final implementation should use logistic regression or these exact fields.

BOUNDARY
This is synthetic.

It does not:
- freeze a production state vector;
- freeze a classifier;
- prove these variables are sufficient for real Yggdrasil;
- authorize one global scalar;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CANDIDATE GENERIC META-STATE
Six candidate scalar fields:

1.
TRUST MAGNITUDE

2.
AGE / RECENCY

3.
EFFECTIVE EVIDENCE COUNT

4.
CAUSAL-CONTROL CONFIDENCE

5.
MODEL / CONTEXT FIT CONFIDENCE

6.
RESOURCE COST / AUTHORITY PRICE

Five trust types are represented:

inherited-prior expression;

causal-control validity;

structural nomination/search trust;

context-routing authority;

context-challenge value.

Each type uses the same field vocabulary
but assigns different importance to those fields.

SYNTHETIC DECISION POPULATION
300,000 local trust decisions.

Continuous fields are independently varied over broad ranges.

Each trust type has a hidden additive authorization rule using the six fields with different weights.

Small unmodeled stochastic variation is added.

The resulting authorize / do-not-authorize population is approximately balanced:

positive authorization:
49.7%.

This construction is intentional.

The audit asks:
how much decision information is lost when a candidate field is removed or collapsed?

TRAIN / TEST
180,000 synthetic decisions used for fitting.

120,000 held-out decisions used for evaluation.

The evaluator is a type-conditioned linear decision rule.

This matches the synthetic generative form,
so differences between schemas primarily reflect missing state information
rather than model-capacity failure.

PRIMARY SCHEMAS

FULL TYPED STATE

trust
+
age
+
evidence count
+
causal confidence
+
fit confidence
+
cost.

TRUST ONLY

trust magnitude
+
trust type.

LEAVE-ONE-FIELD-OUT

remove each candidate field from the full schema.

COMPRESSED EVIDENCE

replace:

age
+
evidence count

with:

effective_evidence_mass
=
normalized_count
*
exp(-2 * age).

COMPRESSED APPLICABILITY

replace:

causal confidence
+
fit confidence

with:

causal_confidence
*
fit_confidence.

BOTH COMPRESSIONS

use:
trust
+
effective evidence mass
+
applicability
+
cost.

PRIMARY HELD-OUT RESULTS
Accuracy.

FULL TYPED STATE

0.86333.

TRUST ONLY

0.68935.

PRIMARY TRUST-ONLY NEGATIVE
Trust magnitude by itself loses approximately:

17.4 percentage points

of decision accuracy.

Therefore:

ONE TRUST NUMBER
DOES NOT CONTAIN
ENOUGH INFORMATION
TO REPRODUCE THE REQUIRED ADAPTIVE AUTHORITY DECISIONS.

LEAVE-ONE-FIELD-OUT

MINUS AGE / RECENCY

accuracy:
0.82365.

loss vs full:
3.97 percentage points.

MINUS EVIDENCE COUNT

0.85637.

loss:
0.70 points.

MINUS CAUSAL-CONTROL CONFIDENCE

0.80797.

loss:
5.54 points.

MINUS MODEL / CONTEXT FIT CONFIDENCE

0.82418.

loss:
3.92 points.

MINUS RESOURCE COST

0.81675.

loss:
4.66 points.

PRIMARY FIELD-INDEPENDENCE RESULT
In this synthetic cross-domain population,
the most damaging single omission is:

CAUSAL-CONTROL CONFIDENCE.

Resource cost,
age,
and fit confidence also carry large independent decision information.

Raw evidence count contributes less uniquely.

This does NOT establish universal importance ordering.

It does establish:
the tested variables are not all recoverable from trust magnitude alone.

EVIDENCE-MASS COMPRESSION
Replace:

AGE
+
COUNT

with one effective-evidence-mass scalar.

Accuracy:

0.84818.

Loss vs full:

1.52 percentage points.

INTERPRETATION
Age and sample support are partially compressible.

A single effective-evidence-mass quantity can preserve much of their joint utility.

This is a promising state-reduction direction.

However:
the compression is not lossless.

A young/high-count estimate
and
old/high-count estimate
can still require different treatment
depending on the domain.

APPLICABILITY COMPRESSION
Replace:

CAUSAL CONFIDENCE
+
FIT CONFIDENCE

with their product.

Accuracy:

0.83253.

Loss vs full:

3.08 percentage points.

PRIMARY NON-COLLAPSIBLE RESULT
Causal validity and representation/context fit answer different questions.

Examples:

HIGH FIT
+
LOW CAUSAL CONTROL

means:
the current state may be well represented,
but consequence attribution is unsafe.

HIGH CAUSAL CONTROL
+
LOW FIT

means:
the causal baseline may be trustworthy,
but the stored model/context may not apply.

Their product hides which failure occurred.

Therefore:

CAUSAL CONFIDENCE
and
MODEL-FIT CONFIDENCE

should remain distinguishable
unless a future representation proves an information-preserving compression.

BOTH COMPRESSIONS
Use:

trust
+
effective evidence mass
+
applicability
+
cost.

Accuracy:

0.81986.

This is substantially worse than full typed state.

Thus aggressive scalar compression recreates the information-loss problem H23 warned about.

MINIMAL WORKING INTERPRETATION
The current research supports a compact generic trust object closer to:

TRUST VALUE

+

EVIDENCE FRESHNESS / MASS

+

CAUSAL VALIDITY

+

MODEL / CONTEXT FIT

+

RESOURCE PRICE

+

TYPE.

Raw age and raw evidence count may be candidates for partial compression into:
EFFECTIVE EVIDENCE MASS.

Causal validity and fit confidence should remain separate.

TYPE IS NOT A SEMANTIC ENVIRONMENT ID
The type identifies:

WHAT ADAPTIVE QUESTION THIS TRUST INSTANCE ANSWERS.

Examples:

expression trust;

control trust;

nomination trust;

context trust;

resource-policy trust.

It does not identify:
which external regime
or
which semantic task
the cell is in.

RELATION TO H23
H23:

share the update rule,
not the authority state.

H24:

share the field vocabulary where possible,
but do not force independent uncertainty dimensions into one scalar.

Together:

ONE COMPACT META-RULE
+
SMALL TYPED LOCAL STATE

is currently better supported than either:

many bespoke controllers

or

one global confidence value.

RELATION TO H5-H22
The retained fields map directly to prior failure modes.

TRUST VALUE:
current degree of authority.

EVIDENCE FRESHNESS / MASS:
H6 stale-prior suppression,
S9 control retirement,
H16 delayed-credit freshness.

CAUSAL VALIDITY:
S1-S9,
H12,
H20-H22.

MODEL / CONTEXT FIT:
H7,
H17-H20.

RESOURCE PRICE:
S4-S6,
H8,
H13-H15,
H21-H22.

This is not accidental duplication.

These are distinct axes repeatedly required by independent experiments.

IMPORTANT LIMITATION
The synthetic authorization rule is constructed from these candidate fields.

Therefore H24 is an:
ABLATION / IDENTIFIABILITY LOWER-BOUND STUDY,

not independent evidence that nature or real Yggdrasil must use exactly this state vector.

Its value is architectural:

if future implementation removes one of these distinctions,
it should provide another state variable that carries the missing information.

DECISION
AR-H24 supports a compact typed meta-state,
but rejects aggressive one-scalar compression.

Supported synthetically:

- trust magnitude alone is insufficient;
- recency/freshness contains independent information;
- causal-control confidence is not interchangeable with model-fit confidence;
- resource cost must remain visible to authority decisions;
- age and evidence count are partially compressible into an effective-evidence-mass quantity;
- a shared field vocabulary can support several trust types.

Not demonstrated:

- final field count;
- final numerical encoding;
- learned trust-type discovery;
- real memory footprint savings;
- real Yggdrasil implementation cost;
- hardware-optimal representation.

CLEAN SCIENTIFIC PAUSING POINT
H19-H24 form a coherent integration sequence:

H19:
temporal continuity rejects brief false context,
but not persistent false context.

H20:
functional causal validation distinguishes genuine vs persistent false context.

H21:
functional validation itself must be value-gated.

H22:
challenge value can be learned,
but maturation, staleness, and confounding remain.

H23:
one generic trust update form is reusable,
but trust state must remain domain-local.

H24:
the generic local trust object can likely be compact,
but causal validity,
fit,
resource price,
and freshness are not safely collapsible into one confidence scalar.

NEXT HIGH-VALUE MOVE
AR-H25 — END-TO-END GENERIC META-RULE COMPOSITION

Instead of another isolated synthetic toy,
compose the current generic meta-state into one bounded multi-layer developmental loop containing:

- fast role adaptation;
- inherited prior expression;
- causal-control selection;
- context routing;
- evidence-budget allocation;
- structural candidate nomination.

Question:

Does the shared typed meta-rule remain stable when all of those adaptive layers operate simultaneously
and their trust updates interact?

Primary risks:

- oscillatory feedback between trust layers;
- deadlock where every layer waits for another layer's confidence;
- runaway probing;
- structural-write starvation;
- coupled stale-state cascades.

This should be the next systems-level synthetic integration test.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
synthetic_decisions = 300000
fit_decisions = 180000
heldout_decisions = 120000
full_typed_accuracy = 0.86333
trust_only_accuracy = 0.68935
