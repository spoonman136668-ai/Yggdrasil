# ITD-02 V33 — pre-executable preregistration: unseen synthetic world families and autonomous-action budget controls

**Scope and chronology.** This is a NEW, isolated developer-side synthetic assessment, frozen before executable V33 world/evaluator implementation or outcome inspection, from V32 draft PR #621 exact commit `446af1295c5c318c4c520f467b767d6ed700c9fe`. V32 exact-host evidence SHA `57dca7f34d119cbf1f10fbf9bb3c21b01c71b1e760fa256617522fa4f59c4ca7`, classification `V32_BOUNDED_SYNTHETIC_PROBATION_ENGINEERING_POSITIVE__NO_SCIENCE`, was trained/selected on V29 A/B constructed worlds and cannot be used as independent held-out validation. This V33 benchmark uses different frozen evaluator-only laws, without retuning fixed V32 source-surprise >=1.50 or 2-source-support returns. Independent parallel V31 heldout Q1/Q2/Q3 stream PR #619 is a separate research lane: **do not read, run or alter its sealed holdout laws or candidates**.

## Frozen genuinely new (relative to the V32 selector's implementation) reward families

All cues and actions use original `PUBLIC_CUES` (4) and `ACTIONS` (3), source law `R0 = research.itd02_v18_intermediate_plasticity_audit.target(cue,first,second,nonlinear=True)`, and original 12 unique selected contexts `selected_map()[0]` from V23/V29. The V33 synthetic reward laws exist **exclusively in the evaluator**, not any learner, chooser, selector, checkpoint, public feature or model. They are *preregistered before generation and evaluation*, but they are still designed toy families, not truly unknown real-world causal tasks.

Let `c=PUBLIC_CUES.index(cue)`, `f=ACTIONS.index(first)`, `a=ACTIONS.index(second)`; `clamp(x)=max(-3.0,min(9.0,x))`. Four frozen worlds:
- `A0`: `R0` unchanged source control.
- `U1`: `clamp(R0 + 1.4*(-1 if (c+f)%2 else 1)*(-1,0,1)[a] + 0.20*(f-1))`, source-vs-action interaction change.
- `U2`: `clamp(R0 + (2.1 if (c+f+2*a)%3==0 else -1.1))`, crossed-parity reward change.
- `U3`: let `h=int(SHA256(UTF8("V33-U3-9093:"+str(c)+":"+str(f)+":"+str(a))).hexdigest()[:8],16)`; `clamp(R0+(3.0 if h%5==0 else -0.40))`. Source-independent deterministic sparse action perturbation, seed **9093**, no adaptive search.

No adjustment if tasks are unfavorable. Source original 576 selected-feedback pretraining unchanged. After pretraining each independently initialized arm receives exactly **12 original selected public observations** in original order, with actual selected rewards returned by one of A0/U1/U2/U3. Next **3 additional selected feedback opportunities** occur at fixed public context indices 0,4,8 of that 12-case list, with only actual chosen second action reward delivered; each arm chooses *its own action prospectively* from cue/first, observed public counts, its own model scores, fixed random seed (if applicable). The feedback budgets therefore match by event count (12+3), cue/first context order, source pretraining, and task; **do not** falsely claim action-matched parity when choices differ.

Following three extra actions each arm receives **exactly 12 more public selected reward episodes** using the original twelve selected actions in order and source-world `R0` feedback, with **no stage/return signal** to learner, model or policy. For U1–U3 this is a genuine *evaluator-defined synthetic return*, not original-world first use. Snapshots after 12, after 15, after first 4 source-return events (19 total) and after all 12 source-return events (27 total) measure frozen 12-context action choices and regret, source/fast head regrets and active chosen actions. Return latency counts first original SOURCE choice at 1..12 observed return feedback, and false-fast occupancy is sum of active FAST on final eight source-return observations. The source-only world A0 serves as negative false-switch/retention control.

## Frozen comparison portfolio (all independent prospective action choices, equal public feedback counts)

