# NKR-23 and NKR-24 — source-conditioned decision diagnostics

These two studies continued after NKR20/21 negative learning results and
NKR22's missing-action-support result. They do not rerun those primaries.
Source equations were publicly inspected before this preregistration;
this is explicitly exploratory/source-conditioned, not blind source science.

## Why extra history failed in this fixed source model

The original public MDPSCM reward/transition source was verified at exact
Git blob6264ec5450754c009e98c3e85f6d5927ece0a9ab. A restricted Boolean AST
interpreter and independent direct equations agree on all32 state/action/
latent assignments. No original code, RNG, environment constructor, reset
or do action was executed.

| Public state | Action | Nominal reward-one probability | Next-state-one probability |
|---:|---:|---:|---:|
| 0 | 0 | 0.82 | 0.82 |
| 0 | 1 | 0.18 | 0.18 |
| 1 | 0 | 0.18 | 0.18 |
| 1 | 1 | 0.82 | 0.18 |

Under the source's nominal iid latent model, current state/action are
sufficient for these conditional probabilities. Prior public reward adds
no population conditional information. That explains why increasing the
history bins can add sparse-sample error rather than better understanding.
This is evaluator-derived knowledge of the published source, not a relation
newly discovered by the native model.

## Do already-learned native counts imply useful decisions?

Every reconstructed native checkpoint MUST equal its previously sealed NKR19
checkpoint. Thus source-derived oracle equations cannot change native training.
An independent same-information Beta fit makes identical action choices.
Seven-step reward expectations below are calculated from the source model,
not measured by executing new policies. Common initial state is uniform.

| Public observations/world | Native optimal choices /8 | Native expected reward/step | Mechanical policy | Source oracle ceiling |
|---|---:|---:|---:|---:|
| 8 | 7 | 0.740000000 | 0.545714286 | 0.820000000 |
| 16 | 8 | 0.820000000 | 0.545714286 | 0.820000000 |
| 24 | 8 | 0.820000000 | 0.545714286 | 0.820000000 |

THEORETICAL_DECISION_VALUE_SUPPORTED

All always0/always1 values, actual historical prefix-start-state expectations,
full action maps and exact fractions are preserved in NKR24/result.json.
The source oracle is an unfair knowledge upper bound, not an equally informed
learner. Strongest equally informed conventional gain is ZERO.

NKR22 data-only bounds are unchanged: they deliberately omit these added
source-equation assumptions and concern realized missing rewards. A known
model can calculate expectations without providing empirical validation of
new policy execution, real-world source truth or unfamiliar mechanisms.

## Qualification and boundaries

Public source Git SHA:c94e9a4cd3641588b6b8507e71ccee5c27032bdf.
Original source license:Apache-2.0. Original source snapshot is included only
as nonexecuted attributed reference text. The actual nominal probability
model is a mathematical interpretation of source decimal probabilities,
not a test of NumPy's PRNG implementation or new physical observations.

Native modules/weights/acceptance were not changed; new source actions0.
scientific_pass=false; no owner runtime, merge, controller, schedule or paid API.
Ubuntu audit:0.015345s; Windows:0.188000s.
Source SHA:003b73eddd6b49dd21fffba266c9c91ea6726d70
Stable receipt:276c219f5c2f04442b104e955e10a10ee81fc81c71387dc1deb377a0c09e264a
Final whole-root/NKR05 and independent G29 both-OS qualification is pending
at evidence commit time; terminal PR receipt supplies the final source status.
