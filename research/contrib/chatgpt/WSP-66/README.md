# WSP-66 — Falsifying active-exploration advantage using matched 48-charge trajectories

## Prospective source and criteria frozen before code/outcomes
- Initial prospective commit: `bc07caa5397e209fd07502b7e71374b23f7a982b` (`prereg.json`). No WSP66 world, policy or code existed before this freeze.
- Parent WSP65 [PR #956](https://github.com/spoonman136668-ai/Yggdrasil/pull/956) at exact source `5fc18268bb75c3ef1b457ab84041f25ea23bd4b7`. WSP65 showed **600/768** history-conditioned accurate predictions, zero wrong-confident, against **749/768 for equal-charge random exploration** at *128* physical observations. That negative **exploration-policy comparison** remains intact; prior SELFTEST_SIGNAL was for hidden-memory vs visible and short-suffix controls.

## Why this experiment is not a repetition of WSP65
- The original WSP65 policy was biased toward current-state/action novelty and often **missed latent mode-transition evidence**. WSP66 evaluates a *different* source-blind, precommitted ordered-action-pair design against random exploration, with **less than half** the prior training actions.
- Fixed **order-two de Bruijn 16-channel-pair cyclic sequence** for 4 public actions, repeated three times: 48 charged actions and every ordered action pair represented across adjacent physical interventions. The source never supplies hidden role or mode information. This is **structured design** and *not* genuine outcome-adaptive curiosity or feedback-driven model uncertainty maximization.
- Random control uses an independently SHA256-seeded uniform action selection policy and exactly 48 actions. Frozen WSP65 active policy also runs on its own equal-budget trajectory as diagnostic.
- **All three arms reuse EXACTLY the original WSP65 `HiddenParityWriter` without modifications**. The only intervention is action selection, so any difference in model performance reflects the training data acquired, not a new numerical hypothesis family.

## Worlds, charged action custody and heldout tests
- 16 independently newly seeded SELFTEST worlds 3201–3216, **eight** with three observed bits and **eight** with four. The evaluator-only WSP66 source has its own salt and produces randomly permuted action channels and sensor roles. True mechanics, however, remain within the **same strongly prewired WSP65 one-hidden-parity-bit source family**; this is not independent physics-class transfer.
- Every arm begins visible all-zero and latent mode zero, then executes 48 consecutive physically valid charged actions through a stateful evaluator session, no training resets, teleports or arbitrary-state physical queries.
- Evaluate **64 fresh independently generated 8–16-step public action/consequence histories per world**, 1024 final mode-sensitive next-step predictions. The physical test episodes reset to known zero only at evaluation start; **all three models and all other controls see exactly the same public context** and queried action ID. These context observations are NOT fed back into persistent model training. Report all context action steps/costs separately.
- Audit correct/abstain/wrong confident for balanced, random, original WSP65, independent empirical latent-mode automaton, visible-state lookup, two-action-suffix lookup and history-scramble diagnostic. Never hide a stronger baseline.

## Frozen criterion
- Balanced model must correctly and confidently predict **at least 650/1024** heldout consequences.
- It must exceed the **random 48-action** model by **at least 96/1024**, a 9.375 percentage-point gain, using exactly the same WSP65 learning mechanism and same test episodes.
- It must make **zero** wrong-confident predictions; exhibit actual repeated-visible-state/action contradictory outcomes in >=12/16 source worlds; achieve all 16 unique adjacent ordered action pairs within 48 physical actions in every world; and pass cold snapshot, restore and tamper controls for all 16 worlds.
- **Measured whole process CPU** (action selection + charged source transitions + learner observation/fitting + heldout inference) must be **at most twice** that of random with the same relevant work. Shared evaluator test construction, cold-restore controls and the independent controls are reported separately. If any criterion misses, retain `SELFTEST_NEGATIVE_OR_INCONCLUSIVE` without thresholds changing after outcomes.

## What a result can and cannot mean
This tests whether *structured experiment design* improves learning of a **source-family-aligned single hidden parity bit**, not general representation discovery, human language, unknown-world rule learning, self-directed general intelligence, or whole-stack neural-model training replacement. It is a fresh prospective **SELFTEST** (never DEV or PRIMARY scientific first-use). There is no independently trained neural belief-state baseline or independent scientific acceptance. Even a positive SELFTEST is not `SCIENTIFIC_PASS`.

## Reproduce and separate qualifications
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-66 -p 'test_*.py' -v
```

Focused Ubuntu/Windows, generated-only exact-source G29 companion, and the full inherited two-platform regression must qualify final candidate SHA before ENGINEERING_PASS. No merge, deployment, scheduling, paid APIs, controller changes, new runners or official owner-loop integration.
