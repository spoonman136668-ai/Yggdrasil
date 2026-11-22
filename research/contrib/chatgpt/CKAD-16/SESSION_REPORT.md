# CKAD16 — second public source in one cumulative native checkpoint

CUMULATIVE_SECOND_SOURCE_DEVELOPMENT_SUPPORTED

Continues the trained CKAD15 state. Each new DTR training batch executes in a
FRESH Python process, restores the preceding full state, applies a new public
training prefix and saves the successor. All prior deterministic weights,
property facts and MDP probability state are byte-exact and retain their readouts.
One unchanged PublicCausalCells bank estimates the first-stage state transition
and terminal outcome at separate addresses with the correct public history.
Immediate zero reward is never substituted for the full delayed consequence.

| Training episodes/replica | Pooled episodes | Transition Brier | Terminal Brier | Pooled Brier | CART pooled |
|---|---:|---:|---:|---:|---:|
| 0 | 0 | 0.250000000000 | 0.250000000000 | 0.250000000000 | 0.250000000000 |
| 64 | 192 | 0.243937300611 | 0.005443688586 | 0.124690494599 | 0.121894464435 |
| 128 | 384 | 0.247733341821 | 0.001526912774 | 0.124630127298 | 0.123849910095 |
| 192 | 576 | 0.246586898188 | 0.000701464836 | 0.123644181512 | 0.123279672315 |

Frozen gates: {'exact_beta': True, 'fresh_process_continuation': True, 'no_held_training': True, 'probability_learning': True, 'retention': True}
The exact fully fitted Beta control matches every probability. Fully grown CART
fits each observed public conditional empirical mean and receives the same inputs.
No superiority over the strongest conventional learner is claimed.
The old DTR02 PUBLIC_DTR02_NO_GAIN result remains preserved; its policy reward
rates do not measure this forecast experiment and are not substituted as scores.

Original archive authenticity: GitHub run39932201242/artifact12492506361, ZIP SHA256
ada547777ba2ba49070fe2606ac99c8d9248532f1cb16c8a0f8eab0f4001508c.
The768 public FIT episodes were previously consumed. This new retrospective
split trains on576 and holds192 complete episodes for384 forecasts per stage.
It is NOT a blind unfamiliar-family or virgin-source study. The compact state
stores only TRAIN records; held outcomes, seeds and replica IDs are not inputs.
No original environment import/reset/do, new intervention, policy rollout,
private U/info, source oracle, accepted-ref or source-owner mutation occurred.
Future causal policy value and independent fresh-world learning remain unproven.

Whole campaign Linux 23.119560s / Windows 26.954000s.
Linux parent CPU 9.544678s plus measured child CPU 12.514295s.
Source authoring, setup, sealing, CI scheduling and final qualification are additional.
No2x speedup, native novelty over Bayes, broad intelligence or deployment claim.
Source SHA: af4dfa03734f794feb86dfeb8cf8b4c757626e57
Stable result SHA256: d05168f528c87a681fc4c1c22a3d7da93a3a6c9d8eab4421543968b3985154e9
Reproduce: `python -B research/contrib/chatgpt/CKAD-16/campaign.py --output-directory /tmp/ckad16`.
Independent audit: `python -B research/contrib/chatgpt/CKAD-16/independent_audit.py`.
Mandatory full final Linux/Windows regression and independent raw/G29 qualification
follow sealing. SCIENTIFIC_PASS=false. DEPLOYMENT NONE. DRAFT/UNMERGED.
