# Gate 13 pre-analysis freeze — hidden-family intervention-rank identifiability

**Status:** source-free mathematics only; **no original-world source actions, no trained model update, no new held outcomes, no scientific PASS**. This is a *separate, append-only design qualification* of the earlier `action_identifiability_prereg.json`, whose Git blob `f6b9a8d54b3ef7645ab091d796ce3a71301380f6` must remain unchanged.

## Question and predeclared finding to check

The earlier design requires two actions with different old-vs-new Jensen–Shannon information and at least one family where each action wins. But those rankings come from an **evaluator-only** table that the causal learner must not see. It is possible for two latent families to have opposite oracle-best probes **while all public observations before the first choice are bit-identical**. Rank reversal *alone* does not establish a policy can condition on family or select better than a fixed probe.

**Fixed complete two-family counterexample** (no simulator, sampling, model weights or source actor):

- `R` is a hidden binary old/new causal regime with equal prior 1/2. `F` is a hidden source family A/B with equal prior 1/2, independent of `R`. No public initial observation distinguishes A from B.
- In family A, action `a0` has `P(Y=1|R=old)=1/10`, `P(Y=1|R=new)=9/10`; `a1` gives `1/2` in both regimes.
- In family B, reverse the action roles: `a0` gives `1/2` in both regimes; `a1` gives `1/10,9/10` under old,new.
- `Y` is one binary next observation; choice is made **before** seeing the family's identity or the response. All conditional outcome laws are *evaluator-only*, not permissible native inputs.

Evaluate natural-log information about the **regime only**, not the joint pair `(R,F)`.

- Conditional source-knowing oracle gets `I(R;Y|a*(F),F)=JS(Bern(1/10),Bern(9/10)) = 0.3680642071684971` nats per one observation.
- For either blind first action, the mixture over unobserved `F` is `P(Y=1|R=old,a)=3/10`, `P(Y=1|R=new,a)=7/10`; `I(R;Y|a)=JS(Bern(3/10),Bern(7/10))=0.08228287850505178` nats. Both available actions tie exactly.
- Thus even though the evaluator's two family-specific *oracle* action ranks reverse, a source-blind policy with identical initial public histories has **zero first-action selection advantage over fixed choice/random** in expectation. This does **not** prohibit later adaptation after legitimately informative observations, and it does not prove the native architecture cannot learn; it refutes using oracle rank reversal as evidence of available **initial** decision knowledge.
- Do **not** compare `I(R;Y|a,F)` (which conditions on unobserved `F`) with `I(R;Y|a)` as if both were matched-information policy arms. The oracle is a privileged evaluator ceiling only.

## Frozen implementation/review checks

1. Create a *pure* evaluator-side helper that computes both rank vectors and the source-blind regime information after correctly marginalizing unobserved family. Use exact rational input and numeric entropy only at the final evaluation. No sampling, source calls, integration with the native planner, model training, policy updates, source first-use or new scheduler.
2. Source-free negative fixtures verify this two-family symmetry, the two distinct information scopes, no ability to infer public family distinguishability from hidden family labels, and rejection of malformed probability/family prior data. At least one positive asymmetrical example should show the helper can resolve genuine blind action information differences rather than always printing a tie.
3. The existing v1 audit can continue to compute **evaluator-only source suitability**, but its rank reversal must never be called **learner-observable conditional intervention value**. Add explicit flags to its output if needed; do not change frozen v1 thresholds or automatically grant scientific eligibility.
4. For any later *source-owner-approved* disjoint real experiment, establish a **prospectively logged public-prefix mechanism/rank cue** that can be inferred without oracle family labels, and compare policy vs fixed/random and *fully trained active Bayesian* from identical permitted prior observations/action budgets. Separately log first-probe information, later adaptation, realized reward and cold retention. The owner must authenticate novel family, license and first-use lease under [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426).
5. Exact-source Python regression on Linux and Windows, source-pinned G29 check and required inherited native/JEPA checkpoint replay and cross-platform parity are mandatory for an engineering PASS; prior CI is historical only. Preserve failure receipts and don't make a scientific claim from synthetic mathematical checks.

**Authority and isolation:** Original amalgam Work [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), cumulative checkpoints, existing actor and source-owner issue #426 remain untouched. Existing code is shadow-only, PR #1326 remains draft/unmerged, and the current owner expressly denies original-world first-use. No scheduled or recurring work.
