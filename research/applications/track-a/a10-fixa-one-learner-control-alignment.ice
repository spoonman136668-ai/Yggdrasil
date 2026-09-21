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
