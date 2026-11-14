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
