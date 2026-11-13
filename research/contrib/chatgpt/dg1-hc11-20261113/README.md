# DG1-HC11 — Confidence calibration by repeatable physical witnesses

**External, isolated, synthetic development research.** Preregistration was committed separately before any HC11 implementation or outcome at `835c004206b6febde17a4bf3e14c6f541cf35ef0`, starting from the frozen HC10 draft #977 at `c6a48d2d4460c85c428f97554b2e737e77ada52d`.

## Failure addressed

HC10 increased the number of return-to-A correct predictions, but also produced 128/512 confidently wrong predictions and tied a separately implemented conventional JSD controller. It also made 74/512 confidently wrong predictions in a cubic out-of-grammar cohort. Its source code and prior failures are not retuned.

## Frozen proposed safety mechanism

The native HC09 two-bank, 320-mask-bit causal program and physically charged HC10 action-selection policy remain unchanged. An *additional* bounded witness memory stores, at most, one record for each of 64 public state/action pairs. A record reaches confidence only after the **same real transition** has been observed twice in the current evidence epoch. Observed contradictory transitions, a bank switch, or an unresolved causal observation clear all prior witnesses. A queried prediction must agree with both the frozen underlying model and that repeated direct observation, else it abstains.

This is **not counterfactual transfer**: predictions on never-witnessed pairs must abstain. More cautious confidence is allowed to reduce coverage. It cannot guarantee against a hidden regime switch with no discriminating evidence.

The independent conventional control uses HC09's separately coded two-context model and Jensen–Shannon action chooser with the same witness memory. One-witness and ungated controls reveal the coverage/error tradeoff. Gated models have additional memory compared to ungated models, so do not claim equal total capacity. No hidden phase labels, evaluator answers, free simulator queries, gradient training, tokens, models, or paid APIs reach the learner.

## Prospective physical tests

New seeds 91001–91008 are continuous A→B→A with 40 charged steps, inversion at steps 16–31. Seeds 91009–91016 use stationary majority physics; 91017–91024 use cubic out-of-grammar physics, each 48 charged steps. Up to eight externally forced bit flips cost physical steps and teach no mechanism label. Final evaluator-only audits cover 64 state/action pairs; A→B→A also audits at steps 16 and 32 without revealing answers.

The preregistered positive DEV bar requires final return-to-A at least **32/512 correct with zero confident errors**, stationary majority at least **64/512 correct with zero errors**, cubic OOD **zero errors**, and fewer confident errors on ABA and OOD than ungated HC10. Even a full DEV success and superiority over the conventional witness control would not qualify as independent scientific acceptance.

## Reproduce and review

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-hc11-20261113 -p "test_*.py" -v
python research/contrib/chatgpt/dg1-hc11-20261113/eval_dev.py
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build_code_atlas.py --check-if-present
```

Official Yggdrasil research-loop execution, merge/promotion, native integration and WSP weight editing remain separate and unauthorized by this contribution.

## Frozen prospective development outcome — negative coverage

First testable source `c935c9f623b42b3f1dbf4f179f7ff0cc8b1ff559`; cross-platform run [43468455539](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43468455539). Full source and receipt identity in `result.json` and `provenance.json`. The 9 focused tests passed on both operating systems. Generated G29 was stale because the candidate adds files; that is an engineering indexing defect, not a scientific outcome.

| Frozen cohort (512 evaluator-only transitions) | Native two-witness correct/wrong/abstain | Conventional two-witness | Ungated native |
|---|---|---|---|
| A→B→A | 8 / 0 / 504 | 8 / 0 / 504 | 294 / 156 / 62 |
| Stationary majority | 10 / 0 / 502 | 10 / 0 / 502 | 512 / 0 / 0 |
| Unfamiliar cubic | 14 / 0 / 498 | 14 / 0 / 498 | 281 / 44 / 187 |

Classification: **MIXED_DEV / PRIMARY NO-GO**. Zero confident errors were observed, but the preregistered required coverage (32 ABA, 64 stationary) failed, and the ordinary conventional controller was exactly tied. This approach is physical-experience recall with abstention, not safe compositional transfer. No post-result threshold or seed adjustment. Preserve the negative. No merge or native integration.
