# CKAD31 — Source-identifiability guard for native sparse causal forecasts

**Status:** Preregistered research-only experiment. No accepted model edits, autonomous owner actions, merge or deployment. Primary B is reserved.

The prior CKAD30 experiment (#1243) demonstrated that making more sparse native predictions can worsen held-out Brier despite retaining the learned source. CKAD31 tests whether a conventional **GF(2) degree-2 source-span certificate**, used *only to permit or reject* an already-trained native readout, prevents unsupported confident predictions on fresh synthetic two-interaction worlds.

The guard is not native causal reasoning and no scientific superiority is claimed: it depends on a conventional declared polynomial class, so an independently fitted conventional GF(2) arm is an essential control. The exact full 2,880-rule Bayesian control remains. All arms receive identical public interventions. No hidden rule ID or held consequence enters training.

## Frozen protocol and stop

The committed `prereg.json` (commit `837d728bde20a6b898a73b2f88ad4786785622cf`) precedes the source. Candidate uses the existing `NativeCumulativeLearner` and original `repair_sparse`, untouched. New independent pilot seeds are `9311,9322`, with 16 revealed source interventions for each of nine slots, six interference slots, full cold/retention/quarantine, and 48 held composite cases per arm per seed. Primary seeds `1311,1322,1333` are prohibited until an independently audited pilot certificate.

**SCREEN_GO** requires both pilots pass controls and at least one pilot beats both ungated sparse and unmodified native Brier by at least **0.02** with >=10% guarded primitive held coverage; otherwise stop and preserve **SCREEN_NO_GO**. No tuning based on pilot held data, no primary reruns and no protected first-use.

## Provenance

Source lock will pin this experiment's code blob before any execution; the world generator uses a new SHA-derived seed namespace. Pilot result JSON, source hashes, qualification receipts and negative outcomes belong in this Git branch and draft PR, not chat attachments. An accepted `main` update, owner integration, or FORGE dispatch is not permitted by the contributor experiment.

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-31 -p 'test_ckad31.py' -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-31/campaign.py --mode preflight
```
