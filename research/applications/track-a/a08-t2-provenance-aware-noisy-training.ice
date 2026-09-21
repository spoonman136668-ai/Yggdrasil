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


PRE-RUN IMPLEMENTATION FREEZE 01 — A08 TRAINING T2 PROVENANCE-AWARE NOISY EXPERIENCE

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE DERIVATION OF ANY PRIMARY A08 TARGET,
CORRUPTED-ROOT PAIR,
ROOT-ARRIVAL ORDER,
DUPLICATE FANOUT,
OR LEARNER EVENT ORDER.

IMPLEMENTATION COMMIT

4a25d1e417f10dbe854a43f712c926d323bfb53f.

SOURCE BUNDLE

Loader:

research/applications/track-a/a08_t2_provenance_noisy_training_v1.py

Loader Git blob:

c2f2477917bac636a68adadc4b1fdd9dfb8a3aaa.

Payload:

research/applications/track-a/a08_t2_provenance_noisy_training_v1.py.gz

Payload Git blob:

1204196e7b4f39bf1ac6d1371924d564187a56b3.

Compressed payload SHA-256:

ef3e87bd5a9a7484a3f640805e9451287f134632e08c2d0a56beb0552a4d1ae4.

Compressed payload bytes:

8414.

Decompressed source SHA-256:

0dc330887718767812b2143877b751dc1ad580e0cefe834afac88486ad5707e0.

Decompressed source bytes:

29943.

FROZEN PARENT

A07 source SHA-256:

de26ba2c1530f9086a878521f4705896c8f2ad332179ceec0fde9d5f6d71d0ad.

A07 freeze:

ee9014bde9c210ca31fbea7d94bb2a514c6e6f62.

A07 manifest:

6abcdd47683edf0b5b4c814518b19709d205f69f25e5db49b3057526f3818139.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Experience roots:

6 pairwise distinct roots.

Primary corruption budget:

2 roots per scenario.

Qualification threshold:

4 distinct non-conflicted roots.

Quadratic target catalog:

840.

Training feature rank:

11 / 11.

Mechanical manifest used only:

MECHANICAL-NONPRIMARY-FREEZE.

Mechanical manifest SHA-256:

1a3946154c88bb654848ba000e8dc82ab6ef67e0803b0a5d3e125e89035ad22f.

No real primary target,
corruption pair,
arrival order,
duplicate pattern,
or learner event order derived:

TRUE.

FULL NON-PRIMARY T2 SMOKE

12 / 12 learner A exact reconstructions.

12 / 12 learner B exact reconstructions.

12 / 12 learner-pair agreement.

120 / 120 unseen held-out predictions correct.

12 / 12 hereditary commits.

Service requests:

55296.

Candidate served / correct:

52273 / 52273.

Candidate incorrect:

0.

Raw experience observations across both learners:

3936.

Same-root duplicate observations collapsed:

2352.

Stale-program served:

0.

Natural migration inheritance:

245.

All dedicated noisy-experience probes:

PASS.

All required unsafe controls / governance fail-closed checks:

PASS.

Four-corrupted-root boundary:

EXPOSED.

Forged-root-metadata boundary:

EXPOSED.

All restarts:

equivalent.

All existing constitutional safety totals:

zero.

These used the literal fake freeze label
MECHANICAL-NONPRIMARY-FREEZE
and are implementation validation only.

They are not A08 scientific evidence.

PRIMARY STATUS AT THIS FREEZE

NOT DERIVED.

Let the resulting freeze-update commit SHA be F08.

Only after F08 exists may the harness derive:

- 12 target programs;
- 12 corrupted-root pairs;
- per-input six-root arrival orders;
- per-root duplicate fanout;
- learner-local raw-event processing orders.

No post-freeze rejection or replacement is allowed except the preregistered target equality retry.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-FREEZE PRIMARY NOISY-TRAINING MANIFEST — BEFORE FIRST PRIMARY EXPERIENCE EVENT

DATE:
2026-09-21.

FREEZE COMMIT F08

de08cc900d6e306411ae879114b3b648f0a94708.

TRAINING / NOISE MANIFEST SHA-256

1324fa1fd16e0250520f380f1872006627a5777207b2b537a6297dc26605274a.

This SHA binds:

