# WSP-31 — one actual source-fact acquisition: DEV_SUPPORTED

One actual selected source answer improves **other, unqueried target answers**
from **2,492 to 2,662 /3,840**: +170 answers / **4.43 percentage points**. It also
beats an equal-budget connection-clarification answer by **78 /2.03 points** and
a fixed-first source query by **42 /1.09 points**. All frozen gain thresholds pass,
including competitiveness with both same-information trained head controls.

This is a **DEV_SUPPORTED actual learning result**, not WSP30's oracle bound.
One selected answer is directly stored as a known fact and used when refitting
the numerical router. It remains a small authored, correlated, finite-family
experiment with supplied memory/routing/query machinery, not complete training,
independent SCIENTIFIC_PASS or unknown-world intelligence.

| Arm | Actual new answers /case | Native correct /3,840 common unqueried labels | Shared-feature trained head | Fully gradient source/head |
|---|---:|---:|---:|---:|
| Impact-selected source fact | 1 | 2,662 | 2,368 | 2,442 |
| Fixed-first source fact | 1 | 2,620 | 2,374 | 2,380 |
| Impact-selected connection clarification | 1 | 2,584 | 2,290 | 2,136 |
| Same fact representation, no query | 0 | 2,492 | 2,256 | 2,184 |

The source arm meets preset gains >=77 over no-query, >=39 over connection query,
no worse than fixed-first source, and within 38 of each strong trained comparator.
Actual gains are 170, 78, 42 and +294/+220 versus the two trained heads.

## Fair scoring and representation control

All 120 actually acquired WSP29 modules remain, including the 13 imperfect modules.
The cohort is unchanged: 60 pairs x 16 source completions x two true recipes =
1,920 worlds. Every arm starts with the same 12 actual source observations and
five actual target observations. No true recipe, full hidden table or task ID is
passed to the model.

The connection query is selected **before its answer**. Its one answered target
point is excluded from scoring for **every** arm, including the source-query
arms. The other two inputs give 3,840 common never-queried target labels. Correctly
reciting an answered target question never counts as heldout success.

All arms receive the same faithful fact memory. Source facts override inferred
fallback guesses only at actually observed inputs; target fact slots return only
actually observed target labels. Unknown labels are canonical zero with a separate
known-mask bit and are not treated as true zeroes. The original WSP29 learner
scores 2,476 on these identical evaluation points; the new no-query representation
scores 2,492. That **16-answer representation-only effect** is separate from the
**170-answer actual-query effect**. More memory is not silently called learning
from a new fact.

## Acquisition and retention

For four unknown source points and three unknown target points, the planner
simulates hypothetical answers zero and one, refits only from existing actual
facts plus that hypothetical bit, and counts unknown-target prediction changes.
Numerical first-maximum gates select a source or connection query. This is a
supplied decision-sensitivity proxy, not guaranteed information-gain optimality.
It never sees the actual hidden answer until after selecting its question.

The source query selected bank0/input5 in 1,112 worlds, bank0/input6 in 452,
bank1/input5 in 108 and bank1/input6 in 248. The fixed-first control always asks
bank0/input5. Connection queries select target input3/5/6 in 1,660/216/44 worlds.
The question is a generic address in this supplied small world, not discovery of
an arbitrary measurement instrument or an open-ended experiment.

Each query arm receives one actual binary answer; the no-query arm receives none.
The query-used flag rejects further unknown answers. Identical queried evidence
can replay without mutation; contradictory or unsolicited answers reject. Actual
source answers alter only the selected source-fact slot. Existing unknown guesses
are not protected as if they were established facts.

All **130,560 old-fact checks**, 5,760 acquired-fact checks, 5,760 queried-evidence
replays, 122,880 source-locality checks and **7,680 cold restores** pass. Immutable
base-bank bytes are retained in all 7,680 arm states. Same initial evidence gives
the same questions; same augmented actual evidence gives the same predictions,
verified without giving hidden world identity to any learner. These are faithful
known-fact and base-weight retention results, not noise robustness, preservation
of every old guess, or lifelong memory for arbitrarily many tasks.