1. **V32 NOVELTY** primary: unchanged V32 opt-in public source-surprise probation selector + original V30 count-first NOVELTY chooser. Original V22 fast ring only learns from selected public reward, frozen V22 source bank retained.
2. **V32 GREEDY**: identical V32 native learner/selector, external chooser maximizes its live ACTIVE action scores without count exploration.
3. **V32 ROUND_ROBIN**: identical native learner/selector, deterministic previous-selected-action+1 chooser.
4. **V32 RANDOM**: identical native learner/selector, independent fixed-seed 3001 uniform action chooser.
5. **V26 NOVELTY**: original V26 active selector + same V30 novelty chooser; historical negative reference.
6. **RLS NOVELTY**: full 80-feature online matrix-RLS/CUSUM, its **own** independently chosen minimum-public-visit-count action using its own conventional selected predictions.
7. **RLS GREEDY**: identical RLS/CUSUM, its **own** independently greedy selected second action.

All 7 arms have identical 576 source pretraining, 12+3 target selected-feedback, additional 12 source-return feedback; no learner receives any unselected reward, offline evaluator regret, world label, privileged stage boundary, or alternate arm's selected reward. Policy wrappers may receive public cue/first and original actual selected-action counts. The external experiment constructor alone knows the 12/3/12 schedule, a disclosed setup assumption. Offline **always-SOURCE**, **always-FAST**, V32 source/fast active, V26 active and conventional two-expert evaluations are diagnostic comparators, not independently trained action selectors. Record prospective selected-action pre-feedback absolute error, offline 12-context action regret, source bank identity, fast update count, 326 stored/163 trainable native scalars, <=12,288-byte restorable native checkpoint, original 8-cell edge message counters, memory/cpu/wall separately by host.

## Frozen ordered outcome rules

(1) If any original Git blob drift, hidden evaluator world ID/reward used in a chooser or learner, 12/3/12 budget mismatch, source frozen-state mutation, checkpoint integrity failure, missing one of seven independently choosing controls, incorrect 80-feature conventional update, cross-host canonical SHA mismatch, missing original V31–V22 native focused safety regression, incorrect action cost, or resource omission: `V33_HELDOUT_CONTROL_ENGINEERING_BLOCKED__NO_SCIENCE`.

(2) If among U1,U2,U3 **fewer than two** have V32 NOVELTY budget3 12-context regret at least 10% below *its own* budget0, or across all three the mean V32 NOVELTY budget3 regret is not >=10% lower than its mean budget0: `V33_UNSEEN_WORLD_LEARNING_GAIN_NOT_ESTABLISHED__NO_SCIENCE`.

(3) If in any U1/U2/U3 first SOURCE return is not achieved within 4 actual selected terminal reward observations, or any of their final eight return observations falsely use FAST, or A0 original source world post-probe V32 NOVELTY decision regret exceeds its budget0 by 10% (if zero, must remain zero): `V33_RETURN_OR_SOURCE_RETENTION_FAILED__NO_SCIENCE`.

(4) If the above pass but V32 NOVELTY does not beat **both independently action-selecting** full-matrix RLS NOVELTY and RLS GREEDY by >=10% on **mean** budget3 12-context regret across the 3 new worlds, or has fewer than 2/3 family wins versus the better of those two conventional controls, or has no changed 12-context action choice in at least two families: `V33_HOLDOUT_STRONG_CONTROL_GAIN_NOT_ESTABLISHED__NO_SCIENCE`.

(5) Only if all guards and prospective gates pass: `V33_BOUNDED_SYNTHETIC_UNSEEN_FAMILY_ENGINEERING_POSITIVE__NO_SCIENCE`. Even a positive would prove only predeclared *toy* holdout performance of an **externally hand-engineered** controller on retail-ineligible dev CI, not native learned self-improvement, genuine unfamiliar-world generalization, scientific first use, or production-readiness. Existing V25–V32 negative outcomes remain immutable.

Absolute prohibition: don't change original V22/V24/V25/V26/V32 source, V30 chooser, V31/V32 evidence, source memory, independent Q1/Q2/Q3 holdout stream, model promotion, FORGE/CKB-plane/controller, accepted checkpoints, G29/write-proxy acceptance, PR merge or deployments. Freeze code chronology and run exact-source Windows2022+Ubuntu24.04, canonical evidence SHA match; report all failures, no cherry-picking or threshold retuning.