- 12 target quadratic programs;
- 12 corrupted-root pairs;
- all per-input six-root arrival orders;
- all per-root duplicate fanout counts;
- frozen learner roots;
- train / holdout split;
- qualification threshold.

LEARNER EVENT-ORDER MANIFEST SHA-256

ebcbc5dae8a06128f43753ad5350c12adc365241729de1a66d53a253f44fa062.

This second SHA binds the deterministic learner-A and learner-B
raw-event processing order for every primary training epoch.

PRIMARY SCENARIOS

S00:
target role 0;
training epochs 82..103;
commit epoch 104;
coefficient mask 188;
target 0xe1b4;
corrupted roots E1,E2;
raw experience copies per learner 160;
experience schedule SHA-256 0f91cc468377f10d2c1f5c1ed90775f3d596e3de05e44095737865412fa97851.

S01:
target role 2;
training epochs 158..179;
commit epoch 180;
coefficient mask 348;
target 0xa35c;
corrupted roots E0,E4;
raw experience copies per learner 163;
experience schedule SHA-256 1dbfccbd90f905ddea846c5d23c96e13045711d65687fb023e31ea22c11c8925.

S02:
target role 2;
training epochs 81..102;
commit epoch 103;
coefficient mask 970;
target 0x5c3a;
corrupted roots E1,E4;
raw experience copies per learner 173;
experience schedule SHA-256 7de6ccca37759265142e90d7b92b2248e822cc0dd9d910d0426f77e38ec08113.

S03:
target role 0;
training epochs 101..122;
commit epoch 123;
coefficient mask 1667;
target 0xc355;
corrupted roots E0,E3;
raw experience copies per learner 174;
experience schedule SHA-256 872b5b3ed049b3bbc62f8e9604a1868f2523ba8c189437c6b8d3ef8f4fa9eafc.

S04:
target role 3;
training epochs 186..207;
commit epoch 208;
coefficient mask 1802;
target 0xa69a;
corrupted roots E3,E5;
raw experience copies per learner 172;
experience schedule SHA-256 d6c9471c06f9144a2560e08b787ef73f88e20db9a793cb0a326e86667056ae83.

S05:
target role 1;
training epochs 97..118;
commit epoch 119;
coefficient mask 1092;
target 0x9c6c;
corrupted roots E3,E5;
raw experience copies per learner 159;
experience schedule SHA-256 cb02352dbddb3f1656e8f4d322018377510846d6b832433062f903c986c2d538.

S06:
target role 3;
training epochs 132..153;
commit epoch 154;
coefficient mask 1970;
target 0x8be2;
corrupted roots E4,E5;
raw experience copies per learner 147;
experience schedule SHA-256 fed934399e1bf2b4000b92a18bf703a025f5da7623fc315bb8c17a4777506ac5.

S07:
target role 0;
training epochs 133..154;
commit epoch 155;
coefficient mask 270;
target 0x5656;
corrupted roots E2,E5;
raw experience copies per learner 150;
experience schedule SHA-256 f55b7954dec310ee8dc4ba6efa670fa3a4c328ab790099da40706987b167d7eb.

S08:
target role 0;
training epochs 138..159;
commit epoch 160;
coefficient mask 1899;
target 0x714d;
corrupted roots E1,E5;
raw experience copies per learner 159;
experience schedule SHA-256 8643d021609da13ce8c10a256625d9ee3049e17843b6491d8a527f52d9f413b3.

S09:
target role 0;
training epochs 97..118;
commit epoch 119;
coefficient mask 1167;
target 0x3369;
corrupted roots E0,E5;
raw experience copies per learner 156;
experience schedule SHA-256 44efcdb6de08763025fb55744117981b4a321f6361831824e75fde03280943f7.

S10:
target role 3;
training epochs 118..139;
commit epoch 140;
coefficient mask 644;
target 0xaacc;
corrupted roots E0,E1;
raw experience copies per learner 164;
experience schedule SHA-256 504de1eef27c19ab1ddcc15a30257009a234eeb42506b279a64cd6ba9422aeff.

S11:
target role 3;
training epochs 86..107;
commit epoch 108;
coefficient mask 971;
target 0xa3c5;
corrupted roots E1,E2;
raw experience copies per learner 157;
experience schedule SHA-256 dcc7749589dc3e2d0660b68c09c0fef2495b60d7a5f0181edb7ec9f912de7b8e.

All target derivation counters:

