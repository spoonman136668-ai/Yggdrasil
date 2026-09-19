TITLE: DG-1A-AR-H49 — Colluding / In-Range Local Price Manipulation Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE LOCAL-ANCHOR + TEMPORAL-BUDGET RESULT / COORDINATED-COLLUSION LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh48-asynchronous-adversarial-price-gossip-audit.ice

PURPOSE
H48 showed that large obvious price inflation can be strongly contained using:
- source provenance;
- duplicate collapse;
- freshness / TTL;
- robust neighborhood aggregation;
- direct local resource cross-check.

H49 attacks the next failure:

WHAT IF SEVERAL NEIGHBORS COORDINATE
AND
EACH MESSAGE STAYS INSIDE THE LOCAL CROSS-CHECK BOUND?

No one sender looks extreme.

The attack is:
small,
coherent,
and spatially coordinated.

QUESTION
Can local generative-memory price remain useful under slow coordinated in-range neighbor bias
without suppressing a genuine gradual scarcity increase?

BOUNDARY
This is synthetic.

It does not:
- establish adversarial security;
- freeze a local-anchor weight;
- freeze a temporal rate limit;
- prove real Yggdrasil price faults form contiguous clusters;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

FOCUSED PRICE FIELD
Spatial organism:
10 x 10 regions.

Each region has:
- true local structural-memory scarcity;
- noisy direct local scarcity observation;
- local price estimate;
- nearest-neighbor price messages.

H49 intentionally uses a lighter synchronous neighborhood transport model.

Reason:
H48 already established the asynchronous delay / duplicate / stale-message effects.

H49 isolates:
COORDINATED IN-RANGE BIAS.

COLLUDING REGION
A 3 x 3 neighboring cluster begins a slow coordinated price increase.

Attack interval:
steps 25..59.

Each colluding region gradually adds up to:

+0.35 synthetic price units

to its outgoing price signal.

The H48 single-message cross-check bound is:

0.45.

Therefore every malicious source remains individually plausible.

No single message is an obvious outlier.

COMPARATORS

BOUNDED NEIGHBOR GOSSIP
Blend:
55% direct local scarcity observation
+
45% neighbor price.

Clamp result to:
local observation +/- 0.45.

This represents the H48-style bounded-neighbor mechanism
without explicit coordinated-attack defense.

STRONG LOCAL CONSEQUENCE ANCHOR
Blend:
80% direct local resource/scarcity evidence
+
20% neighbor price.

This intentionally reduces neighbor authority.

TEMPORAL CHANGE BUDGET
Blend:
70% local
+
30% neighbor.

If neighbor consensus differs from direct local scarcity by more than:

0.10

then:
- cap neighbor-induced deviation from local scarcity to 0.10;
- cap one-step estimate movement to 0.03.

If local and neighbor evidence agree,
normal movement is allowed.

These constants are synthetic discriminating values only.

PRIMARY COLLUSION CONFIRMATION
50 matched spatial seeds.

PRE-ATTACK TOTAL PRICE MAE

BOUNDED:
0.02612.

LOCAL ANCHOR:
0.03271.

TEMPORAL:
0.02738.

The stronger local anchor is slightly noisier in clean conditions because it uses less neighborhood denoising.

DURING COORDINATED COLLUSION

BOUNDED

total price MAE:
0.03950.

attacked-cluster MAE:
0.13313.

remote false-high-price fraction:
0.0424%.

LOCAL ANCHOR

total:
0.03482.

attacked cluster:
0.05206.

remote false-high:
0.0168%.

TEMPORAL CHANGE BUDGET

total:
0.03313.

attacked cluster:
0.07263.

remote false-high:
0.0080%.

PRIMARY COLLUSION NEGATIVE
H48's large-fault cross-check is not sufficient against coordinated in-range bias.

Every source remains inside the allowed local deviation,
yet the cluster collectively raises local price.

Thus:

BOUNDED INDIVIDUAL MESSAGE INFLUENCE
DOES NOT GUARANTEE
BOUNDED COORDINATED GROUP INFLUENCE.

PRIMARY LOCAL-ANCHOR POSITIVE
Independent direct local scarcity evidence sharply limits the coordinated attack.

Attacked-cluster error falls from:

0.13313
to
0.05206.

This comes at a clean-state denoising cost.

Therefore:
neighbor advice and local direct evidence have a real bias/variance tradeoff.

PRIMARY TEMPORAL-BUDGET POSITIVE
The temporal price-change budget also limits coordinated drift:

cluster error:
0.07263.

It produces the lowest overall wrong branch-admission decision rate in the companion admission test.

Thus a useful price controller can ask not only:

IS EACH MESSAGE PLAUSIBLE?

but also:

IS THE AGGREGATE PRICE FIELD MOVING FASTER OR FARTHER THAN DIRECT LOCAL RESOURCE EVIDENCE SUPPORTS?

BRANCH-ADMISSION CONSEQUENCE
Synthetic candidate branch values are sampled around true local price.

Correct structural admission:
candidate value > true local price.

80 matched seeds.

COLLUDING ATTACK WINDOW

BOUNDED GOSSIP

false rejection of genuinely worthwhile branches
inside attacked cluster:
29.62%.

overall wrong admission decisions:
9.85%.

