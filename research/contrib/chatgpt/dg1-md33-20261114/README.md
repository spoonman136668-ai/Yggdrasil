# DG1-MD33 — fully trained conventional controls for MD32

**Status:** External, research-only synthetic controls. Preregistered before
source and before any transfer or cold result. No change to the Yggdrasil
native non-transformer/non-token model, MD29/MD30/MD31/MD32 frozen research,
`main`, accepted state, owner controller, research loop or original datasets.

## Question in plain English

MD32 created a new causal task with real, paid encoder/decoder interventions.
A physical two-probe policy already solves every test fixture for **+0.800**
net reward; a privileged knowing-the-answer oracle earns **+0.960**. Before
trying another unconventional learning rule, we need to know how much reward
a **trained conventional learner** can achieve using the same real
cause-and-effect experience. If such a learner reaches **+0.910 or higher**
on both novel structural transfer and independent cold restoration, this
tiny task is considered saturated for testing new intelligence mechanisms.

## Frozen data and custody

- Exact MD32 baseline parent: `7551d15cafe9bf028242f009de2218773a7b40ba`.
- **Preregistration-only commit before any new implementation or scores:**
  `fc827ffb0e1f1ec3095b535e3ae7a7c9ad9ac4f7`.
- **Train:** synthetic seeds 11000–11767, 768 context episodes grouped into
  192 four-episode blocks. Three source laws, four decoder offsets, stable
  and rewired conditions, eight repetitions each.
- **Validation:** 12000–12191, disjoint 48 four-episode blocks with
  the same three training families, two repetitions each.
- **One-shot unfamiliar transfer:** 13000–13191, 48 new blocks of
  braid/inhibitor/crossbridge (3 unfamiliar families).
- **Cold restore:** 14000–14095, 24 more unfamiliar-law blocks, with
  independently rehydrated trained checkpoints.
- Every model learns only from **3,072 physically charged public actions**
  (768 training episodes × 4 real steps). The validation dataset also
  incurs 768 real actions; it is never used to fit categorical counts.
  The recurrent model uses the validation set only for prespecified
  early stopping. All model actions on test are new and paid.
- Policies get only publicly observed precursors, diagnostic menus,
  four-bit downstream responses, charged action history, and block
  reset boundaries. They cannot see hidden law, motif, offset, rewire,
  seed, future, or underlying world objects.
- All official MD32 cohorts and prior MD29–MD31 evaluated/registered
  datasets are inaccessible. The MD32 fixture range 9100–9195 is not
  training, transfer or cold input to this experiment.

## Precommitted conventional baselines

**1. Bayesian factorized causal response model.** Fit a Dirichlet-smoothed
categorical distribution of encoder/decoder responses from publicly paid
probes. A separate four-episode memory stores exact previously observed
responses. It pays a fresh probe unless predictive confidence is at least
94.6667%, the one-step value-of-information break-even for a 0.08 charge.

**2. Fully trained recurrent world model.** Fit a conventional Elman tanh
network (964 trainable parameters, 24 recurrent hidden dimensions) using
full eight-step BPTT per block and Adam with a frozen training seed,
epochs/early-stop rules and holdout validation. It predicts the next
charged four-way mechanism response given a public probe action and
sequence memory. No hidden graph supervision or free world action is used.
It maintains a separate exact memory of physically observed responses;
its hidden state updates only when an actual probe returns a result.

**3. Empirical model-based RL.** Fit a four-way categorical physical
transition model for all eight encoder/decoder channel queries using the
same 3,072 paid training actions. A finite-horizon one-step Bellman
value-of-information comparison evaluates paying a real probe versus
committing a currently predicted actuator. The model cannot call
`World.step` to look ahead or see latent physical state.

We retain the strong fixed two-probe physical reference, the blind
terminal-zero action and a privileged oracle upper bound, but the latter
is expressly not a deployable learner.

## Precommitted scientific decision

If **any** independently fitted conventional controller achieves at least
0.91 mean reward on *both* 192 unfamiliar transfer and 96 separate cold
episodes, mark MD32 **`TRIVIAL_FOR_NOVEL_GAIN_STOP`**. This is a
*task saturation decision*, not evidence of new general intelligence.
If all trained models remain at or below the handcoded reference on
transfer, mark **`CONVENTIONAL_CONTROLS_UNDERQUALIFIED_NO_NATIVE_GATE`**;
improve task/control adequacy only in a separately preregistered study,
never by tuning this frozen evaluation after seeing its results.

If the best controls exceed blind but do not saturate, MD32 still does
**not** automatically qualify native Yggdrasil scientific improvement:
physical information and full-process compute parity, hard transfer,
cold retention, and independent source-locked first-use qualification
remain mandatory. Every negative or mixed result must be preserved.