## Capacity and actual cost

Persistent writable state is **207 binary scalars**: 150 unchanged bank weights,
32 source known-mask/label bits, 16 target known-mask/label bits, seven route bits,
one occupied bit and one query-used bit. This adds 49 writable bits over WSP29.
Runtime also holds 16 redundant circuit-derived fallback bits and up to seven
two-bit impact scores, for up to **237 resident value bits** before the supplied
VM/program, object metadata and transient state. Twelve route descriptors add 84
static bits; seven query descriptors, memory addressing and the learning rule are
programmed. This is bounded instance learning, not invention of a new primitive.

Fallback values are computed from actual acquired circuits, not true hidden
labels. They are reconstructed at cold restore and never serialized as an
external truth oracle. The impact-score cache is derived from actual state,
shared only across identical-knowledge arm clones, and invalidated on a fact
write. Planning uses 1,920 shared passes /26,880 counterfactual answer states;
all arms pay the same shared prefix work. Two temporary branch states, routing
scores and memory operations are part of its cost.

One canonical checkpoint is 1,711–1,720 bytes depending on the fixed mode tag.
Measured retained native Python state is up to 5,222 bytes. These physical sizes
are larger than packed bit counts. Peak process RSS and energy are unmeasured.
The first complete local assay took **43.89s**, including 11.34s shared planning
and 7.83s conventional fits/features. Per-arm sections include cold/retention
checks; shared validation and artifact overhead are included in whole time.
This is not a matched end-to-end speed/energy comparison between architectures.

## Genuine trained controls and exact reuse

Each arm's two source-logit models and two target heads receive only that arm's
actual known facts and its actual selected question/answer. One head uses the
same native fact-corrected features; the other learns source logits by gradients
before building composed features. They are yoked-information learning controls,
not independent active-query planners. Float capacity, Adam moments, caches and
priors differ; better heldout scores here are not universal superiority over
conventional training.

There are **30,720 logical fit requests**, with **4,592 actual fresh converged fits**
and **26,128 exact-key hits**. All receipts satisfy frozen BCE<=0.01. Fresh work
executes 430,417 Adam updates. Cache keys cover complete training vectors/labels,
width, actual source/target fact masks/labels, upstream payload hashes, feature
representation, optimizer settings and implementation/source provenance. They
contain no true recipe or hidden world ID. Source/target changes miss; equal
actual evidence reuses only an identical semantic computation. Cache memory is
measured at 3,307,196 Python bytes. No nonexistent extra training is claimed.

## Freeze, custody and reproduction

Remote preregistration preceded implementation and the first primary run.
`result.json` contains every primary metric and all 1,920 per-world question,
answer, prediction and checkpoint receipts. Its trace rows are compacted only by
whitespace; loading it and serializing with standard sorted-key two-space JSON
plus newline exactly reconstructs the original primary stdout. Both hashes and
the reconstruction check are recorded in `provenance.json`. No data, prediction,
threshold or learning code was changed after the primary result.

Reproduce: `python research/contrib/chatgpt/WSP-31/run_dev.py`.
Full final qualification: `python research/contrib/chatgpt/WSP-31/qualify.py` — all
original and WSP01–17/WSP19–31 unit suites, full frozen assay, G29 and clean source
at exact final SHA/tree on hosted Ubuntu and Windows. Complete trace stays in the
repository; console receipts omit only duplicate trace arrays. Exact integer
outputs, queries, cache counts and digests must match across platforms; floating
losses are separately checked against the frozen convergence threshold.

The existing workflow is reused. No new workflow, private runner,
owner/controller/queue/scheduler, paid API, merge, accepted state, integration or
deployment is introduced. Earlier hypotheses and evidence remain unchanged.

## Next research implication

The model can acquire a small missing fact, store it directly and improve answers
about a composed task while retaining existing actual facts. Generalization is
still limited by the supplied representation, query proxy, remaining unknown
facts and ambiguous connections. A separately frozen successor should test
cumulative acquisition and interference under bounded memory/queries, with all
source modules and strong controls preserved. No successor run has started here.