LOCAL ANCHOR

cluster false rejection:
12.48%.

overall wrong decisions:
9.12%.

TEMPORAL CHANGE BUDGET

cluster false rejection:
18.44%.

overall wrong decisions:
8.61%.

PRIMARY FUNCTIONAL PRICE RESULT
Coordinated price manipulation is not merely a price-estimation error.

It can cause:
LOCAL STRUCTURAL FREEZE.

Almost one-third of worthwhile branch opportunities are suppressed in the attacked cluster under the baseline bounded-gossip policy.

The stronger defenses substantially reduce that structural inhibition.

REAL GRADUAL SCARCITY CONTROL
A defense against slow malicious price drift must not freeze real gradual scarcity.

The colluding messages are removed.

Instead,
the attacked region's TRUE local scarcity gradually rises by:

+0.35

over approximately:
25 steps.

Direct local scarcity observations change accordingly.

50 matched seeds.

MID-RAMP TOTAL PRICE MAE

BOUNDED:
0.03033.

LOCAL ANCHOR:
0.03344.

TEMPORAL:
0.03017.

ATTACKED-REGION MAE

BOUNDED:
0.05928.

LOCAL ANCHOR:
0.03833.

TEMPORAL:
0.04974.

BRANCH-ADMISSION FALSE REJECTION DURING REAL SCARCITY

BOUNDED:
0.33%.

LOCAL ANCHOR:
2.23%.

TEMPORAL:
0.38%.

PRIMARY ADAPTATION POSITIVE
The temporal change-budget rule does NOT suppress the genuine scarcity ramp.

Reason:

LOCAL DIRECT RESOURCE EVIDENCE
moves with the real change.

The defense specifically limits:

NEIGHBOR-ONLY PRICE DRIFT
unsupported by local consequence.

This preserves the desired H48 asymmetry:

false advisory inflation
gets bounded.

real local scarcity
is allowed to rise.

PROVENANCE LIMIT
Ordinary sender provenance still matters,
but it is not sufficient here.

The colluding sources are genuinely different neighboring sources.

Therefore:

DIFFERENT SOURCE IDS
DO NOT AUTOMATICALLY MEAN
DIFFERENT FAILURE MODES.

This is the same distinction repeatedly observed in:
H10
H18
H40.

Failure-mode diversity matters more than raw identity count.

CURRENT LOCAL PRICE TRUST STACK
DIRECT LOCAL RESOURCE / SCARCITY EVIDENCE

+

NEIGHBOR PRICE FIELD

+

SOURCE PROVENANCE

+

MESSAGE FRESHNESS

+

DUPLICATE COLLAPSE

+

ROBUST AGGREGATION

+

LOCAL-DEVIATION BOUND

+

TEMPORAL CHANGE BUDGET

->

TRUSTED LOCAL MEMORY PRICE.

GENERAL PRINCIPLE
PRICE SHOULD BE ALLOWED TO MOVE QUICKLY WHEN:

DIRECT LOCAL RESOURCE CONSEQUENCE
AND
NEIGHBOR EVIDENCE
AGREE.

Price should move more cautiously when:

NEIGHBORS MOVE
but
LOCAL RESOURCE CONSEQUENCE DOES NOT.

This is a causal-control analogue for resource price.

HARD LIMIT
If colluding neighbor evidence
and
the direct local resource observation

share the same coherent corruption,
then H49's anchor is no longer independent.

The system returns to the common-mode identifiability problem.

No local price-only rule can manufacture truth from fully shared corruption.

DECISION
AR-H49 is POSITIVE with a coordinated-collusion limit.

Supported synthetically:

- individually bounded colluding neighbors can still create substantial collective price bias;
- coordinated price drift can suppress valuable structural branching;
- stronger direct local anchoring reduces local manipulation;
- a temporal neighbor-only change budget further limits unsupported drift;
- genuine gradual local scarcity still propagates when direct local evidence changes with it;
- raw source count does not imply failure-mode independence.

Not demonstrated:

- real Yggdrasil collusion/fault geometry;
- learned local-anchor weighting;
- adaptive temporal price budgets;
- subtle globally correlated local-scarcity corruption;
- price manipulation coupled to resource-transfer manipulation.

NEXT CLEAN QUESTION
AR-H50 — COUPLED RESOURCE-TRANSFER + PRICE MANIPULATION

H27-H29 control:
resource transport.

H47-H49 control:
memory-price information.

So far these control and data planes are mostly tested separately.

Question:

What happens when a faulty region simultaneously:
- inflates structural-memory price;
- attracts or withholds local resource;
- and biases the same neighborhood evidence used by both subsystems?

Compare:

A.
price and transfer trust sharing one provenance state;

B.
independent trust states for resource ownership vs price advice;

C.
cross-check between physical resource flow and advertised scarcity;

D.
failure when both channels share the same corruption.

Desired:

a bad PRICE source
should not gain:
RESOURCE OWNERSHIP AUTHORITY.

a bad TRANSFER source
should not automatically invalidate:
all price evidence.

This should test whether:
shared provenance
can coexist with
separate typed trust state,
as predicted by H23-H25.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
grid = 10x10
colluding_cluster = 3x3
collusion_ramp = 0..0.35
primary_spatial_seeds = 50
admission_test_seeds = 80
