# ITD-02 V35 — frozen action-conditioned ring-local feature representation trial

**Chronology and isolation.** Preregister BEFORE executable V35 code or any V35 reward-law evaluation. Parent is V34 draft PR #625 exact head `fbfd6a97556be1ccb9263ba12725601924ececdf`, V34 independent Windows/Linux digest `580bd1f834ade2e466847b466967384c38a92035041a33bc49e05fbfa43d6fc9`; predeclared V34 outcome `V34_FIXED_LOCAL_CREDIT_ABLATION_NO_RESCUE__NO_SCIENCE`. Original V22 8-cell ring, V24–V26, V32 selector, V33/V34 evidence, scientific acceptance, Mind-Palace, FORGE/CKB-plane and independent Q1/Q2/Q3 scientific holdout remain unchanged. New D1/D2/D3 toy families below are publicly frozen **before candidate implementation**, but this is not an independently blinded real-world holdout.

## Single candidate — local second-action-conditioned public feature basis

V34 found V22 action_partition reduces cross-context spillover but worsens mean decision regret. Instead of hard-disconnecting cells, V35 tests a *fixed differentiable local readout basis* that exposes the **prospective second action** at the existing original native second-action output site, without changing original cell identity, 4-hop transport, error/credit rule, optimizer rate, learnable parameter count, source bank, or public events.

Candidate `LocalActionConditionedRingDev` opt-in subclass of unchanged `SharedContextRingDev(mode="shared")`; each cell retains the same original 20 public-only input features (bias, seven incoming cue/actual-first channels, 12 cue×first products), eight local 20-element heads, and three action biases: **163 trainable scalar values** exactly. For a prospective chosen second action `a`, the **12 existing cue×actual-first interaction features** at each cell are multiplied by `0.25 + 6.0*credit(cell,a)`, where `credit(cell,a)` is the existing original four-hop scalar neighborhood return kernel from that original action's output site, `SharedContextRingDev._coefficients(a)`. The first eight bias / direct transported public channels are unchanged. No new channels, global feature table, labeled regime, handcoded answer oracle or reward-law input. This fixed local geometry binding is **not learned identity**, though the resulting local weights update only from actual selected reward and existing neighbor credit.

Original V22 score and update algorithms operate on the action-conditioned features by setting the candidate action **only for the duration of that one score/update call**. Frozen checkpoint enveloping must explicitly identify `v35.action_conditioned_ring.source_only.v1`, fixed 0.25/6.0 rule, digest and intact original V22 source-only checkpoint; restore MUST NOT silently reclassify a plain V22 bank as a V35 candidate. Must reject corrupted, oversized, frozen-mutable or pending-episode checkpoints. No direct new long-range edge or source-parameter copy. The extra fixed basis is calculated from the original ring geometry and must preserve original ring message validation.

## Truly new-to-V34 evaluator-only frozen toy families

Original public 4 cues and 3 first/3 second actions, original source law `R0=research.itd02_v18_intermediate_plasticity_audit.target(cue,first,second,nonlinear=True)`. For `c=PUBLIC_CUES.index(cue)`, `f=ACTIONS.index(first)`, `a=ACTIONS.index(second)`, all worlds are `max(-3.0,min(9.0,x))`:
- D1: `R0 + (2.4 if (c+2*f+2*a)%4==0 else -0.8) + 0.12*(f-1)`
- D2: `R0 + 1.75*(1 if (c+f)%2==0 else -1)*(-1,0,1)[a]`
- D3: `R0 + (3.2 if int(SHA256(("V35-D3-5107:"+str(c)+":"+str(f)+":"+str(a)).encode()).hexdigest()[:8],16)%6==0 else -0.55)`.

Unseen does **not** mean mathematically independent: all synthetic mappings share original cue/action/task scaffolding. Do not retune the candidate basis or replace any D world after observing results.

## Locked selected-public protocol and controls

