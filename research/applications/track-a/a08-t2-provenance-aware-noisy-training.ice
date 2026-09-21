TITLE: YGGDRASIL TRAINING TRACK T2 / APPLICATION A08 — Provenance-Aware Noisy Experience and Distributed Learning Memory
DATE: 2026-09-20
STATUS: PREREGISTERED / NOISY-EXPERIENCE TRAINING GATE / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T2 / APPLICATION-A
PARENT: A07 T1 Experience-Dependent Hereditary Learning
BRANCH: dg1a-ar

PURPOSE

A07 established the first training result in the Yggdrasil lineage:

labeled experience
->
local program inference
->
held-out generalization
->
constitutional authorization
->
hereditary program state.

A07 also exposed its central training weakness.

Two computationally independent learner lineages can still agree on the same wrong program
when both are taught the same poisoned observation.

A08 asks:

CAN TRAINING EXPERIENCE ITSELF BECOME PROVENANCE-AWARE,
SO THAT REPEATED OR CORRELATED BAD OBSERVATIONS
DO NOT BECOME FALSE INDEPENDENT EVIDENCE?

And:

CAN PARTIALLY ACCUMULATED TRAINING EVIDENCE
SURVIVE PAUSE / RESTART
WITHOUT LOSING ITS PROVENANCE OR DOUBLE-COUNTING IT?

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No production deployment.
No network exposure.
No CKB / KTRADE integration.
No financial task.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

TRAINING CLAIM

A08 remains supervised training.

It does not claim:

independent discovery of training truth;
unsupervised learning;
open-ended learning;
neural gradient training;
adversarial robustness beyond the frozen provenance threshold.

The claim is:

within a frozen corruption model,
training observations are treated as provenance-bearing evidence rather than raw headcount,
allowing the organism to learn the correct hereditary program despite noisy,
duplicated,
and source-correlated labels.

FROZEN PARENT

A07 accepted source SHA-256:

de26ba2c1530f9086a878521f4705896c8f2ad332179ceec0fde9d5f6d71d0ad.

A07 freeze F07:

ee9014bde9c210ca31fbea7d94bb2a514c6e6f62.

A07 training manifest:

6abcdd47683edf0b5b4c814518b19709d205f69f25e5db49b3057526f3818139.

A07 accepted primary result SHA-256:

4e8d381a2f1fd4003066ad9ffe3911d89f3337703eb99b382796b15cb318d430.

A07 quadratic hypothesis class,
11 training inputs,
5 held-out inputs,
GF(2) solver,
A06 hereditary program authority,
and A03 service environments
remain unchanged unless explicitly stated below.

QUADRATIC PROGRAM CLASS

Carry forward A07 exactly.

11 binary coefficients.

Frozen target catalog:

840 balanced non-affine quadratic Boolean programs.

Training input indices:

0,1,2,3,4,5,6,8,9,10,12.

Held-out input indices:

7,11,13,14,15.

The training feature matrix remains rank 11 / 11 over GF(2).

EXPERIENCE PROVENANCE ROOTS

A08 introduces six independent training-experience roots:

E0 = 1 << 44.
E1 = 1 << 45.
E2 = 1 << 46.
E3 = 1 << 47.
E4 = 1 << 48.
E5 = 1 << 49.

These roots identify causal observation provenance.

Repeated observations from one root remain:

ONE effective source.

A copied descendant of one root remains:

ONE effective source.

No amount of same-root repetition creates an additional independent vote.

LEARNER LINEAGES

Carry forward two computational learner roots:

LEARNER_A_ROOT = 1 << 42.
LEARNER_B_ROOT = 1 << 43.

Learner-lineage independence remains distinct from training-evidence independence.

Both learners receive the same set of provenance-tagged experience events
but process events in separately derived deterministic orders.

They may not exchange:

row-reduction state;
qualified labels;
coefficient guesses;
candidate programs.

EXPERIENCE LEDGER

For every training input x,
each learner stores:

root -> observed label state.

Root state is one of:

UNSEEN;
LABEL_0;
LABEL_1;
CONFLICTED.

Rules:

first observation from a root records its label.

Repeated same-label observations from that same root:
do not increase effective evidence count.