0.

Total raw experience copies across one learner over all 12 primary scenarios:

1934.

The second learner receives the same raw event multiset
in independently derived event order.

No target,
corrupted-root pair,
root arrival,
duplicate fanout,
learner event order,
training example,
or held-out label was replaced after derivation.

At the moment this manifest was recorded:

A08 primary experience events consumed = 0.
A08 primary service requests served = 0.

MANIFEST RECONSTRUCTION VALIDATION

Because the sandbox no longer retained the accepted A02 / A03 runtime modules,
manifest derivation was independently reconstructed from the frozen deterministic rules.

Before accepting that reconstruction,
the same path reproduced exactly:

accepted A05 task-program manifest SHA-256:
3fbc3a77eef9068dba92f4206c8c5c7a180efafec2a0105aa52e978dea0fc7f6.

accepted A07 training manifest SHA-256:
6abcdd47683edf0b5b4c814518b19709d205f69f25e5db49b3057526f3818139.

Therefore the A08 manifest derivation path is evidence-bound to two previously accepted manifest anchors.

This note records manifest derivation only.
It is not A08 primary scientific execution.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-MANIFEST STATIC AUDIT — NON-EVIDENCE / PRIMARY UNSPENT

DATE:
2026-09-21.

STATUS:
STATIC MANIFEST VALIDATION ONLY.

No primary experience event was consumed.
No primary service request was executed.
No A08 primary result is claimed.

STATIC AUDIT RESULT

All 12 scenarios:

PASS.

For every scenario:

- target coefficient mask / truth table belongs to the frozen 840-program quadratic class;
- target differs from the current version-0 target-role program;
- training_start = commit_epoch - 22;
- first-round three-root evidence cannot meet the frozen four-root qualification threshold;
- after all six roots report,
  exactly four distinct roots carry the correct label
  and exactly two distinct roots carry the corrupted label.

RAW VS EFFECTIVE EXPERIENCE

Across one learner over all 12 primary scenarios:

raw experience copies:

1934.

Distinct effective root observations:

792.

Same-root duplicate observations that must collapse:

1142.

Therefore duplicate fanout is substantial in the real frozen primary manifest
and cannot accidentally equal effective evidence count.

Per-scenario raw / effective / collapsed counts:

S00:
160 / 66 / 94.

S01:
163 / 66 / 97.

S02:
173 / 66 / 107.

S03:
174 / 66 / 108.

S04:
172 / 66 / 106.

S05:
159 / 66 / 93.

S06:
147 / 66 / 81.

S07:
150 / 66 / 84.

S08:
159 / 66 / 93.

S09:
156 / 66 / 90.

S10:
164 / 66 / 98.

S11:
157 / 66 / 91.

EXECUTION INFRASTRUCTURE NOTE

A repository-native GitHub Actions primary workflow was attempted only after:

- F08 freeze;
- primary noisy-training manifest recording.

Workflow commit:

43b47a35362ac0ad81613c9cb5abc6da12835f8d.

GitHub Actions run:

35576880327.

Result:

FAILURE BEFORE RUNNER ALLOCATION.

Job:

primary.

No runner id / no workflow steps.

Therefore:

no frozen byte verification step executed;
no manifest execution step executed;
no primary sweep executed.

This is infrastructure-only non-evidence.

LOCAL RUNTIME NOTE

The current sandbox retains exact frozen A08,
A07,
A06,
and A05 source bytes,
but the accepted A02 / A03 runtime modules are no longer present locally.

The binary GitHub connector path does not provide a trustworthy byte-preserving materialization route for those missing gzip parents,
and the sandbox has no direct GitHub network transport.

No compatibility runtime,
hand-reconstructed organism,
or altered dependency chain will be substituted for primary evidence.

A08 primary therefore remains:

UNSPENT.

NEXT EXECUTION REQUIREMENT

Resume A08 primary only when one of the following exact-byte paths exists:

1. the accepted A02 / A03 runtime source bundles are restored into the sandbox
   with their recorded source SHA-256 values;

or

2. a repository-native runner successfully checks out the frozen Git objects
   and executes the exact A08 loader.

Until then:

do not alter the frozen A08 harness;
do not alter F08;
do not alter the recorded primary manifest;
do not consume partial primary experience.

canonical_scientific_execution = false.
stab18_r1_touched = false.