Source bank: 576 actual selected public source rewards from original `train_source()["pretrained_shared"]`, frozen, byte-identical across arms. Each target arm starts with a fresh cold native V22 learning bank (163 scalars), processes the *same* original `selected_map()[0]` twelve selected target rewards for its world, then obtains exactly **three prospectively selected public second-action rewards** at original cue/first context indices `(0,4,8)`. No arm gets unselected reward, future world truth, stage label or selected feedback of another arm.

Seven predefined independent arms per D1/D2/D3 (21 arms total):
- V35 action-conditioned local ring + original V30 count-first **novelty** external chooser, primary.
- V35 action-conditioned local ring + original V30 **greedy** chooser.
- Original native V22 **shared** FAST ring + original novelty chooser.
- Original native V22 **action_partition** FAST ring + original novelty chooser.
- Original native V22 **shared** FAST ring + deterministic random chooser (V30 seeded RNG).
- Original full 80-feature **RLS/CUSUM** + independently choosing original novelty policy.
- Same conventional RLS/CUSUM + independently choosing greedy policy.

External chooser reads only public cue/first, selected-action visit counts and current learner scores; candidate supplies same exactly sourced scores, not hidden test outcomes. **Equal counts 12+3 and same public cue/first, but independently chosen second actions — DO NOT claim equal selected-action feedback across independent arms.** As a separate strictly paired diagnostic, replay the primary V35's actual 15 selected feedback events into original shared/partition/80-feature RLS, labeling these as **matched-action controls** (not independent exploration) to separate changes in representation from changes in chosen actions.

At base budget 12 and at budget 15 freeze a cold-restorable clone of each learner. Evaluate all 12 public cue×first contexts, all 3 proposed second actions, 12-context total action regret and 36-output absolute prediction error; only evaluator accesses complete D law and only after model scores and selected actions have been fixed. Capture selection/feedback traces, native 163 scalar weight SHA, checkpoint bytes <=12288, source SHA, original edge input/output/reverse messages, timing, CPU, memory peak, host-specific and no-learn negative unchanged. The V35 added wrapper must not silently break V22 checkpoint size/integrity or source protections.

## Frozen ordered acceptance

1. Original native source or pretrained source bank drift, any hidden family/reward passed to chooser/model, missing arm/paired controls, unequal public budget, changed original 8-cell/4-hop identity, score/credit route inconsistency, new learned scalars, no-learning control mutation, checkpoint invalid/frozen mutation, missing full table and resource accounting, Windows/Linux canonical evidence mismatch, original focused V34→V22 regression failure => **`V35_ENGINEERING_BLOCKED__NO_SCIENCE`**.
2. Fewer than **2/3 D worlds** achieving 10%+ original shared NOVELTY 12-context regret reduction by V35 NOVELTY at budget15, or V35 three-world mean regret not >=10% lower than original shared NOVELTY mean => **`V35_LOCAL_BASIS_TRANSFER_GAIN_NOT_ESTABLISHED__NO_SCIENCE`**.
3. If (2) passes but V35 mean regret at budget15 does not outperform **both** independently choosing RLS novelty and greedy by >=10%, or V35 fails to beat each world's *better* independent RLS in >=2/3 worlds, or V35 new candidate's 36-output absolute prediction error exceeds original shared by >10% mean => **`V35_STRONG_CONTROL_OR_PREDICTION_GATES_FAILED__NO_SCIENCE`**.
4. Only all previous pass: **`V35_BOUNDED_NEW_LOCAL_BASIS_ENGINEERING_POSITIVE__NO_SCIENCE`**. All classifications remain source-only synthetic development, never scientific first use.

Do not retune U1/U2/U3 V33/V34 evidence, do not overwrite V22 original file, train original accepted model, merge, override G29/write-proxy failures, promote model checkpoint, claim native learned representations/identities or autonomous native cognitive generalization, or change FORGE/CKB-plane/controller. Preserve the draft evidence, exact-source host logs, full failures and immutable chronology.
