TITLE: YGGDRASIL A21 / T8E — Out-of-Sample Canary Activation Replication
DATE: 2026-09-21
STATUS: PREREGISTERED CONFIRMATORY REPLICATION / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8E / APPLICATION-A
PARENT: A20 Provisional Canary Patch Activation
BRANCH: dg1a-ar

PURPOSE

A20 discovered a one-sided activation signal on the known A17 worlds:

positive real-canary evidence
was followed by zero harmful expansion decisions
across C1 / C2 / C3.

But A20 reused the same frozen A17 demand / turnover worlds
whose behavior had already been exposed by A17-A19.

A21 is therefore a true out-of-sample replication.

It keeps:

the exact 48 learned patch contexts;
the exact A17 pre-evaluation starting cell states;
the same candidate and stale developmental priors;
the same A20 C1 / C2 / C3 canary decision rule.

It replaces:

the held-out demand sequence;
the epoch-0 replacement set;
the epoch-8 replacement set

with fresh post-F21 trajectories
that cannot exist before the A21 implementation freeze.

PRIMARY QUESTION

Does:

positive first-half real-canary consequence

continue to predict:

non-harmful second-half expansion

on fresh demand / turnover trajectories
that were unavailable during A17-A20 design?

FROZEN INPUT

A20 closure:

baa499248e98066d9b9ba5adbe30fb488dec631d.

A20 source SHA-256:

4e39349fba10c51116164d46a8cdda0d27bc23c0cae08742b281f3d19d6f7cb2.

A17 F17:

3ec24f8242285688a537f5e7dd6e9a231a645597.

The 48 patch contexts remain the exact A17:

12 scenarios x 4 patches.

For each context:

candidate prior = learned A17 patch target;
stale prior = immediately previous A17 learned prior;
starting cell state = exact A17 pre-evaluation candidate state.

A21 does not redraw patch targets.

A21 tests generalization across trajectory uncertainty,
not generalization across patch semantics.

A21 FREEZE

Let the exact A21 implementation freeze commit be:

F21.

No real A21 trajectory may be derived before F21 exists.

POST-FREEZE REPLICATION MANIFEST

After F21,
derive exactly:

8 independent trajectory replicas

for each of the 48 patch contexts.

Total fresh trajectories:

384.

For replica r in 0..7:

derive 16 evaluation demands as eight symmetric zero-mean pairs
around the already-learned candidate target
under:

YGG-A21-EVAL|F21|scenario|patch|replica|pair.

Derive epoch-0 and epoch-8 four-cell replacement sets under:

YGG-A21-REPLACE|F21|scenario|patch|replica|epoch|cell_id.

Replacement sets contain exactly four unique IDs.

The complete 384-trajectory manifest
must be hash-bound in the repository
before primary A21 execution.

No trajectory may be rejected
because of its expected result.

CANARY RULE

Exactly the frozen A20 rule.

C1:
1 / 4 candidate-controlled epoch-0 newborns.

C2:
2 / 4.

C3:
3 / 4.

Remaining epoch-0 newborns use stale prior.

A preserved all-stale twin starts from the identical state.

Run fresh epochs 0-7.

Decision:

canary service > stale twin:
EXPAND.

canary service == stale twin:
HOLD.

canary service < stale twin:
REVOKE.

At epoch 8:

EXPAND:
continue canary state;
4 / 4 candidate newborns.

HOLD:
continue canary state;
repeat the arm's original exposure fraction.

REVOKE:
restore exact stale-twin state;
0 / 4 candidate newborns.

Then run fresh epochs 8-15.

Epochs 8-15 remain invisible to the decision.

REFERENCE TRUTH

For every fresh trajectory also run:

R0 all-stale;
R1 all-candidate.

These are evaluation references only.

PRIMARY CONFIRMATORY SIGNAL PER ARM

An arm is REPLICATION-QUALIFIED iff all are true:

