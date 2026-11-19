# CKAD21 evidence-driven context retrieval

**DEVELOPMENT_NO_GO**

The three complete CKAD20 models continue through six public sessions. Each
session receives sixteen probe episodes before held scoring. The model
reconstructs native candidate forecasts from contiguous witnessed experience
blocks and updates a persistent belief with actual public transition and
terminal outcomes. It conditions the second action on the first revealed
transition. Every subsequent session continues the retained full checkpoint.

Development metrics are exact rational values in result.json.
Frozen development gates are {'returning_reward': True, 'returning_vs_mle': True, 'returning_vs_pooled': False, 'shifted_reward': True}. The independent matched mixture has the
same evidence, candidate structures and action opportunities. Its exact
probabilities and actions must tie. The full-history Beta and fixed trailing64
MLE controls consume the active learner's actual probe outcomes.

The new probe permission differs from CKAD20's zero-adaptation held trial.
All CKAD20 negative results remain recorded. Scientific pass is false and
deployment status is NONE.

Source bd73af2ea954208bff647dd7e1f7f6a7bfa39415.
Stable Linux/Windows result c986dd9dc63ace08f4a0185f80258099971e22ff50884cf6a7ec58e9b1ad650e.
Linux campaign 191.899375s.
Windows campaign 183.656000s.
Setup, final regression, audits and authoring are additional costs.

Reproduce with python -B research/contrib/chatgpt/CKAD-21/campaign.py
--output-directory /tmp/ckad21.

Audit with python -B research/contrib/chatgpt/CKAD-21/independent_audit.py.