If one root later supplies both labels for the same input:
that root becomes CONFLICTED for that input
and contributes no vote until the experiment ends.

A root cannot repair its own conflict by sending more copies.

QUALIFIED EXPERIENCE LABEL

For one training input:

count only distinct,
non-conflicted provenance roots.

label 0 is qualified iff:

at least 4 distinct roots report 0.

label 1 is qualified iff:

at least 4 distinct roots report 1.

With six total roots,
both labels cannot simultaneously reach four.

If neither reaches four:

ABSTAIN.

Record:

effective root count;
zero-root count;
one-root count;
conflicted-root count;
winning margin.

A learner may add one GF(2) training equation for input x
only after that input has a qualified label.

If the input remains unresolved:

no equation enters the model.

PRIMARY CORRUPTION MODEL

For each scenario,
exactly TWO of the six experience roots are scenario-wide corrupted roots.

A corrupted root flips every training label it reports in that scenario.

The other four roots report the correct target label.

Thus corruption is:

source-correlated across inputs
and
persistent across time.

It is not independent Bernoulli noise.

This intentionally tests whether root identity matters.

POST-FREEZE CORRUPTED-ROOT DERIVATION

No primary corrupted-root pair may exist before A08 freeze.

Let F08 be the exact A08 harness freeze commit.

For scenario s:

derive:

SHA-256(
"YGG-A08-CORRUPT-ROOTS|"
+ F08
+ "|"
+ decimal(s)
).

Use deterministic digest bytes to select two distinct roots from E0..E5.

No pair may be rejected or replaced.

POST-FREEZE TARGET PROGRAM DERIVATION

No A08 primary target program may exist before A08 freeze.

For scenario s:

derive:

SHA-256(
"YGG-A08-TARGET|"
+ F08
+ "|"
+ decimal(s)
+ "|"
+ decimal(counter)
).

Map deterministically into the same 840-program quadratic catalog.

Reject only equality with that scenario's current version-0 target-role program.

No difficulty shaping,
noise shaping,
or held-out filtering is allowed.

TARGET ROLE / COMMIT EPOCH

Carry forward the A07 / A06 selector exactly.

For each scenario:

choose the pre-partition demand transition with largest positive role increase.

Ties:

earliest transition;
then lowest role.

target_role =
selected role.

commit_epoch =
selected transition start - 1.

PRIMARY TRAINING WINDOW

A08 uses 22 training epochs:

training_start =
commit_epoch - 22.

Each of the 11 training inputs receives experience in TWO rounds.

Round 1:

training_start
through
training_start + 10.

Round 2:

training_start + 11
through
commit_epoch - 1.

For each input:

three distinct experience roots report in round 1.

the remaining three roots report in round 2.

Thus all six roots are eventually represented.

POST-FREEZE ROOT-ARRIVAL ORDER

For scenario s,
training input x,
experience root e:

derive order key:

SHA-256(
"YGG-A08-ROOT-ORDER|"
+ F08
+ "|"
+ decimal(s)
+ "|"
+ decimal(x)
+ "|"
+ decimal(e)
).

Sort all six roots ascending by digest.

First three:

round 1.

Last three:

round 2.

No arrival order is changed after freeze.

DUPLICATE EXPERIENCE FANOUT

Each root visit emits:

1 + (
first_byte(
SHA-256(
"YGG-A08-DUPLICATES|"
+ F08
+ "|"
+ decimal(s)
+ "|"
+ decimal(x)
+ "|"
+ decimal(e)
)
)
mod 4
)

copies.

Therefore each root contributes:

1..4 raw observations

but still:

exactly one effective provenance vote.

The primary must report both:

raw observation count
and
effective root count.

LEARNER EVENT ORDER

Within one training epoch,
Learner A and Learner B receive the same raw event multiset.

Each learner processes that epoch's events in its own deterministic order:

SHA-256(
"YGG-A08-LEARNER-EVENT-ORDER|"
+ F08
+ "|"
+ decimal(s)
+ "|"
+ learner_id
+ "|"
+ decimal(epoch)
+ "|"
+ event_id
).

Final qualified labels must be invariant to learner event order.

PRIMARY EXPERIENCE EXPECTATION

Because exactly four roots are honest
and exactly two are scenario-wide corrupted:

after all six roots have reported for one input:

