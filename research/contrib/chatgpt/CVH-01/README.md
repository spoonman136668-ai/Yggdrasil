# CVH-01 — Tokenless public successor-return memory (source-safe)

**Status: LOCAL ENGINEERING CAPABILITY PASS (11/11); SCIENTIFIC NO-GO/UNVERIFIED; NO NATIVE MODEL PROMOTION.**

This is the smallest complementary implementation after CB7's source-verified forensic finding that **98.6% of one-step greedy policy regret** came from premature STOP decisions. Its goal is not yet to replace a full-horizon planner. It establishes a bounded **four-observation action-to-earned-return memory**, with finite-horizon credit, context separation, and cold interruption recovery, using the exact six-field public consequence contract already qualified in [FKP-24](https://github.com/spoonman136668-ai/Yggdrasil/pull/1120) and with a pinned parent [FKP-25](https://github.com/spoonman136668-ai/Yggdrasil/pull/1122). No new source model, scheduler, controller, or acceptance pathway was created.

## Precise mechanism

The learner accepts only `(before:int, action:int, reward:int, after:int, terminated:bool, truncated:bool)` where all numeric fields are 0 or 1. A public context is `(previous observed action, previous observed reward, current before state, current action)`, with a distinct start-of-episode sentinel. The 36 possible keys store non-gradient **integer fixed-point** accumulated return units and observation counts. Each genuine observed reward is propagated backward to the last four not-yet-finalized public actions with discount weights **1, 1/2, 1/4, 1/8**. Records are completed only when four actual rewards have arrived or the episode terminates/truncates, never from predicted or source-private future labels. The last three unresolved action traces remain bounded in memory.

Unseen or under-supported action comparisons **abstain** (return `None`), not hallucinate. SHA-256 canonical snapshots include the learned numeric counters, pending traces, trace continuity and rolling digest of observed public records. Exact restoration mid-episode continues identically; corrupted and semantic-invalid canonical snapshots fail closed. This is **corruption detection**, not third-party attested evidence: a malicious actor who can rewrite state and recompute hashes is not defeated by this design.

The key algorithm does not import `causal_gym`, `native_public_mdp`, any original source world or private evaluator. A separately implemented conventional batch return-to-go estimator processes the exact same public tape and independently produces **identical numeric counters and summed returns**, including interrupted open traces and closed episodes. The intentionally weaker immediate-only table does not credit future reward to an earlier action.

## Verified results — fabricated public records only

- **10/10 local focused tests PASS**: correct two-step credit, predecessor-conditioned associations, terminal/truncation isolation, cold interrupt/resume identity, independent conventional parity, supported action choice and abstention, strict public-only validation with atomic rejection, tamper and validly rehashed semantic-forgery refusal, no imagined incomplete return and no upstream source interactions.
- Additional **700 reproducibly generated source-free public streams, 21,231 fabricated records**: the candidate's count and earned-return total after *every* observation exactly match the independently implemented conventional batch estimator. Each intermediate canonical cold checkpoint restores byte-for-byte. **1/1 stress test PASS**. Maximum observed serialized snapshot was **505 bytes**; this is neither full Python object heap nor whole-process memory footprint.
- The controlled **20-record / five-episode fixture** yields starting context with **2 action-0 observations**, learned return **0**, and **2 action-1 observations**, learned four-step discounted return **0.25**. Its delayed reward arrives at `t+2`; the immediate-only table records **0** for action 1, while the model selects action **1** with its minimum two-observation support rule. Independent exact batch table predicts **the same outcome**. Final closed snapshot **464 bytes**, SHA-256 `6947c3d8993721ff825f9e199862f16357815d2e7ab92cc2014a9794e3dc3298`.
- Local Python **3.13.5 Linux x86_64**, compile PASS; 11 tests PASS in **2.987 seconds** on the local research sandbox. All four newly tested Python source files match GitHub's exact Git blobs and local SHA-256 receipts in `provenance.json`. The test harness uses a **same-shaped lightweight FKP24 PublicConsequence definition**, not an execution of the full original FKP24 Python module. Previously qualified FKP25 source hashes are inherited as reference, **not** as newly executed acceptance on this candidate.

## Reproduce from a complete branch checkout

```bash
cd research/contrib/chatgpt/CVH-01
python -m compileall -q .
python -m unittest discover -p 'test_*.py' -v
```

**Boundaries:** These 21,231 input records are fabricated offline fixtures, **not** externally sourced action data. Original Causal-Gymnasium is never imported/constructed/reset/acted upon; no original native external MDP action, 996100 mechanical seed, DEV 996500 or TRANSFER 996600 cohort, protected science first-use, native activation, controller, runner or scheduled task was attempted. No coupled `policy.choose`/source `do` integration has been qualified. Neither persistent general knowledge discovery, unprovided operator invention, multi-episode long-horizon **planning**, unfamiliar source transfer, fully trained conventional sequence baseline superiority nor independently qualified whole-process efficiency has been demonstrated.

**Qualification:** Local exact-source engineering focused/stress PASS, but **mandatory complete final Ubuntu+Windows root regression and generated G29 on this new branch UNVERIFIED**. Parent FKP25 PR #1122 and separate WSP121 PR #1121 have their own passing exact-source two-OS gates, which do **not** transfer to these new source files. No accepted `main` change, PR, merge or deployment.

**Decision:** Keep the research branch isolated and its negative strong-control tie explicit. The next real scientific milestone belongs on independently authorized, original causal-action environments: learn **transition dynamics and conditional multistep decision value** that persist across unfamiliar worlds. Evaluate against independent full-horizon Bayes, fully trained neural and optimized symbolic controls at matched public action, compute and cold-retention budgets before any promotion to native Yggdrasil.
