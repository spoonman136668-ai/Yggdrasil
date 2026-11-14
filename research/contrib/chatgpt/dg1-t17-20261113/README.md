# DG1-T17 — paid intervention-conditioned causal transfer

**Frozen external research. ENGINEERING: original exact-source dual OS PASS. SCIENCE: MIXED_DEV / PRIMARY NO-GO. DEPLOYMENT: NONE.**

## Question and independent setup
After CR16's primary failure and recurrent serialization portability defect, can a bounded causal-module learner use one physically charged diagnostic intervention per held-out episode to recall a previously trained A dynamics regime after B and correctly reuse factorized causal relations in an unfamiliar C? This independent study uses new seed identities `410001..410016`, integer causal worlds, fully trained conventional controls, matched training traces, and a fixed-point fully trainable eight-cell recurrent control.

The preregistration was committed at `a4c0ee310f12f55535f8b5dea6ab2f0b190a6fe9` before the source, controls, or original outcome. No previous failed protocol was altered. Frozen thresholds and classification rules are in [prereg.json](prereg.json).

## Design and custody
16 worlds x 5 arms x 160 paid training steps = 12,800. Two audit marks (128,160), 16 episodes each, one charged diagnostic and one charged learner-selected goal action per episode/arm/world = 5,120 more. **17,920 genuine charged actions total**. Hidden dynamics, oracle action labels and audit outcomes never train learners.

Controls: no_archive, random_route, forgetting_rls, integer_recurrent. The latter trains all input, hidden recurrent, readout and bias weights via deterministic fixed-point arithmetic. The learner under investigation is `causal_modules`; its causal-module routing uses measured diagnostic consequence, not hidden true regime labels.

## Original first-use outcome (identical aggregate scores on both operating systems)

| Learner | Cold return-A regret | Never-trained C regret |
| --- | ---: | ---: |
| causal_modules | 0.000529477838 | 0.007491507567 |
| forgetting_rls | 0.009078669827 | 0.009288426954 |
| integer_recurrent | 0.158090132754 | 0.135667095892 |
| no_archive | 0.015508043580 | 0.026168790646 |
| random_route | 0.010509467684 | 0.012003828306 |

The candidate met all cold-A advantage gates. For unfamiliar C, it **failed** the frozen minimum margin against the strongest conventional control, the random-route comparison, the per-world win threshold, and the false module-routing threshold. Other structural reuse and CPU gates passed. Exact gate booleans and values are in [result.json](result.json).

**Verdict: valid MIXED_DEV, primary NO-GO.** Retention recovered, unfamiliar causal composition not convincingly solved. No AGI, language, real-world transfer or native Yggdrasil improvement is claimed. Further work needs a genuinely separate preregistration, not tuning to the T17 outcomes.

## Verification, receipts and reproduction
Original first-use PR head `30ea69b11544240fa6cb7fc123da972f06afef64`. Original workflow [run 43539743048](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43539743048): Linux and Windows 9/9 prefirstuse tests, 54/54 full inherited regression, physical action budget/cold restoration PASS. Independent cross-OS parity job PASS after removing *only* CPU timing fields; complete checkpoint digests and all other fields matched. Independent G29 [run 43539743047](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43539743047): both OS PASS. Exact original full-world JSON artifacts **14090979483 (Ubuntu)** and **14091121901 (Windows)** remain in GitHub Actions rather than ChatGPT Library.

Pre-first-use toy-only controls (do not repeat original registered study):

```
python -m py_compile research/contrib/chatgpt/dg1-t17-20261113/t17.py research/contrib/chatgpt/dg1-t17-20261113/test_t17.py
python -m unittest discover -s research/contrib/chatgpt/dg1-t17-20261113 -p 'test_*.py' -v
```

This PR never authorizes scheduler/queue activity, native model mutation, merges, promotion or deployment.
