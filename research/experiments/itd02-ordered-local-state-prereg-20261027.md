# ITD-02 locally retained order-sensitive reward readout — 2026-10-27

Source-free, development-only candidate. Freeze parent #582 at `a39171a76d0d7817e3563682bb139a9d7ecf37c4` and experimental v3 two-phase source at `50f7326026f6bf857ab9c62a29fa1b57db4ad815`. Neither accepted science nor autonomous source owner is touched.

## Precommitted single mechanism

The current two-phase neighbor input has 15 distinct ordered contexts, but averaging two independent sigmoid outputs collapses them to nine. Replace **only the native reward readout**, not `LocalTaskRuntime`, with *order-sensitive, nonlearnable local phase retention*: each candidate action's first phase prediction is held at each reward-output site in a temporary local vector of three scalars; after the second phase, the site computes `0.75*second + 0.25*first` instead of their arithmetic mean. This asymmetry makes the order of the two local phases visible in the final score, but **does not create learned temporal state**. It is a strict negative/engineering control against the more expensive design of adding learnable persistent state. No new training parameters, model checkpoint fields, extra predict calls, or more than existing six native predictions per decision. Phase order retained only within the same action's scoring operation, not across public observations. No global oracle or new learner.

Code evaluation must prove the readout differs under reversal when its two phase predictions differ, that two-phase local ordered capacity remains 15 in the codebook, that no original public action/reward bit is altered, and that original v3 snapshot/cold restore works. It must not falsely assert learned self-training, persistent cross-step memory, or a solved information bottleneck.

## Frozen independent source-free test

Previously unused 64 family/seed pairs, families **78..85** and seeds **76..83**; 90 familiar then 90 unfamiliar/reward-changed episodes. Three source-legal rewards (-3,0,+10), same public-only source-blind action exploration, genuine source-selected reward feedback, four independently acting learner families per implementation (native, full-history count, EMA(0.5), rolling last-six), matched 46,080 public events per OS and source. GitHub Windows and Linux source-sha pinned baseline v3 vs order-sensitive candidate. Complete trial and negative-control retention. Candidate must improve native mean on-policy reward in **both** phases and compare favorably with independent conventional actors for any future promotion. Cost is at least equal to two-phase native predictor and must be measured, not assumed retail ready.

Candidate G29 exact-source Atlas, authenticated original task custody, FSA scientific use, and retail hardware remain separate vetoes. No merge or promotion from this engineering experiment. After evaluating, do not retune on the same split.
