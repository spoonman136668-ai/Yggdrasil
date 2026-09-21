TITLE: YGG-A10-FIXA — Guaranteed-Different One-Learner Unsafe-Control Alignment
DATE: 2026-09-21
STATUS: PREREGISTERED / CONTROL-ONLY CORRECTIVE REPLICATION / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T3
PARENT: A10 Developmental Prior R1
BRANCH: dg1a-ar

PURPOSE

A10 R1 reproduced exactly but returned FALSE because N3 failed to construct
an actually different developmental prior in S07 and S08.

The organism,
training,
developmental policy,
replacement behavior,
service result,
restart result,
and safety result all passed.

A10-FIXA asks:

DOES THE FROZEN A10 RESULT BECOME POSITIVE
WHEN N3 IS MADE CAPABLE OF CONSTRUCTING
A GUARANTEED-DIFFERENT VALID DEVELOPMENTAL PRIOR,
WITH ZERO CHANGE TO ORGANISM BEHAVIOR?

FROZEN R1

A10 source SHA-256:

d27d0074f08b6ae613e72a03d018af6b4bda9fd7dffb9615c687c286aca5e73e.

Freeze F10:

cf1a9f459861177cb1e9a0e22c6c68684a543514.

Developmental manifest:

917d82b907a01b7bba4fff972b3f9aca691df7a7f368d0bd34fe9baf7c243cc2.

R1 serialized output SHA-256:

2290d3caabf38c6bd052885f3e70c5e06756a7609b46e44d0940dd7f83b60615.

R1 task-output SHA-256:

09b8fc2000917642b526c3a065839b81d2f6a2c50d2db9d1a37c4c3bfe82844d.

ALLOWED CHANGE

Only N3 negative-control false-candidate construction.

For scenario s:

latent = scenario latent developmental prior.

forged_prior =

the lexicographically first entry in the frozen 124-prior catalog
such that:

forged_prior != latent.

This guarantees:

forged_prior is a valid developmental prior;
forged_prior is different from the learned truth.

The unsafe control then asks:

if a system auto-authorized one learner's forged valid prior
without independent learner agreement,
could false developmental-policy authority be created?

Required unsafe-control result:

TRUE.

FORBIDDEN CHANGES

Do not change:

F10;
developmental manifest;
latent priors;
training vectors;
evaluation vectors;
learner orders;
distributed memory;
learner algorithm;
policy authorization;
birth-role selector;
replacement targets;
task programs;
migration;
repair;
restart;
baseline;
oracle;
thresholds;
P1..P6 probes;
N1;
N2;
N4;
N5;
primary service metrics.

EQUIVALENCE REQUIREMENTS

FIXA must reproduce exactly:

task-output SHA-256 =
09b8fc2000917642b526c3a065839b81d2f6a2c50d2db9d1a37c4c3bfe82844d.

candidate first4 served =
1985.

baseline first4 served =
1922.

oracle first4 served =
1985.

baseline migrations avoided =
29.

candidate incorrect =
0.

stale-program served =
0.

candidate >= baseline scenarios =
12 / 12.

candidate > baseline scenarios =
12 / 12.

All non-N3 R1 primary signals must remain TRUE.

PRIMARY CORRECTIVE SIGNAL

A10_FIXA_CONTROL_ALIGNMENT_VALID

TRUE iff:

R1 source hash matches
AND
F10 unchanged
AND
developmental manifest unchanged
AND
task-output SHA matches R1
AND
all R1 aggregate equivalence anchors match
AND
every scenario N3 forged prior is valid
AND
every scenario N3 forged prior differs from latent
AND
all corrected N3 controls expose one-learner false authority
AND
all other primary signals remain unchanged.

CORRECTED T3 SIGNAL

A10_T3_DEVELOPMENTAL_PRIOR_LEARNING_ACCEPTED

TRUE iff:

A10_FIXA_CONTROL_ALIGNMENT_VALID
AND
all original A10 substantive primary signals are TRUE.

REPRODUCIBILITY

