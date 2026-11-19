# CKAD39 — Evidence-conditioned native causal-memory retrieval

**Status:** DEV candidate; no original pilot or reserved primary first-use, no scientific promotion. Forked from the CKAD38 draft exact source `0acaf48b6148f3241c3627a7f92c0db45009c543`. Preregistration was committed first at `d210f6d0259bb4dc27fe6a5155eeef0ffdcb776a`.

## Question

Can an existing single persistent native causal learner recover an earlier learned causal relationship after an unannounced structural change without erasing its cumulative source ledger?

CKAD38's posterior sharpening failed its two held development pilots, so this is a **different retrieval hypothesis**, not retuning those pilots. The research-only `readout.py` inspects native causal block memories fitted from **real previously witnessed synthetic events** and computes an archive-only likelihood over the **last 16 already witnessed events**. A retrieval influences the output only after the native stream contradiction detector fired within 48 events and one stored source has at least 0.55 normalized posterior mass. It makes a 50/50 blend of evidence-selected archive forecast and unchanged native stream forecast. Conditional terminal predictions update retrieval weights using the already observed transition, not a future outcome.

The implementation does **not** modify `yggdrasil/native_episode_experience.py`, checkpoint layout, source counters, source IDs, accepted training or original CKAD38 files. All observational and action budgets are identical. This is an opt-in read-only output of the **same** learner, not a second training architecture.

## Isolation, splits and stop conditions

The CKAD39 campaign reuses CKAD38's public synthetic A→B→A structural families as a separate **development** screen with disjoint seeds and new source IDs. It does **not** establish out-of-family transfer. Evaluator-only world identifiers, regime boundaries and future outcomes are never input to native or conventional predictors.

- DEV-only: `38911`, `38912`.
- Original CKAD39 pilots (not to be used before source freeze and independent preflight): `39181`, `39182`.
- Reserved, untouched primary: `49181`, `49182`, `49183`.
- Forbidden consumed CKAD37/38 pilots: `14071`, `14072`, `14181`, `14182`.

Predeclared screening criterion: on both original fresh pilot seeds, pooled late B+late A-return Brier at most 0.145 and absolute improvement at least 0.025 against both default native stream and the **strongest** fully trained conventional control, with no worsening in the early B/return phases; exact cold/source-integrity checks. A pilot GO would still be development feasibility, **not scientific proof**.

**Early stop:** if either DEV seed cannot meet the 0.025 improvement against both the baseline native stream and strongest conventional control, do not consume pilots. Do not tune a failing observed seed.

## Reproduction (development only)

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-39 -p test_ckad39.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-39/campaign.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-39/campaign.py --mode dev --seed 38911
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-39/campaign.py --mode dev --seed 38912
```

No `--mode pilot` is authorized or scientifically qualified on this unscreened branch. Pilot mode requires an absent `source_lock.json` to be created under a **separate later source-identity freeze** after two-platform DEV qualification; there is no lock or pilot evidence here.

Final exact-source full regression, independent source/control reconstruction, unfamiliar family transfer, accepted owner review and any scientific first-use remain separate requirements. GitHub workflow qualification does not constitute approval to modify Yggdrasil's accepted model, research loop, runners or deployment.