correct label root count = 4.

incorrect label root count = 2.

Therefore:

correct label MUST qualify;
incorrect label MUST NOT qualify.

Duplicated corrupted observations must not change this.

After all 11 inputs complete round 2:

each learner should hold exactly 11 qualified correct equations;
rank should reach 11;
the inferred target program should be exact.

No learner may emit a complete candidate before all 11 inputs are qualified.

HELD-OUT GENERALIZATION

Carry forward A07 exactly.

Held-out labels:

7,11,13,14,15

never enter learner state.

Each learner candidate is evaluated on those five unseen inputs.

Required:

120 / 120 total held-out learner predictions correct.

PROGRAM AUTHORIZATION / HEREDITY

Carry forward A07 / A06 unchanged.

A learned candidate becomes authoritative only after:

Learner A candidate == Learner B candidate;

learner roots are pairwise disjoint;

candidate belongs to frozen 840-program class;

parent digest / version are valid;

existing organism governance passes;

existing registry qualification passes.

Then use the existing hereditary program commit,
migration inheritance,
wake catch-up,
repair catch-up,
stale-program exclusion,
and restart persistence.

PRIMARY SERVICE WORKLOAD

Use the exact 12 accepted A03 schedules.

384 epochs x 12 service requests x 12 scenarios
=
55296 service requests.

Experience events are additional training events
and do not count as service requests.

PRIMARY METRICS

Per scenario report:

target role;
target program;
two corrupted experience roots;
raw experience observation count;
effective experience roots per input;
round-1 status per input;
round-2 status per input;
same-root duplicates collapsed;
conflicted roots;
qualified labels;
abstentions;
learner ranks;
learner candidates;
held-out errors;
program commit;
hereditary metrics;
service metrics;
restart metrics.

PRIMARY REQUIRED COUNTS

12 / 12 exact learner-A target reconstructions.

12 / 12 exact learner-B target reconstructions.

12 / 12 learner-pair agreement.

120 / 120 held-out learner predictions correct.

12 / 12 hereditary commits.

0 incorrect served requests.

0 stale-program served requests.

At least one natural migration program inheritance.

Every training input:

final correct effective-root count = 4.

Every training input:

final incorrect effective-root count = 2.

Raw duplicate count MUST exceed effective evidence count
in at least one primary input.

No duplicate may change the effective root counts.

DISTRIBUTED MEMORY / RESTART

Learner state must be serializable.

Persist:

per-input root ledger;
conflicted-root state;
qualified-label state;
GF(2) equation state;
learner rank;
learner candidate if complete.

If an A03 restart falls inside the A08 training window:

the primary must resume learner state exactly.

Regardless of natural restart placement,
run dedicated probe M1:

restart both learners after round 1
and before round 2.

Required:

post-restart final learner ledgers,
qualified labels,
candidate programs,
and hereditary commit
match uninterrupted shadows exactly.

DEDICATED NOISY-EXPERIENCE PROBES

P1 — SAME-ROOT AMPLIFICATION

One corrupted root sends 64 copies of its wrong label.

Three honest roots each send one correct label.

A fourth honest root arrives later.

Required:

before fourth honest root:
ABSTAIN.

after fourth honest root:
correct label qualifies.

The 64 copies remain one effective bad root.

P2 — COPIED DESCENDANTS

Four nominal witnesses all descend from one corrupted root.

Required:

effective evidence count from that family = 1.

They cannot satisfy the four-root quorum.

P3 — UNRESOLVED 3 / 3 CONFLICT

Three roots report 0.
Three independent roots report 1.

Required:

ABSTAIN;
no equation;
no complete learned commit through that input.

P4 — SELF-CONTRADICTING ROOT

One root reports both labels for the same input.

Required:

root becomes CONFLICTED;
contributes zero votes.

With four independent honest remaining roots:

correct label can still qualify.

P5 — TWO CORRELATED BAD ROOTS

Two roots are wrong across all 11 inputs.

Four roots are correct across all 11 inputs.

Required:

exact target reconstruction;
all held-out predictions correct.

P6 — ROUND-1 MEMORY RESTART

Persist after first three roots per input.

Restart.

Consume remaining roots.

Required:

byte-equivalent final evidence ledger and candidate
to uninterrupted learner.

