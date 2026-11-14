# AAI-04A — four-family causal-law benchmark admission

This isolated contributor experiment follows valid *negative* AAI-03A benchmark admission and the invalid AAI-02B scrambled-label control. The goal is to assess whether a more difficult task has useful causal intervention value, room below the privileged expert ceiling, and genuinely disjoint held-out law **families** for training/fitting.

Preregistration SHA: `8bcf5aeb02003ea198c954461ab2532996815559`, committed before evaluator source and first outcome. Frozen source uses a **12-law, four-family** synthetic world; two noisy do-interventions, two-step irreversible terminal action plans and a four-slot causal-memory limit under 32 passive distractors.

The known-catalog exact Bayesian utility planner, greedy information-gain planner, exact Bayesian random/no-probe controls, fully fit supervised tabular learner, shuffled-label/sham controls and true-law expert ceiling are all retained in the same frozen evaluation. **The expert ceiling is privileged and is never a like-for-like scientific superiority baseline.** The exact Bayesian prior already knows the 12-law structural catalog, even for held-out train families; thus positive transfer is not proof of discovering an entirely unknown law.

Reproduce:

```bash
python -B -m unittest discover -s research/contrib/chatgpt/AAI-04A -p 'test_aai04.py' -v
python -B research/contrib/chatgpt/AAI-04A/run.py
```

A successful AAI-04A would establish **benchmark admission only**, not a new associative mechanism, intelligence improvement or permission to modify Yggdrasil. The next AAI-04B would require its own preregistration, matched learned controls, resource budgets, causal transfer, cold retention, negative controls and independent scientific qualification. Preserve negative outcomes; no post-result adjustment. Keep evidence solely in repository.
