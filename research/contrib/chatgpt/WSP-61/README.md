# WSP-61: no-reset reachable-state causal learning

## Prospective source custody
- Frozen before any new source/learner/observations: `7abb093ce94b75da5301cedc06b67aa634d32f0d` (`prereg.json`).
- Parent WSP60 PR #951, exact baseline `74796fa9d40a1723b725a1356777061d0fc69a1b`. Its 384/384 causal-planning repair and missed active superiority threshold remain unchanged.
- SELFTEST only: seeds 2701–2712, **12 independently sampled sources**, two distinct dynamics families: six conditionally gated toggle chains and six three-way XOR-gated mechanisms. Four permuted action roles and four hidden bit-role indices. This is a new deterministic binary sensor simulator, not a reuse of WSP59/WSP60 source.
- All source physics and oracle shortest-path enumeration live in evaluator-only `source.py`. The candidate `learner.py` does not import the evaluator, its hidden roles, or task construction.

## The methodological change
- **No training resets.** Each agent begins at a single all-zero state and gets exactly 80 charged, chronological action transitions. The next physical state follows from the action just taken; there is no arbitrary-state query or free teleport. The agent's `observe` explicitly rejects discontinuous histories.
- The active agent chooses only its *current-state* action from public evidence, prioritizing unmeasured state/action contexts, predicted novel states, and balanced coverage. The random agent selects a uniformly random channel from its *own* current state. Each policy receives the same action cap, not the same resulting states.
- Candidate causal explanation tables enumerate all 0–3 sensor-bit parent subsets, retaining partial tables from actual consequences. If any evidence-consistent candidate is ungrounded or disagrees at a queried state/action, the learner **abstains**. No gradient optimizer, pretrained neural model, token-based language model, source-derived operator function or hidden action mapping.
- The three-way XOR family deliberately creates **four-variable effect dependencies** (target bit plus three controls), which may be outside the candidate's bound of three parents. This is an explicit out-of-prior **negative challenge**, not an implementation error to fix after observing outcomes.

## Frozen evaluation
- 12 × 32 = **384** heldout, source-reachable, 2–6 step start-to-target planning tasks. The goal interface supplies exact raw binary sensor states; **this does not test natural language**.
- For the active and seeded-random agents, evaluate the *same* tasks and 12 × 64 source state/action predictions. Charge 80 interventions/arm/world, 960 interventions per arm in aggregate. Count confidence errors, abstentions, distinct states visited and state/action coverage.
- Diagnostic exact state/action memorization under the *same active history*; cold snapshot/restore must reproduce all transition predictions and plans, reject tampering and retain chronological evidence.
- Frozen `SELFTEST_SIGNAL` only if active solves >=55% of 384 goals, beats equal-action random by >=10 percentage points and makes **zero** confident wrong source transition predictions. Otherwise preserve `SELFTEST_NEGATIVE_OR_INCONCLUSIVE`.
- Full-process time/CPU, hypothesis counts, persisted bits and experimental source SHA256 receipts recorded with every fixture.

## Limits
This study challenges the **no-reset and hidden three-parent causal-boundary** assumptions, but still gives transparent four-bit sensor vectors, four primitive action channels, fixed six-action planning horizon, and exact desired sensor goals. Tasks are selected by evaluator to be achievable within six steps. This is not independent natural-world transfer, language acquisition, unrestricted representation learning, full AGI, or a matched conventional neural baseline. Active action selection incurs additional compute.

## Reproduction and governance
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-61 -p 'test_*.py' -v
```

Dedicated Linux/Windows SELFTEST, exact-source G29 atlas and mandatory two-platform inherited regression are independent engineering qualifications. No DEV/PRIMARY first-use, scientific acceptance, deployment, merge, model-loop promotion, new controller/runner, scheduled task or paid model API.