P7 — LEARNER-LINEAGE ORDER INVARIANCE

Learner A and B consume identical provenance-tagged evidence
in different event orders.

Required:

same qualified labels;
same coefficients;
same candidate.

P8 — HEREDITARY PROPAGATION

After learned commit,
exercise A06:

stale dormant wake;
migration into target role;
repair after update.

Required:

no stale-program service.

NEGATIVE / LIMIT CONTROLS

N1 — RAW HEADCOUNT VOTING

Unsafe control.

Let duplicate observations count as independent votes.

A corrupted root with sufficient fanout must be able to produce a false label majority.

Expected:

false training evidence reachable.

N2 — ROOT IDENTITY REMOVED

Unsafe control.

Treat all observations as anonymous.

Expected:

copied correlated evidence can become false independent support.

N3 — THREE / THREE FORCE-TIEBREAK

Unsafe control.

Force a label decision under 3 / 3 conflict.

Expected:

arbitrary false label reachable.

N4 — FOUR CORRUPTED ROOTS

Boundary.

If four genuinely distinct experience roots are coherently corrupted,
the frozen four-root quorum can qualify the wrong label.

Expected boundary.

N5 — FORGED ROOT METADATA

Boundary.

If one bad source can forge multiple independent root identities,
provenance-aware counting can be defeated.

Expected boundary.

N6 — GOVERNANCE UNAVAILABLE

Even a correctly learned candidate cannot commit without existing organism governance / registry qualification.

Expected:

no hereditary commit.

PRIMARY SIGNAL

A08_T2_PROVENANCE_AWARE_NOISY_TRAINING_SUCCESS

TRUE iff:

12 / 12 learner A exact target reconstruction
AND
12 / 12 learner B exact target reconstruction
AND
12 / 12 learner pairs agree
AND
120 / 120 held-out predictions correct
AND
12 / 12 hereditary commits
AND
TASK_ACCURACY == 1.0
AND
incorrect served requests == 0
AND
stale-program served requests == 0
AND
every primary input ends 4 correct roots / 2 incorrect roots
AND
same-root duplicates never increase effective evidence
AND
migration inheritance >= 1
AND
all M1 / P1..P8 probes pass
AND
N1..N3 expose unsafe controls as preregistered
AND
N6 fails closed
AND
all restarts are equivalent
AND
all existing authority / provenance / causal / resource safety totals remain zero.

BOUNDARY SIGNALS

N4 four-corrupted-root failure
and
N5 forged-root-metadata failure

are reported separately.

They do not count as primary failures.

They define the constitutional trust boundary of this T2 experiment.

REPRODUCIBILITY

Two complete deterministic A08 primary sweeps.

Serialized result SHA-256 must match exactly.

Post-freeze target,
corrupted-root,
root-arrival,
duplicate-fanout,
and learner-event-order manifests
must match exactly.

NO POST-RESULT TUNING

After F08 exists,
do not alter:

- six experience roots;
- two corrupted roots per primary scenario;
- four-root qualification threshold;
- root-conflict rule;
- duplicate collapse;
- 22-epoch two-round schedule;
- target derivation;
- root-arrival derivation;
- duplicate derivation;
- learner event-order derivation;
- quadratic hypothesis class;
- train / holdout split;
- hereditary authority path;
- probes;
- controls;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

A07 showed that Yggdrasil can learn from examples.

But both learners were taught by the same clean teacher.

A08 makes the classroom messy.

There are six independent sources of experience.

Two of them are wrong for the whole training episode.

Some sources repeat themselves several times.

Those repetitions are not allowed to become extra votes.

Yggdrasil must remember:

who told me this?

not merely:

how many times did I hear it?

For each training example,
four independent sources must agree before the label is allowed into the learner.

If the evidence is split,
the learner waits.

If one source contradicts itself,
that source is discarded for that example.

After the noisy evidence is resolved,
the cells still have to infer the program,
predict the five unseen cases,
pass constitutional authorization,
and inherit the learned program exactly as in A07.

The training memory also has to survive restart halfway through evidence collection.

This tests whether the provenance discipline that protected repair and governance
can now protect learning itself.

canonical_scientific_execution = false.
stab18_r1_touched = false.