Two complete deterministic FIXA sweeps.

Serialized FIXA result SHA-256 must match exactly.

NO POST-RESULT TUNING.

PLAIN-SPEAK PREREGISTERED QUESTION

The organism passed.

One test of an intentionally unsafe shortcut was badly constructed.

It tried to make a wrong policy by swapping two numbers,
but sometimes those numbers were equal.

FIXA changes only how that fake bad policy is chosen.

It picks a different valid policy every time.

Then we rerun the exact same frozen developmental worlds.

If all real Yggdrasil behavior is byte-equivalent
and the unsafe one-learner shortcut is now exposed in all twelve cases,
the T3 result is accepted without rewriting R1.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A10-FIXA CONTROL ALIGNMENT

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE FIRST A10-FIXA PRIMARY EXECUTION.

IMPLEMENTATION COMMIT

1a9a4c471660c66aa83c357099d61a15c8e1539a.

SOURCE BUNDLE

Loader:

research/applications/track-a/a10_fixa_control_alignment_v1.py

Loader Git blob:

df1a6e6f956fb0a8b9622a4d9f8e4dd933a29659.

Payload:

research/applications/track-a/a10_fixa_control_alignment_v1.py.gz

Payload Git blob:

473363e7c9ab083ccf7015702aba8534604ebc45.

Compressed payload SHA-256:

dc23313b69ee205ada306b87d18776216f3408b88f94d902f75c4940bf3f55a2.

Compressed payload bytes:

2132.

Decompressed source SHA-256:

b1cd02b88ea64f9f60c4ae8fb9372bd6b595a3c6e99120499dd3d043a512ae8e.

Decompressed source bytes:

4969.

FROZEN R1 WORLD

Original A10 freeze F10:

cf1a9f459861177cb1e9a0e22c6c68684a543514.

Developmental manifest SHA-256:

917d82b907a01b7bba4fff972b3f9aca691df7a7f368d0bd34fe9baf7c243cc2.

R1 source SHA-256:

d27d0074f08b6ae613e72a03d018af6b4bda9fd7dffb9615c687c286aca5e73e.

R1 serialized output SHA-256:

2290d3caabf38c6bd052885f3e70c5e06756a7609b46e44d0940dd7f83b60615.

R1 task-output SHA-256:

09b8fc2000917642b526c3a065839b81d2f6a2c50d2db9d1a37c4c3bfe82844d.

MECHANICAL PRECHECK — NON-EVIDENCE

Wrapper syntax:

PASS.

Wrapper validate():

PASS.

R1 source hash:

MATCH.

R1 developmental manifest:

MATCH.

Corrected N3 forged-prior constructor:

valid frozen-catalog prior in 12 / 12 scenarios.

Corrected N3 forged prior differs from latent prior:

12 / 12 scenarios.

No organism decision,
training observation,
evaluation observation,
replacement target,
developmental-policy rule,
task program,
baseline,
oracle,
threshold,
or substantive primary metric is changed by the wrapper.

No A10-FIXA primary run occurred before this freeze.

PRIMARY EQUIVALENCE REQUIREMENTS

The FIXA run must reproduce exactly:

task-output SHA-256 =
09b8fc2000917642b526c3a065839b81d2f6a2c50d2db9d1a37c4c3bfe82844d;

candidate first-four-epoch served =
1985;

baseline first-four-epoch served =
1922;

oracle first-four-epoch served =
1985;

baseline migrations avoided =
29;

candidate incorrect =
0;

stale-program served =
0;

candidate >= baseline scenarios =
12 / 12;

candidate > baseline scenarios =
12 / 12.

The only intended correction is:

N3 ONE-LEARNER FALSE POLICY AUTHORITY REACHABLE

must now be evaluated with a guaranteed-different valid prior in every scenario.

REPRODUCIBILITY

Execute two complete deterministic FIXA sweeps.

Serialized FIXA output SHA-256 must match exactly.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — A10-FIXA GUARANTEED-DIFFERENT ONE-LEARNER CONTROL ALIGNMENT

