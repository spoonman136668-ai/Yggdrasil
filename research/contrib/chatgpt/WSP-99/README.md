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
