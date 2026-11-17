# WSP-153 — sparse causal-operator inference, source-free development NO-GO

**Decision: `SOURCEFREE_SPARSE_OPERATOR_DEVELOPMENT_NO_GO`.** This is a deliberately isolated, source-free development experiment and not a successful native Yggdrasil learning study, scientific first-use, merge, promotion or model change.

## Custody and frozen hypothesis

- Parent WSP-151 exact qualified SHA `86595cd728c2978502f877e2cd6b61a9802e00d9`, tree `8a39159776c23aed558f164b9729b73b03896ccb`, PR #1200 (draft).
- Independent WSP-152 negative, PR #1202, SHA `47f760aef4a9b88881cdb7649a2aef42c7b9823f`, has fully passing dual-OS engineering regression. WSP-153 does **not** inherit WSP-152's failed confidence-coverage policy.
- Original prereg-only commit `304fee3e1829536d02973ac425fb214498cee09d`; corrected one mislabeled negative (3-input majority is *in* the three-term quadratic class) before any implementation or effects. Final preimplementation frozen prereg `0314e4a00be02b468b4d0ad04d98c9cb35f66570`; its history, correction and sole-path commits remain inspectable. Neither prereg was modified afterward.
- All prior WSP-149 original scientific transfer negative, WSP-151 source-free grammar and WSP-152 negative remain immutable. No protected original cohort, WSP-151 first-use, native model weights, accepted-main ref, or controller/runner/scheduler was accessed.

## Mechanism and controls

The learner receives a six-bit *do* intervention and its returned effect. Without hard-coded OR/AND/XOR names in the learner, it enumerates **1,794** candidate GF(2) algebraic laws made from up to three of 22 possible monomials (constant, six single-input and 15 pairwise input products). Charged observations eliminate inconsistent rules. It predicts only where every surviving rule agrees, otherwise abstains; an empty version space is UNKNOWN, never a forced confident answer. The active intervention policy maximizes candidate disagreement among previously uncharged contexts. Four common observations plus four own actions are the same budget as the fixed control. The exact agreement is conditional on this restricted model class, not absolute causal certainty.

Strong controls were trained or fitted using the **same eight active observed effects**: an independently implemented exact symbolic enumerator, a fully fitted six-feature binary CART-equivalent tree, and frozen WSP-151 OR/AND Bayesian inference. An independent fixed-action sparse-policy arm provides the action-selection control. All predictions were sealed before held outcomes were scored.

## Original fabricated-only diagnostic

Frozen local source-free test cohort: 16 ON-family worlds (AND2, OR2, XOR2, COMPOSE3) and four OFF-family worlds (CUBIC3, CUBIC_XOR, ODD4, EXACT2OF4), 20 distinct worlds total. Both policy arms receive eight interventions. Common uncharged held sets: **844 ON** + **210 OFF** = **1,054** outcomes.

| Policy (ON shared held = 844) | Confident correct | Confident wrong | Abstained |
|---|---:|---:|---:|
| Active sparse version space | 209 | 0 | 635 |
| Fixed-action sparse version space | 203 | 0 | 641 |
| Exact independent symbolic, same active actions | 209 | 0 | 635 |
| Fully fitted CART, same active actions | 641 | 203 | 0 |
| WSP-151 Bayesian, same active actions | 47 | 0 | 797 |

- Active ON confident coverage **24.763033%**, below frozen >=30% gate.
- Correct confident gain vs strongest same-action conventional control **−51.184834 percentage points**, below frozen +5 pp gate (strong CART predicts all held, but with 203 mistakes). Correct-only metric is not risk-adjusted; both are reported.
- Active model correctly abstained on many ambiguous in-class cases, **0 confident errors on ON**, but OFF-world **30 confidently wrong out of 210 = 14.285714%**, violating frozen <=2% gate. Confidence is *class-conditional* and not safe when the world violates model assumptions.
- Independent symbolic control **ties every exact active prediction**. The numerical enumeration does not demonstrate uniquely native learned intelligence or superiority to symbolic methods.
- Non-resource outcome SHA256 `855d323cf494becd2a884a2e740afd0f2568de83fff7e8d38c93e21835e9bda8`; per-world receipt SHA256 `6d98807a44435e6fcc717b729a47899fcb02ca6b8fdb0b6dde7d19e6140c329b`. Linux and Windows returned byte-identical digests with six source-free tests PASS each.
- Whole-process local CI fabricated scoring CPU/wall: Linux 0.35561/0.35563 s, Windows 0.50000/0.49428 s (descriptive, no energy or model-training speed claim).

**Scientific status: UNVERIFIED / no new native science.** Do not retune sparsity, threshold or action scores against this consumed fabricated cohort; any future change needs fresh preregistration, new seeds, independent source-owner custody, full controls, and fresh exact-source qualification. The falsifiable next question is how to recognize when a plausible sparse explanation is out-of-family, not simply adding more algebraic templates or turning abstentions into confident assertions.

**Qualification:** focused source-free Linux/Windows [run #44176866645](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44176866645) PASS. Final source-pinned G29 and full inherited/root regression require separate exact-source evidence. No scientific acceptance or promotion is requested.