DATE:
2026-09-21.

STATUS:
CLOSED / POSITIVE CORRECTIVE PRIMARY / REPRODUCIBLE /
A10 T3 DEVELOPMENTAL PRIOR LEARNING ACCEPTED VIA FIXA / NON-CANONICAL.

FROZEN FIXA HARNESS

Implementation commit:

1a9a4c471660c66aa83c357099d61a15c8e1539a.

Freeze commit:

e3a4b6f98e01b2762784aa5409832f06f1ea05f8.

Decompressed FIXA source SHA-256:

b1cd02b88ea64f9f60c4ae8fb9372bd6b595a3c6e99120499dd3d043a512ae8e.

Source bytes:

4969.

Compressed payload SHA-256:

dc23313b69ee205ada306b87d18776216f3408b88f94d902f75c4940bf3f55a2.

Compressed payload bytes:

2132.

ORIGINAL FROZEN A10 WORLD

A10 freeze F10:

cf1a9f459861177cb1e9a0e22c6c68684a543514.

Developmental manifest SHA-256:

917d82b907a01b7bba4fff972b3f9aca691df7a7f368d0bd34fe9baf7c243cc2.

R1 source SHA-256:

d27d0074f08b6ae613e72a03d018af6b4bda9fd7dffb9615c687c286aca5e73e.

R1 frozen implemented signal remains:

A10_T3_DEVELOPMENTAL_PRIOR_LEARNING_SUCCESS = FALSE.

That R1 result is preserved and is not rewritten.

REPRODUCIBILITY

Two complete deterministic FIXA sweeps.

Sweep 1 serialized output SHA-256:

9df5d9a29f1533243eb5eb52b54fe92dd71bf2a6edded44d47cf10c83c628573.

Sweep 2 serialized output SHA-256:

9df5d9a29f1533243eb5eb52b54fe92dd71bf2a6edded44d47cf10c83c628573.

Byte-identical:

TRUE.

CORRECTIVE PRIMARY SIGNALS

A10_FIXA_CONTROL_ALIGNMENT_VALID:

TRUE.

A10_T3_DEVELOPMENTAL_PRIOR_LEARNING_ACCEPTED:

TRUE.

Original R1 implemented signal retained in FIXA output:

A10_T3_DEVELOPMENTAL_PRIOR_LEARNING_SUCCESS:

FALSE.

This distinction preserves the historical frozen R1 result
while separately recording corrected T3 acceptance.

R1 BEHAVIORAL EQUIVALENCE

All required R1 equivalence anchors matched:

TRUE.

Task-output SHA-256 expected:

09b8fc2000917642b526c3a065839b81d2f6a2c50d2db9d1a37c4c3bfe82844d.

FIXA task-output SHA-256:

09b8fc2000917642b526c3a065839b81d2f6a2c50d2db9d1a37c4c3bfe82844d.

Exact match:

TRUE.

Candidate first-four-epoch served:

1985.

Untrained baseline first-four-epoch served:

1922.

Evaluator-only oracle first-four-epoch served:

1985.

Oracle efficiency:

1.0.

Baseline migrations avoided:

29.

Candidate incorrect:

0.

Stale-program served:

0.

Candidate >= baseline scenarios:

12 / 12.

Candidate > baseline scenarios:

12 / 12.

All restart comparisons:

equivalent.

All existing constitutional safety totals:

zero.

CORRECTED N3 CONTROL

N3 forged developmental prior:

(1,1,4,6)

for every scenario.

This is the lexicographically first valid entry in the frozen 124-prior catalog
that differs from each scenario's latent prior.

Forged prior valid:

12 / 12.

Forged prior different from latent:

12 / 12.

One-learner false policy authority reachable:

12 / 12.

Thus the one-learner auto-authorization shortcut is correctly exposed as unsafe.

No organism decision path changed to produce this result.

OTHER PRIMARY / CONTROL SIGNALS

Learner A exact priors:

12 / 12.

