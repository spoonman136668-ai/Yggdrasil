# WSP-76 — Paid observed causal contrasts, not model-imagined novelty

## Prospective source and decision custody

**Preregistration FIRST:** `b83f86bc381c628e5e218d233ac6951fadcbb804`, committed before new WSP-76 physical source, action selector, test or result; read all fixed source seeds, independent charged streams, intervention policy, controls, success thresholds and authority limits in `prereg.json`. Parent [WSP-75 draft PR #973](https://github.com/spoonman136668-ai/Yggdrasil/pull/973) exact SHA `27c50ae9d5e22b5978c8c1f9eb748e836c64cd96` is frozen scientifically negative: 315/768 correct versus equal-paid random policy 325, physically charged contexts 371 vs random 393, 19 genuinely uncharged correct, 36 confidently wrong. Focused and G29 dual-OS passed; inherited full regression still running when WSP-76 branched.

## Why this mechanism differs

WSP-74 maximized neural model disagreement and lost to random exploration. WSP-75 added model-imagined reachable novelty and still lost to random while collecting fewer distinct paid state/action contexts. WSP-76 **does not use imaginary next states for action scoring**. It uses only physically charged, observed action/consequence differences and source-blind action balancing. The scientific question is whether real within-state intervention contrast evidence improves physically unseen neural prediction after explicit numeric hidden-weight edits.

## Source, controllability and real physical costs

- Independent source-role and action-shuffle SHA-salted SELFTEST seeds **5001–5016**. Twelve primary worlds: four **conditional XOR**, four **conditional AND/conjunction**, four **mixed/coupled** physical laws. Four **nested conditional adversarial** worlds, all four binary sensors, four public actions. Every hidden action-role toggles its OWN role bit unconditionally and may conditionally flip LOWER role bits; since roles can be set in descending 3→2→1→0 order, all 16 public sensor states are structurally reachable, even though individual experimental policies may fail to explore them. We verify this by full evaluator-only reachability enumeration AFTER all learning, and freeze ≥12/16 as mandatory source quality gate, with no post-hoc world replacement.
- For every seed, run **THREE independently physically charged no-reset 144-action trajectories**, starting from the same zero sensor state: observed-contrast, precommitted cyclic-balanced and SHA-seeded uniform-random policies. All three separately pay the **same first 96 physical actions** and get identical public consequences. Their 48 further real actions are policy-specific and MUST be performed at each copy's actual current physical state. **16×3×144 = 6,912 real charged physical source actions**; no teleportation or arbitrary-state training query. Equal paid budgets do not imply equal acquired information.
- Train identical WSP-70 source-blind numerical ReLU Stage-A residual and random-feature teachers on each world's actually paid 96 shared A public rows. At 48/96, grown signed-conjunction neurons modify real numerical hidden weights; after the 96th charge both networks freeze. Phase B policy and neural writer never import private physics source, roles, action permutations or heldout target labels.

## Frozen source-blind observed-consequence policy

For every *next* real action, derive the current state's already charged action outcomes and actual effect-signature diversity (bitwise before/after XOR) from the paid A+B ledger. Consider ONLY action channels whose B-use count is at most `(minimum B-use count + 1)` so no action channel is starved. Among them rank each candidate by the precommitted score:

```text
+12   if an OTHER action was already physically tried at this REAL state
      and the candidate state/action has NOT been charged
+ 8   if this exact real state/action has NEVER been charged
+ 4   if the action has produced >=2 distinct REAL XOR effect
      signatures on paid past states and candidate pair is uncharged
+ 4   if two previously physically tried actions at this REAL state
      produced different next states and candidate pair is uncharged
+ 2/(1 + this channel's paid B-action count)
```

Maximize the score, break ties by SHA256(seed,step,action), perform ONE real action, append its consequence. Do NOT use frozen teachers' counterfactual next states or hidden physics to choose actions; predictions are used only during subsequent neural weight learning and evaluation. The balanced control follows one seeded public four-action permutation repeated 12 times; the random control samples each of 48 actions independently. Balanced always pays 12 uses/channel, neither balance nor random selects interventions from observed consequences.

## Scientific measure of actual causal evidence

For every real visible state s and two distinct actions a≠b, count a UNIQUE action-contrast certificate only if both (s,a) and (s,b) have ACTUALLY been physically paid and produced different observable next states. Report full A-only certificates, A+B certificates and the genuinely NEW distinct certificates acquired during B. These measure paid differences between controlled interventions at the same observed state—**not** model-predicted novelty, a formal identifiability theorem, or a free counterfactual. Score actual real state/action coverage and visited states alongside contrast counts.

## Common numerical direct-weight learner and independent controls

- All three fully paid policies apply the exact unchanged WSP-74 source-blind gradientless neural `repair`: evaluate discrete ±0.5 changes in up to four existing grown ReLU sensor-coordinate coefficients, selecting top eight eligible neurons by PAID B action residual, and accept only numerically useful changes to A+B charged squared-error loss, then reset and reprogram four output readout vectors and covariance using 144 paid rank-one RLS updates. No new width, no gradients/backprop in direct candidate, no source truth or symbolic rule compiler at inference. Finite-difference loss evaluation still uses supervised paid labels and is numerical optimization.
- SAME paid observed-contrast A+B public rows: (a) readout-only full RLS no hidden edit; (b) same-capacity randomized real hidden coefficient edits and identical RLS; (c) independent exact charged-context lookup and depth-four decision tree. Both independent policy arms use the same learned A hidden representation and same direct repair method.
- Independent fully trained 8→32-ReLU→4 sigmoid neural MLP with **three deterministic Adam training restarts** on the exact same 144 paid observed-contrast A+B rows, to ≥95% exact training-side accuracy or mark conventional baseline unqualified. Record its forced and confidence-gated heldout physical prediction results, gradient update counts and whole CPU; no direct-weight superiority claim under unequal confidence or training convergence.
- Matrix-only numerical cold restore and tamper rejection for every direct model, no source/charged ledger or model-generated synthetic experience stored in inference artifact; report Stage-A known-truth retention using evaluator labels only AFTER final weights freeze.

## Frozen success/negative rules

Source evaluator-only full reachability **≥12 states in each of 16 worlds**. Primary physical heldout = **12×64=768** outcomes; separate true never physically charged context performance per arm. Primary two-action compositions = **12×32=384**. Four nested conditional challenge worlds contribute **256** separate physical heldout outcomes.

`SELFTEST_SIGNAL` requires ALL preregistered thresholds: ≥360 confident-correct physical predictions; ≥18 more than both equal-paid random and balanced; ≥15 more than SAME paid-ledger readout-only and random hidden-weight edits; ≥15 more genuinely NEW physically charged same-state action-contrast certificates in B than each random/balanced; ≥24 confidently correct genuinely NEVER paid physical contexts and ≥8 more than random; ≤24 confidently wrong primary; ≥80% previously correct/confident Stage-A retention; ≥115 two-step correct; ≤16 wrong confident on four declared negative worlds; changed hidden coefficients in ≥10 primary worlds; all 16 cold snapshot/tamper parity; whole action-selection+repair+evaluation CPU ≤6× uniform-random-policy+same-repair CPU.

**ANY failed gate => `SELFTEST_NEGATIVE_OR_INCONCLUSIVE`**. No change to seeds/source family, action scoring/eligibility, cutoff, learner, control, training budgets or thresholds after outcomes. Structural controllability is evaluator-only, not supplied to policy; source can be fully reachable even when paid action policies fail to discover those states.

## Engineering, science and authority separation

Reproduce focused: `python -m unittest discover -s research/contrib/chatgpt/WSP-76 -p 'test_*.py' -v`.

Require exact-SHA focused **Ubuntu+Windows**, generated-only **three-file source-anchored G29 code atlas**, and mandatory inherited full regression BOTH OS. Source and ledger hashes plus numeric-only model hashes and CPU cost are scientific receipts. Engineering PASS cannot prove learning, nor can a synthetic SELFTEST prove AGI, language understanding, independent open-world transfer or `SCIENTIFIC_PASS`. The existing narrow source-grammar and supervised finite-difference weight editing remain acknowledged. DRAFT/unmerged; no protected DEV/PRIMARY first use, deployment, promotion, official autonomous owner/controller/runner/scheduler changes, or paid API.

## Auditable mechanical test-harness correction before scientific scoring

The initial WSP-76 CI attempt still used WSP-75's previous `seed >= 4913` negative-cohort boundary in the *evaluator test harness* after renaming this experiment's new seed cohort to 5001–5016. That incorrectly assigned all 16 WSP-76 worlds to the four-world negative bucket and made the test fail at `primary_worlds = 0`, before printing or qualifying a WSP-76 science result. The boundary alone was corrected to the **preregistered** `seed >= 5013`. The source laws, source seeds, direct neural mechanism, action policy, charged budgets, controls, and frozen success thresholds were not changed. This mechanical repair requires the full exact-SHA requalification; no result cherry-picking or post-outcome calibration is allowed.
