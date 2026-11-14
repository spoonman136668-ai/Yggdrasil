# WSP-99 — delayed causal effects and hidden-state learning

**State: fixture-control engineering only. No WSP99 original PUBLIC or RESERVED first-use. Scientific improvement UNTESTED.**

## Plain English
WSP-98's direct weight editor predicted all its test outcomes, but the strongest conventional and symbolic methods were perfect too. WSP-99 builds worlds where actions can change a hidden memory without changing the next visible state; consequences may appear a step later. This makes remembering the *history of actions* necessary in principle, though usefulness on unseen problems still requires experiments.

## Preregistered sequence and authority
- Task prereg before simulator: `babec7b7a352ab5f322217dac200dbf5591edee6`.
- Strong symbolic and conventional comparator budgets frozen before their implementation: `42d0b79ef173b00c3a2b0270fadb80b30bcdf044`.
- GRU-16 capacity addendum frozen before the GRU implementation: `9c0beaf1a55a7b1dd73e5e21d3936042f94d1788`.
- Exactly eight DEV fixture worlds `0..7`. PUBLIC `99011..99042` and RESERVED `99101..99164` cannot be instantiated via `FixtureWorld`. WSP98's 40 reserved worlds are not consumed.
- Independent symbolic finite-state version-space control, fixed 16-unit gradient-trained tanh RNN, memoryless negative comparator, and stronger 16-unit fully gradient-trained GRU are implemented. All strong baselines receive observed histories and actions only; no hidden-latch oracle passed to any learner.
- DEV training uses at most 24 short epochs. The original budget, if separately admitted, is fixed at 1800 epochs per registered seed for each neural control, with source-fit checks and no heldout-driven early stopping. The symbolic solver performs source-consistent full grammar enumeration.

## Development commands (no original worlds)
```sh
python -m pip install numpy==2.1.3
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s research/contrib/chatgpt/WSP-99 -p 'test_*.py' -v
```

## Remaining qualification
Source-pinned G29 generated atlas and mandatory inherited full regression are required on exact candidate SHA across Ubuntu and Windows. After those succeed, the next independent task is to finalize source/action generation and scoring, freeze all original first-use mechanics, and separately authorize the first PUBLIC original cohort. Do not assume a successful simulator or recurrent fixture test proves intelligence or unique superiority of directly programming numerical weights. Preserve negative findings; do not tune causal laws after first-use results.

**Isolation:** draft only; no merge, accepted model, controller, scheduler, queue, paid API, production or autonomous research-loop mutation.

## New gate — source-matched experience and full-budget DEV headroom

The prospective fixture policy was frozen **before implementation** at `44099f8778d3a2692ba2efa8d699194ae4c809f2`. Its source constructor (`source_eval.py`) supplies 24 common four-step observational episodes plus eight four-step investigative episodes per active/random arm, with identical starting states and action budgets. An active action can use only prior visible states/actions, never the hidden oracle. Exactly 24 disjoint starting states are reserved for each fixture's two-branch three-step delayed counterfactual test. All models' predictions are frozen and SHA-256 hashed before fixture truths are requested.

The full-budget DEV diagnostic was frozen at `7d7161b59169d44c32a317dbe028e5666170dd22`, before implementation of `fixture_headroom.py`. It trains the conventional RNN16, GRU16 and memoryless16 on the same source for all three preregistered seeds at 1,800 epochs each; selects by source training loss ONLY; and scores an independent symbolic system-identification control. All original PUBLIC and RESERVED worlds remain disabled. The test is intentionally expensive relative to the small fixture unit tests, so it runs only when the dedicated `ci(wsp99): original-free fixture headroom one-shot` commit is dispatched; it is **not** part of every push or full regression.

**Interpretation:** A ceiling tie with the symbolic or trained controls means this task does not yet demonstrate unique direct-weight programming superiority. A neural source-fit failure is also not a direct-weight victory. Development fixture outcomes are not independently sealed novel science, and cannot justify tuning original-world rules after inspecting results. Preserve results including negatives. WSP-99's source-blind controls and evaluation code do **not** claim a SCIENTIFIC_PASS or accepted Yggdrasil change.
