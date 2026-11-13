# WSP-63 — Sparse physical rule extrapolation under charged no-reset actions

## Immutable preregistration
Frozen before new WSP63 source/model/tests: `cf6d1d8918ca01c527dfe713737b7e02463c1c7c` (`prereg.json`). Parent [WSP62 draft PR #953](https://github.com/spoonman136668-ai/Yggdrasil/pull/953) at `ace34717ddc3bf4110e4ae0cd895a071c94ae7ca`. WSP62's scientific SELFTEST negative remains: 351/384 goals, but only 11 correct unseen state-action predictions versus frozen required 25, with direct observation lookup nearly matching the candidate.

## Scientific question
Can an explicitly structured, compressed representation predict physical consequences that it **never encountered directly**, under a deliberately reduced 48-action budget? Is its confidence safe on an unknown rule *outside* the assumed basis?

## Frozen source and methods
- Four worlds each of chain, XOR/AND and **cubic three-input AND negative-control** sources, seeds 2901–2912 with an independent WSP63 SHA256 generator domain. The evaluator-only `source.py` holds unknown sensor and action roles, source dynamics, and oracle-constructed reachable goal tasks. Learners never import it.
- Each policy must execute **48 physically continuous charged actions from a fixed all-zero initial state**, with no training reset, teleport, arbitrary-state query, or withheld task feedback. Both arms must acquire experience in actual reachable states.
- Original unmodified WSP61 `ReachableCausalLearner.select_action` chooses the active trajectory. The **same exact active ledger** is passed to the new `CompressedEffectLearner`, WSP62's quadratic Boolean learner, WSP61's fixed three-parent learner and a direct observation-lookup control. The random policy executes its *own* 48 actions using the same compressed model.
- The new learner infers an action's affected sensor bit from nontrivial observed deltas. It writes a 7-dimensional degree<=2 Boolean trigger function of the **three other** bits via conservative GF(2) constraint elimination and abstains when a prediction cannot be established from that model and the evidence.
- This **single-bit action effect prior** and **quadratic trigger prior** deliberately match the eight source-family-aligned worlds. Cubic trigger physics in the other four worlds breaks the quadratic assumption, making confident unsafe extrapolation a meaningful negative result, not something to hide.

## Frozen criteria
- 8 in-family worlds ×32 goals = **256** heldout 2–6-action goal tasks. Exploratory success requires >=180 solved, >=20 more than exact same-ledger memory lookup, >=35 truly **unobserved** action/state predictions correct, **zero** confident wrong among all 8×64 physical transition audits.
- Additionally require **zero** confident wrong across the four *out-of-basis cubic* worlds' 4×64 transition audits, despite model mismatch, and exactly 48 chronological charged actions/arm and cold restore parity. If any condition misses: `SELFTEST_NEGATIVE_OR_INCONCLUSIVE`, no metric retuning.
- Diagnostic whole-12-world outcomes (384 goals) include frozen WSP61, WSP62 and random control scores, source receipts, exact-known vs truly unseen audited transitions, hypothesis ranks, numerical dimensions, snapshot bits and end-to-end CPU/wall.

## Strict limits
Even a positive criterion only tests a synthetic source-aligned structural prior. It does not establish unrestricted causal model invention, natural language, general intelligence, or superiority over independently trained neural and symbolic models under matched computation. Action budgets are matched, but model-selection compute may differ. Out-of-basis safety cannot be guaranteed from finite evidence alone.

## Reproduction
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-63 -p 'test_*.py' -v
```

Only SELFTEST, no DEV/PRIMARY scientific first-use. Focused Linux/Windows, exact-source G29, inherited final two-platform regression must qualify the exact source tree. No autonomous controller or research-loop changes, PR merge, deployment, production action, schedule, paid API or runner reconfiguration.