The commit/run evidence belongs only in this repo and GitHub Actions;
no user chat Library files.

## Reproduction

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-md33-20261114 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-md33-20261114/evaluate.py
```

The exact-source Windows/Linux workflow runs the entire inherited
Yggdrasil regression and all frozen MD30/MD31/MD32 controls before
MD33 tests and the single synthetic transfer/cold evaluation. The
separate G29 atlas must qualify on that exact candidate SHA. Cross-OS
public action and policy classification parity must pass; hardware-
dependent floating-point training losses and elapsed CPU cost are
reported separately rather than misrepresented as byte-identical.

## Verified MD33 synthetic development outcome — November 14, 2026

**ENGINEERING PASS, SCIENTIFIC SUPERIORITY UNVERIFIED.** The source-only
controls and data generator were frozen before model training and score
inspection. The actual 768-episode, **3,072-paid-action** training set, 192
validation episodes (768 paid steps), 192 unfamiliar-law transfer
episodes and 96 separately restored cold episodes were run as registered
in the MD33 synthetic protocol.

| Policy | Transfer reward | Cold reward | Transfer physical probes |
|---|---:|---:|---:|
| Privileged oracle (upper bound only) | 0.9600 | 0.9600 | 0 |
| Fitted Bayesian causal response model | **0.8133** | **0.8133** | 352 |
| Fitted empirical model-based RL planner | **0.8133** | **0.8133** | 352 |
| Handcoded public two-probe reference | 0.8000 | 0.8000 | 384 |
| Trained 964-parameter Elman recurrent model | 0.0763 | 0.0763 | 96 |
| Blind fixed action | −0.1650 | −0.1650 | 0 |

Bayesian and model-based RL used **identical physical action traces**,
succeeded on all 192 transfer episodes, and saved only **32 paid probes**
against the perfect handcoded policy. This improves mean reward by just
**+0.0133**. Identical behavior is **not independent evidence** that two
architectures each provide a strong unique conventional baseline.

The recurrent world model actually trained its weights (cross-entropy
**1.4062 → 0.3125** on train; best validation **0.3125**, 63 training
epochs, best epoch 51), but reached only **43.75% goal success** on the
unfamiliar motifs. Its low probe count reflects risky, poorly
transferred predictions rather than intelligence/efficiency improvement.
The result is preserved as a conventional-learning negative.

The best fitted control is **0.1467 below** the privileged 0.9600
upper bound and fails the predeclared 0.9100 *task saturation* stop.
However, the task's two-probe physical strategy already achieves
100% goal success: what remains primarily concerns **paid-probe
efficiency**, and a strong matched-compute, truly independent
conventional baseline remains UNVERIFIED. Therefore **no native
Yggdrasil intelligence, transfer, retention, AGI or RSI gain** is
established.

### Qualified exact source and cross-platform custody

- Original frozen prereg-only commit:
  `fc827ffb0e1f1ec3095b535e3ae7a7c9ad9ac4f7`.
- First tested source: `782f6755864108e792fc02a141c69c771e8aa797`.
  Its engineering parity job initially failed **only** because
  Windows wrote a CRLF terminator in the split JSON; parsed splits
  and full portable model/action receipts already matched exactly.
- Workflow-only UTF-8 LF serialization fix:
  `d87110177ae48b2ba20485901ba6dcc8412d242b`.
  **No** scientific model, hypothesis, hyperparameter, generator,
  seed, training action or threshold was changed.
- Exact source-qualified run:
  [MD33 qualification 43623486120](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43623486120)
  **SUCCESS**, Windows and Linux each **109/109** regression tests
  (54 inherited + 32 MD30 + 7 MD31 + 8 MD32 + 8 MD33), plus
  byte-identical action, physical reward, split and classification
  parity. [G29 source-atlas acceptance 43623628942](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43623628942)
  **SUCCESS** on both platforms.
- Detailed metrics and source/build/runtime provenance are preserved
  in `result.json` and `provenance.json`. Complete CI artifacts
  are attached to the workflow runs, not to the user's chat Library.

**Final decision:** Freeze MD33 as a completed *synthetic
control-adequacy diagnostic*, not SCIENTIFIC_PASS or native model
promotion. Do not retune this cohort. The next worthwhile research
decision is a harder consequential-intervention benchmark with fully
trained matched-compute controls; do not start another unconventional
learner solely because the present tiny task shows an oracle gap.

**DEPLOYMENT:** None. No official first-use, merges, Yggdrasil
native-weight changes, accepted refs, owner loops, runners, schedulers,
Forge/Wingless/Hybrid integration, or main mutations. The independent
CKB proxy-fanout failure is still a separate infrastructure workflow,
not MD33 science.
