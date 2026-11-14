# AAI-03A: structural causal-law benchmark admission

The previous AAI-02B fixed association selector was **scientifically invalid**, despite valid engineering. This is an **independent** synthetic benchmark with eight distinct causal transition laws, interventions with noisy outcomes, 32 passive distractors, eight total event-memory slots, and a terminal real action whose outcome is scored against an independently sampled goal.

AAI-03A tests **benchmark usefulness**, not any new learning mechanism. Exact Bayesian utility planning is intentionally a strong known-model control. A trained, Laplace-smoothed tabular likelihood, information gain, random actions, a no-intervention policy, a privileged expert upper bound, and negative cue/label controls are evaluated under the frozen protocol.

Preregistration: `7f5b8b7150446a7b54a9fd9bc962cd584b2c92a6`, before evaluator source and outcome.

Reproduce:

```
python -B -m unittest discover -s research/contrib/chatgpt/AAI-03A -p 'test_aai03a.py' -v
python -B research/contrib/chatgpt/AAI-03A/run.py
```

No native Yggdrasil integration, model edit, controller, owner-loop, runner, accepted-state change, or deployment. No post-result changes to thresholds, worlds, seeds, laws or scoring. Source-only evidence stays in this repository; never upload a file to the user's conversation library.
