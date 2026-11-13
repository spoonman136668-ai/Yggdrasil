# WSP-60: Counterexample-driven causal identification and grounded planning

## Frozen before source/model/outcomes
- Preregistration: `1c2fc386ad6f15296aed00a8d49b63addf35a03c` (`prereg.json`). Parent exact source WSP59 PR #950 at `6c4a5992bd796c1b71889a57bb39a85a8c6e3633`.
- WSP59 prior negative is retained: 19/256 planning successes and 10 incorrect confident transitions despite 256/256 taught conjunction mappings. The initial pairwise-coverage probe states confound which of the two flags causes action outcomes, and selecting only the simplest consistent explanation was unsafe.
- WSP60 creates **12 disjoint seeds 2601–2612** using the same frozen synthetic source distribution; only evaluator code imports WSP59 `source.py` via an isolated module. Learner never imports source.

## Prospective causal intervention
- Two agents receive the same 40 initial charged physical observations (10 source-blind pairwise-covering states for each of 4 channels), and nine fully taught nonce byte-goal meanings.
- Unlike WSP59, the `IdentifyingAgent` preserves **all** fully covered and evidence-consistent cause-parent subsets of size at most 2. It predicts only if those alternatives agree; when they disagree it abstains.
- **PRIMARY checkpoint:** select one more charged state/action per channel, four additional interactions for **44 total**; active selection maximizes competing-model prediction divergence, while a seeded random baseline selects unqueried states. Both use exactly the same learned rules, planner and demonstrations.
- **SECONDARY only:** one further charged probe per channel, 48 total. This cannot rescue a missed primary result.
- Both agents must plan 32 heldout, source-achievable, 2–4-step two-goal instructions per world using causal table predictions, grounded taught nonce phrases and BFS. 384 primary tasks total.
- Audits include all 80 simulator state/action combinations per world, action-ledger hashes, exact cold restoration (including the new all-hypothesis behavior), snapshot tamper controls, model-candidate counts, numeric table entries, planning and wall/CPU cost.
- Old WSP59 minimum-parent learner is evaluated with the **same 44 active-source observations** using an extended WSP60-only budget wrapper. Exact lookup and deliberately wrong instruction grounding are further ablations.

## Frozen exploratory threshold
Signal only if active ≥250/384 physical goal successes (≥65%), exceeds random by ≥47/384 (≥12 percentage points), predicts **no** incorrect confident physical transitions across 960 state/action checks, exactly grounds all 384 composed instructions, and cold restoration reproduces predictions and plans in all 12 worlds.

If a criterion is missed, retain `SELFTEST_NEGATIVE_OR_INCONCLUSIVE` without changing the threshold. A passing exploratory result would show reliable identification of confounded causal dependencies in this **finite, strongly prior-aligned source family**, not general intelligence, free-form language, unrestricted physical-law discovery, independent neural/symbolic superiority, or full training-cost superiority.

## Qualification and boundaries
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-60 -p 'test_*.py' -v
```

Only existing Linux/Windows GitHub CI and full inherited regression with exact-source G29 atlas. No DEV/PRIMARY first-use, autonomous owner-loop integration, new controller/runner, schedule, paid API, scientific promotion, merge or deployment. The simulator permits arbitrary-state intervention resets without charging their real-world cost.