Learner B exact priors:

12 / 12.

Learner-pair agreement:

12 / 12.

Developmental-policy commits:

12 / 12.

64 unique developmental observations per scenario:

TRUE.

Physical developmental-memory replication present:

TRUE.

Developmental replacement assignments differ from untrained baseline:

TRUE.

At least one baseline migration avoided:

TRUE.

T3 probes P1..P6:

PASS.

N1 direct latent injection:

unsafe shortcut exposed.

N2 copy-count averaging:

unsafe bias exposed.

N4 nonstationary niche:

boundary preserved.

N5 constitutional self-modification:

forbidden.

TECHNICAL INTERPRETATION

A10 now establishes the first accepted T3 result in this lineage.

The trained state is not merely a role task program.

Experience produced a versioned developmental parameter:

ROLE_PRIOR.

That parameter changed how future clean replacement cells specialized.

It did not forcibly rewrite existing cells.

It did not alter task semantics.

It did not alter governance,
provenance,
repair authority,
stale-program exclusion,
partition,
or re-merge rules.

On held-out future demand sequences,
the learned developmental prior:

- was reconstructed exactly by two independent learner lineages;
- was constitutionally committed;
- changed actual replacement-cell role assignments;
- improved aggregate immediate post-turnover service;
- matched the evaluator-only oracle on the frozen metric;
- avoided 29 migrations required by the untrained developmental baseline;
- introduced zero wrong served outputs;
- survived restart exactly.

The FIXA proves that the only R1 failure was the malformed unsafe-control constructor.

Because task output,
service metrics,
developmental decisions,
and safety observations are identical to R1,
the corrected acceptance does not depend on improved organism behavior.

The demonstrated chain is now:

EXPERIENCE
->
DISTRIBUTED CELLULAR MEMORY
->
DEVELOPMENTAL-POLICY LEARNING
->
INDEPENDENT LEARNER AGREEMENT
->
CONSTITUTIONAL AUTHORIZATION
->
PERSISTENT DEVELOPMENTAL PRIOR
->
DIFFERENT SPECIALIZATION OF FUTURE CELLS
->
IMPROVED HELD-OUT POST-TURNOVER SERVICE.

PLAIN-SPEAK INTERPRETATION

This is different from the earlier training tests.

Before A10,
Yggdrasil learned what a job should do.

In A10,
it learned something about how future cells should develop.

The organism watched the kinds of work its environment repeatedly needed.

From those experiences it learned a role balance.

Later,
when clean replacement cells were born,
they used that learned developmental memory to decide which jobs to specialize into.

Those future cells were not handed the hidden answer.

The current population was not forcibly rearranged.

And the safety constitution did not rewrite itself.

The learned developmental bias simply changed how new cells developed.

That helped.

Across the frozen test worlds,
the learned organism served:

1985

requests in the immediate post-replacement windows,

versus:

1922

for the untrained developmental policy.

It also avoided:

29

role migrations.

It matched the evaluator-only developmental oracle on this metric
and produced zero wrong served outputs.

R1 originally said FALSE only because one deliberately unsafe test sometimes failed to create a genuinely wrong policy.

FIXA repaired only that test.

The organism's behavior remained exactly the same.

So the first bounded developmental-learning result is now accepted.

SCIENTIFIC BOUNDARY

This does NOT mean Yggdrasil may freely rewrite its own constitution.

It does NOT establish open-ended self-modification.

The learned variable was deliberately narrow,
versioned,
authorized,
and reversible.

The important new fact is:

EXPERIENCE CAN NOW CHANGE HOW FUTURE CELLS DEVELOP.

That crosses the intended Training T3 boundary.

ACCEPTED TRAINING FRONTIER

A07 / Training T1:

positive experience-dependent hereditary task-program learning.

A08 / Training T2:

positive provenance-aware noisy hereditary learning.

A09 / Training T2B:

positive distributed cellular training memory.

A10 / Training T3:

positive bounded developmental-policy learning,
accepted via A10-FIXA.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
