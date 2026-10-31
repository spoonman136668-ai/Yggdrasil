# MG95-A intervention-memory screen: independent equation check

Classification: SYNTHETIC DEVELOPMENT ONLY. Source commit `de7013c6bd39c5969fca3a9fc63576b7ed6c5faf`; file blob `8707c3be5954cf28e97fe4dc43a7a97dd9df0aff`.

Independent JavaScript reimplementation of the Python source's state-transition equations, identical 24 training events and 24 held-out events, yields:
- action-indexed two-counter memory: 12/24 correct; frozen state ones=[1,1], totals=[3,3].
- context-indexed two-counter memory: 12/24 correct; frozen state ones=[1,1], totals=[3,3].
- state did not change during evaluation for either model.

Mechanism interpretation: train combines observation and intervention regimes, so a 2-counter mechanism cannot preserve action/context/intervention distinctions. This is a failure to represent the conditional causal mechanism, not a legitimate advantage. No independent native architecture implemented.

Exact committed Python execution UNVERIFIED; original-world test NOT EXECUTED; required final regression UNVERIFIED; scientific claim NONE. Next candidate must store intervention-conditioned causal state, compare against equally informed conventional conditional-count and Bayesian/model-based controls under explicit storage parity, and demonstrate held-out shift. No promotion.
