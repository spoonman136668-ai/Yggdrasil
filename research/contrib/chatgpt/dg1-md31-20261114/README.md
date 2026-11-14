# DG1-MD31 — paid structural-change evidence ledger

**Experimental status:** Independent, research-only successor to frozen
[DG1-MD30 PR #1027](https://github.com/spoonman136668-ai/Yggdrasil/pull/1027).
Synthetic development, no official MD30/31 first-use, no native Yggdrasil
integration, and no model/weights/accepted-ref changes.

## Plain-English question

Does a persistent non-token causal learner work better if it spends one *real,
paid physical intervention* after a possible structural change, then uses
the observed consequences to decide whether to remember its earlier
explanation or adopt an alternative? We previously saw MD30's tournament
sometimes help on rewires but suffer on stable conditions. This line
tests a *new*, prespecified change-detection hypothesis. It does **not**
alter or tune MD30.

## Frozen-before-code custody

- Original frozen MD30 source parent:
  `70a8e6de35d255ecf834a4ce8ee97650d54f32c7`.
- MD31 first commit is **preregistration only**:
  `5e8a99a172d978c3dc31241c5d0e7efb129fa3b4`.
  All exact cohort/motif assignments, changes, compute, action costs,
  hypothesis selection, gate threshold, negative controls and result
  classification are in `prereg.json`, frozen before MD31 candidate source.
- Existing six-variable environment, 768 native response hypotheses,
  MD30 Bayesian control, native model, and shared 1,920 charged
  training-action observations are imported **unaltered**.
- Previously studied synthetic seeds 5301–5360 and 6301–6360 are
  **not** MD31 evaluation data. The newly frozen **synthetic**
  evaluation is seeds 8301–8420: 120 episodes, 40 per transfer motif,
  balanced 60 stable vs 60 rewired.
- Separate fixture-only seeds 7301–7312 test physical identifiability:
  stable and rewired stage-two worlds initially show identical public
  state, but at least one paid internal-node intervention distinguishes
  their causal consequences. If this fails, **TASK_NO_GO** before scoring.

## Model and controls

`change_ledger.py` wraps the frozen MD30 persistent tournament without
changing its source. The ledger selects a stage-two diagnostic from C/D/E,
value 0/1, by maximizing the 32-versus-32 competing hypotheses'
predicted downstream disagreement. Its single physically charged
observation supports stage-zero-memory reuse or stage-one-memory
reopening. A fixed evidence margin (0.75 per hypothesis) selects
the memory bank. Every gate arm pays exactly the same first stage-two
probe, with these matched controls:

- evidence-gated bank choice (new native non-token candidate);
- paid sham detector that *always* chooses stage-one bank;
- paid always-carry detector that *always* chooses stage-zero bank.

We also independently run the unchanged original MD30 native tournament,
fully trained Bayesian filter, and fixed actuator A, each subject to
the same episode action cap with all actual diagnostic costs charged.
Only physical `World.step` receipts update hypothesis predictions.

## Falsification, not curve fitting

The development-only success rule requires mean reward +0.05 versus the
strongest frozen reference, a positive deterministic paired-bootstrap
lower bound, no more than 0.03 loss in **any** transfer motif or
stable/rewired regime, a change-detection accuracy >=0.65 and at least
+0.03 net reward over *both* matched paid-probe ablations.

An encouraging average that fails any of those conditions is
`DEVELOPMENT_MIXED_NO_PROMOTION`, not scientific proof. No official
cohort seeds are accepted. There is no post-evaluation tuning. A
development-only pass still would not authorize first-use, model
promotion, a merge or autonomous-loop integration.

## Reproduction

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-md31-20261114 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-md31-20261114/paired_preflight.py
```

CI also runs all **32 existing MD30** focused tests, the mandatory
**54 inherited Yggdrasil** regression tests, and the separately pinned
G29 source atlas on both Linux and Windows. Exact portable model,
action, and reward receipts must match byte-for-byte across platforms.
The first-use lock and all original heldout results remain untouched.

## Frozen development result — November 14, 2026

**Classification: `DEVELOPMENT_MIXED_NO_PROMOTION`.** The new mechanism
was qualified and scored **once** on its preregistered synthetic 120-episode
cohort (8301–8420). Its scientific success criteria **did not pass**.

| Arm | Mean net reward | Charged diagnostics |
|---|---:|---:|
| Frozen MD30 Bayesian filter | **0.477917** | 257 |
| Fixed action A | 0.460000 | 0 |
| Frozen MD30 native tournament | 0.390417 | 347 |
| New evidence-gated ledger | 0.375833 | 382 |
| Paid sham always switch | 0.356667 | 368 |
| Paid always carry | 0.350833 | 382 |

Native gated minus strongest Bayes = **−0.102083**; precommitted
paired-bootstrap 95% lower bound = **−0.352500** (required positive).
Differences by frozen heldout composition were braided **+0.116250**,
crossfork **−0.466250**, doublecollider **+0.043750**; the crossfork
regression substantially breaches the −0.03 maximum. Stable environments
lost **−0.457500** versus Bayesian; rewired environments gained
**+0.253333**. A favorable rewired subset does **not** excuse the
frozen mixed/negative result.

The change detector correctly kept prechange knowledge on **59/60
stable cases** but recognized actual rewires in only **18/60 cases**:
77/120 = **64.1667%** classification, below the frozen 65% gate.
Against the *same paid-probe* control arms, net reward advantage was
just **+0.019166** (sham) and **+0.025000** (always-carry), both below
the frozen +0.03 requirement. Cold memory restoration reproduced
identical action/reward traces.

### Engineering and source custody

**93/93 tests passed on Linux and Windows** on the identical candidate
`5cb0ac1629a28daadc194b574e94ad8bb3218db7`: 54 inherited, 32
original MD30 and seven new MD31 fixtures. The full portable results,
hypothesis-memory hashes and physical action traces matched byte-for-byte
across platforms. G29 atlas qualification passed on both operating
systems with original source pin `d86d7d91b1312d69291a5d4389834f60d033deb4`.

Full exact-source evidence:
[MD31 qualification run](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43615658167)
and
[G29 source atlas](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43615718256).
The detailed immutable metrics, negative controls and scientific custody
are retained in `result.json`, `provenance.json` and the run's two
CI artifacts. Neither artifact uses the user's chat file library.

**Scientific interpretation:** the evidence gate mostly selected the
prechange bank, even on actual structural transitions. This is a
falsifiable *limitation*, not grounds to retune the already observed
dataset. Stop this MD31 candidate; preserve negative results. No original
heldout cohorts, Yggdrasil weights, accepted refs, controller or loop
were changed. The separate CKB proxy-fanout workflow remains failing
and is not an MD31 scientific failure.
