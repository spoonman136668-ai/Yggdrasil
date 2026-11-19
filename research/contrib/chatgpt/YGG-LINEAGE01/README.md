# YGG-LINEAGE01 — canonical native checkpoint custody (read-only)

## Why this gate exists
CAP01–CAP03 continued real native and JEPA learned weights across isolated draft research branches. CAP03 reached 1,118 and 1,093 cumulative witnessed episodes, passed 466/466 full regression on both operating systems, but failed frozen controls. None of these engineering results implies that the **official Yggdrasil owner** accepts, loads, or advances this same native checkpoint.

A live autonomy workflow can run successfully without advancing research. Distinguish code, learned model, owner checkpoint, and science before launching more cumulative training. This report is a source-bound Git snapshot, not a host inspection.

## Pinned facts and limitations
- Accepted `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Its sole tracked `yggdrasil/` Python native module is `public_causal_cells.py` (Git blob `5c9a9904e31688bebc2e53723569e1fb988a981f`), whose constructor initializes zero native counts and whose 164-byte snapshot is an explicit-memory control. No model weights/checkpoint in the inspected accepted main repository tree are established as the canonical *continually trained* state. **This does not assert no weights exist on an external owner host or in private storage.**
- Official `main` `.research-autonomy/config.json` says enabled `true`, authority `research-only`, active branch `research/autonomy-yggdrasil-active`, CKB governance-only. **Reading this configuration is not a license to change/execute its controller.**
- Pinned active research branch `92c421a5475a27015a390efb88c373eb5f15379d`, state Git blob `27194d56d16fb318c5118fd2b1119695876256d6` reports last accepted cycle `2026-10-16T18:05:00.0902965Z`, classification `preregistered-blocked`, `scientific_claim=false`, experiment suffix `096`. The newer November 19, 2026 launcher [#44522000519](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44522000519) completed SUCCESS but its next-cycle dispatch step was SKIPPED. **Launcher success ≠ learned-state continuity.**
- [CAP03 draft PR #1318](https://github.com/spoonman136668-ai/Yggdrasil/pull/1318), exact evidence candidate `a594a6c5273345687544ddc31e698498bda41d2c`, independent synthetic development `NO_GO`, 466/466 full dual-OS engineering qualification. It is a model research proposal, **not** an accepted canonical checkpoint.
- Other research owners, private machine disks, GPU runner state, acceptance custody, process restarts, and locally held private checkpoints are **UNVERIFIED** from this read-only Git audit.

## Exact reproduction
```bash
git fetch --no-tags origin 92c421a5475a27015a390efb88c373eb5f15379d
git fetch --no-tags origin a594a6c5273345687544ddc31e698498bda41d2c
python -B research/contrib/chatgpt/YGG-LINEAGE01/audit.py --output /tmp/ygg-lineage01.json
python -B -m unittest discover -s research/contrib/chatgpt/YGG-LINEAGE01 -p 'test_*.py' -v
```

The audit reads three exact Git commits and does not execute experiments or mutate state. GitHub Actions verifies both supported OS. The generated JSON declares missing custody as **UNVERIFIED**, not PASS.

## Next owner-qualified research interface

Before additional first-use:
1. Read verified owner-native canonical checkpoint identity, source manifest, learned-state SHA, chronological witnessed ledger, original train/validation split and runner.
2. Verify historical cold retention and training resume on **that** checkpoint, not a separately initialized learner. Preserve source bytes, seeds, owners, action budgets and existing model's tokenless architecture.
3. Freeze one genuinely unfamiliar operator dataset and matched exact symbolic/fully trained conventional/action-cost controls before first use; prohibit tuning on prior CAP03/CKAD scored cohorts. Require predefined gains and independent Linux/Windows qualification.
4. Request specific authority only for owner acceptance/deployment or protected first use if the verified contract requires it. Never treat ChatGPT WebUI, GitHub Actions success, or historical standing scope as universal owner authority.

**Status:** source audit only; engineering pending until CI; scientific gain unproven; accepted main/runner unchanged; no merge, promotion, schedule change, paid API, or deployment.
