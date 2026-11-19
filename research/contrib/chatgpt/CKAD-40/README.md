# CKAD40 — Native causal-memory identifiability diagnostic (DEV only)

**Research hypothesis only.** Baseline: CKAD39 draft PR #1286 at `feef03a15ec68a8e3da073e9d78d197acf656ea8`, whose two-seed retrieval screen was `DEV_NO_GO`. This branch does **not** retune, rerun, or change the previous experiment. The new preregistration was committed **before code** at `d38ba4e7c438b0a2eb89bf08cd5f54e6ff0fe2e3`.

## What is being tested

Before another mechanism is proposed, diagnose three separate necessary conditions:

1. **Archive coverage:** Have genuinely observed, source-trained historical native blocks from **both** old regime A and changed regime B become available by forecast time? Only already complete blocks with `>=8` authentic source episodes can count; the live/novel learner and blocks overlapping the latest 16-event evidence window are excluded.
2. **Observed-evidence identifiability:** With both sources present, does an evaluator-only grouping of the learned archive show that the 16 **previous** observed action/consequence tuples distinguish A from B by their independent predictive likelihood? Private phase labels are used only to group previously trained source blocks and evaluate accuracy, **never** sent to the native learner, used as live observations, or turned into a deployable predictor.
3. **Representation ceiling:** Given the correct regime *from the evaluator*, are the correct source-block predictions themselves better than the original native stream and the strongest actually fitted conventional Beta/Hedge controls? This is a privileged upper-bound diagnostic, **not** proof the learner can discover or recognize a regime itself.

Native `NativeEpisodeExperience` is still the **single persistent source-trained learner**. Training occurs only after genuine observed actions, transitions and terminal consequences, and no checkpoint schema or accepted model changes. The unit tests include phase-label isolation, in-sample evidence leakage prevention, source/read purity, stop rules and forbidden first-use seeds.

## Frozen development budget and stop

Two fresh CKAD40 DEV seeds `40811` and `40812`, 2 worlds per seed, same original synthetic A→B→A structural families, identical independent action policy and source observations for native and conventional controls. CKAD39/38 seed cohorts are forbidden to rerun. CKAD40 reserved holdouts `41811,41812,42811,42812,42813` are never accessed.

Check both seeds (no averaging a failure away): at least 64 evaluable late B/return episodes, at least 50% late-phase eligible coverage, at least 65% classification accuracy on previous witnessed evidence, and evaluator-only archive oracle Brier gains of 0.015 against **both** original native stream and strongest conventional control.

Decision is first failing necessary condition: `ARCHIVE_COVERAGE_GAP`, `IDENTIFICATION_GAP`, `REPRESENTATION_GAP`, or `DIAGNOSTIC_POTENTIAL`. Any decision remains **scientific PASS=false**, because label-grouped archives and phase-aware oracle are not available to a native autonomous learner. This one-shot screen must not be tuned after outcomes.

## Reproduce development-only audit

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-40 -p 'test_ckad40.py' -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-40/diagnostic.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-40/screen_dev.py
```

CI runs the exact source on Linux and Windows. DEV diagnostic CI success cannot justify native scientific first-use, full qualification, merge, accepted ref, Forge/Yggdrasil research-loop changes, deployments, paid APIs, or scheduled tasks. No new owner or scheduler is created. Negative evidence must be committed to GitHub along with exact SHA and run IDs.
