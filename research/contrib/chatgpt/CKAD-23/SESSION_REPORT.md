# CKAD23 — Unsignaled causal context detection in one cumulative learner

**DEVELOPMENT_GO** — frozen synthetic development only.
No native model promotion, no automatic Forge/Yggdrasil loop admission.

This experiment began with the exact three qualified CKAD22 native
checkpoints at 448 retained public episodes each. The source changed its
causal rule at episode counts 48,96,144; the learner was not told when.
Every chosen first intervention preceded the observed next state; every
second intervention preceded the revealed terminal consequence.

The detector used S=max(1,S/(4*p)) from exact prequential joint evidence
and triggered a new context at S>=16 after >=8 retained local episodes.
All source receipts remain append-only in one cumulative native model;
only contextual readout/hypothesis selection was reset.

An independent conventional replay of the same mixture, actions and
context change detector matched native readouts and boundary receipts.
A fully trained trailing64 MLE used the exact same public action receipts.
Random acquisition was equal-budget but chose its own interventions.

| Held count | Detector /288 | No-reset /288 | Periodic32 /288 | Trailing64 MLE /288 |
|---:|---:|---:|---:|---:|
| 64 | 221 | 80 | 142 | 145 |
| 112 | 216 | 225 | 229 | 250 |
| 160 | 241 | 163 | 237 | 208 |
| 192 | 235 | 202 | 235 | 234 |

## Frozen development gates

- gain_vs_no_reset: PASS
- at_least_periodic32: PASS
- at_least_trailing64_mle: PASS
- returning_invariant_reward: PASS
- per_seed_false_alarms: PASS

## Unsignaled detections by seed

- Seed 101: stream-relative inferred counts [50, 71, 86, 151]; false alarms 2; final checkpoint 6cf3bac82207adb581d71efd324d0506ecc75cabd024d74336f693177e7cf790.
- Seed 202: stream-relative inferred counts [31, 51, 59, 91, 146]; false alarms 2; final checkpoint 3b7817ec701c683a72319a1287e670621a81f12252fc24691afece75297f7a6c.
- Seed 303: stream-relative inferred counts [52, 146]; false alarms 0; final checkpoint bc139dde9e595ddc8f30b0f33e6e51b8816ee0095a4273d220164b6916617c16.

Limitations: synthetic source family; three model seed groups; change points
and frozen success gates were predefined; matching conventional policy is a
necessary parity test, not proof of superiority over it. No protected
scientific first-use was consumed. Every failed threshold is preserved.

Final result stable SHA256: c80646b4370d8433aa859ed6d9b7e44fea8a274ce2ebd6ed88102d1a8f7d4a67

**ENGINEERING:** subject to mandatory full final regression on atlas-sealed SHA.
**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**
