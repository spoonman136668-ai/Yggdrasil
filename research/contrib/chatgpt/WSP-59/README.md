# WSP-59: Cold-start unfamiliar world, grounded instruction, causal planning

## Frozen before implementation
Prospective protocol: `b2649394ab24e1d588aa96423821057ff5640990` (`prereg.json`). Based on WSP58 PR #949 SHA `6df0917e97fe22255153ae7af00d98fecc7c605a`, without changing its experiments. This PR is an **isolated SELFTEST**; scientific admission is not authorized.

## What is genuinely new here
- The learner receives an unfamiliar world of 20 observable states, four randomly relabeled action channels and hidden nonlinear/conditional state transitions. Hidden causal action roles and true operator maps exist **only** in evaluator-only `source.py`.
- It receives 40 charged state-action-outcome interventions per world (10 per action channel), then writes its own numerical factored causal tables. It never imports source or uses a gradient optimizer or an autoregressive objective.
- It receives nine labeled grounding demonstrations for primitive byte-encoded task phrases. All 32 heldout tasks/world combine **two** of those predicates in a new instruction via a known ` & ` byte-interface contract, requiring 2–4 correct actions from unfamiliar starting states.
- The same learned rules must support shortest-first planning (maximum four actions) and survive cold snapshot/restore without additional observations.
- Eight worlds with newly sampled source physics (seeds 2501–2508): 256 heldout tasks, 640 possible source physical transitions for independent candidate checking.

## Architecture and controls
- **Causal-coverage agent** chooses a 10-state pairwise-covering design per action channel independent of hidden source outcomes. This is **source-blind structured intervention design, not feedback-adaptive curiosity**.
- **Seeded random agent:** same 40 interventions, identical nine demonstrations, identical causal learner and planner; only probed states differ.
- **Exact observation lookup:** the causal agent's same 40 observations and same planner, but cannot infer unobserved state-action consequences.
- **Shuffled symbol grounding:** same 40 physical observations and same planner, but teaching pairs deliberately map each nonce phrase to the wrong grounded predicate.
- The generic causal prior **assumes every next-state register depends on at most two current-state registers**; this matches the source generator and gives a powerful structural advantage. It does not infer the number or domain of registers, an unrestricted causal graph, or natural-language semantics.
- Any state can be selected for a charged query, so state resetting/intervention positioning is **free** in this simulator. Real-world action and reset costs are not represented. Strong neural and independent symbolic matched-compute baselines remain unexecuted.

## Frozen success/failure criterion
At least 65% of 256 heldout tasks solved by causal-coverage agent, at least 15 percentage points ahead of random probing on exactly those tasks, **zero** wrong-confident transition predictions across all 8×80 table queries, 100% exact grounded conjunction decoding and cold restore parity. Otherwise retain `SELFTEST_NEGATIVE_OR_INCONCLUSIVE` without tuning the frozen test.

Even if positive, this is evidence for *coupling* numerical rule learning, taught symbol composition, bounded planning and cold memory **inside a small synthetic family**. It is **not** evidence of AGI, open-language learning, fully general unseen law induction, continual multi-domain understanding, or full-system cost advantage.

## Reproduction and custody
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-59 -p 'test_*.py' -v
```

Focused Linux and Windows, full inherited WSP regression and exact-source G29 source atlas are separate engineering checks. No DEV/PRIMARY first-use, merge, promotion, deployment, scheduled task, model-in-the-loop integration or paid API.