EXPAND decisions >= 48
AND
actual second-half harmful EXPAND rate <= 0.05
AND
full-candidate second-half harmful labels among EXPAND decisions <= 0.05
AND
actual EXPAND harm rate is no greater than half
the unconditional R1 second-half harm rate
when the unconditional harm rate is nonzero
AND
all restart / leakage / exposure / restore probes pass.

Coverage floor:

48 expansions

means the arm must earn expansion
on at least 12.5% of 384 fresh trajectories.

The 5% harm ceiling is fixed before F21.

No post-result threshold changes.

MINIMUM-EXPOSURE SELECTION RULE

A21 does not choose the highest-service arm.

If multiple arms are REPLICATION-QUALIFIED,
the selected arm for a future sequential-controller experiment is:

lowest unproven exposure first.

Selection order:

C1;
then C2;
then C3.

If C1 qualifies:
select C1.

Else if C2 qualifies:
select C2.

Else if C3 qualifies:
select C3.

Else:
no arm selected.

This hierarchy is frozen before results.

SECONDARY METRICS

For each arm report:

EXPAND / HOLD / REVOKE counts;

actual second-half harmful / neutral / beneficial EXPAND outcomes;

full-candidate second-half harmful / neutral / beneficial labels among EXPAND decisions;

canary-phase regret versus stale twins;

second-half delta versus stale twins;

complete service delta versus R0;

complete service delta versus R1;

revoked beneficial / neutral / harmful R1 opportunities;

held beneficial / neutral / harmful R1 opportunities;

maximum unproven exposure.

Report per-replica and per-patch-context concentration.

A result must not be carried by one scenario alone
without being disclosed.

INTEGRITY PROBES

P1:
A17 replay still equals 3978 / 3950 / 37-of-48 / 38 before A21 trajectory derivation.

P2:
384 unique trajectory identities.

P3:
each trajectory has exactly 16 demands
whose exact mean equals candidate target.

P4:
each trajectory has exactly four unique replacement IDs
at epoch 0 and epoch 8.

P5:
no A21 trajectory tag equals an A17 evaluation / replacement tag.

P6:
decision uses epochs 0-7 only.

P7:
C1 / C2 / C3 exposure limits exact.

P8:
stale twin and canary start byte-identical.

P9:
REVOKE restores exact stale-twin state.

P10:
two complete primary sweeps byte-identical.

P11:
no patch deletion;
no C-v3;
no duplicate context;
major history remains [v1,v2];
slot count remains 3.

P12:
all 8 replicas per each of 48 patch contexts are present.

NEGATIVE / LIMIT CONTROLS

N1:
always-patch R1 establishes unconditional fresh-world harm rate.

N2:
future leakage invalidates experiment.

N3:
dropping stale twin invalidates causal decision evidence.

N4:
selecting the highest-service arm after results is prohibited.

N5:
changing 5% harm ceiling after results is prohibited.

N6:
new patch semantics are not tested here.

N7:
sequential interaction between decisions remains untested.

INTERPRETATION

A21 is confirmatory.

A20 asked:

can bounded real exposure look useful?

A21 asks:

does that signal survive
when the future trajectory is genuinely new?

If no arm qualifies,
the A20 signal is not robust enough
for sequential autonomous authority.

If an arm qualifies,
only the preregistered minimum-exposure selection rule
may nominate it for the next experiment.

Even then,
A21 does not authorize production use.

A later experiment must test sequential patch decisions
where one activation decision changes the state inherited by the next.

PLAIN-SPEAK QUESTION

A20 looked promising,
but it tested worlds we already knew a lot about.

A21 creates hundreds of fresh futures
after the experiment is frozen.

The cells do not get to see those futures early.

They try the patch on a few newborns,
watch eight real steps,
and decide whether to expand.

Then we reveal the second half.

If positive canary evidence still almost never leads to harm
across hundreds of fresh futures,
we have something much stronger than a lucky result.

And if more than one canary size works,
we deliberately choose the smallest one,
not the one with the prettiest score.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
