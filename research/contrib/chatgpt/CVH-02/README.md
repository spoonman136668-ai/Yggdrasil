# CVH-02 — Public-policy interface for tokenless earned-return memory

**Local SOURCE-FREE engineering: 9 tests PASS, 1 exact original FKP-24 adapter test SKIPPED; engineering acceptance UNVERIFIED. Scientific transfer/learning NOT RUN.**

CVH-01 learned finite four-step future **observed** reward returns, but had no complete policy that an action/consequence source could drive. CVH-02 provides a narrow `choose(binary_public_state, tuple_of_public_events)` and `observe(six_field_public_event)` wrapper compatible in shape with the qualified FKP-24 [source-safe public-only interface](https://github.com/spoonman136668-ai/Yggdrasil/pull/1120). It does not import CausalGym, instantiate a source, invoke `do`, call a private oracle, or consume any original-source seed.

## Frozen scope and implementation

- Accepted Yggdrasil `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; exact CVH-01 isolated parent `140ea46403cb506c9e6b75d1da65c5f9676cc850`; inherited FKP-24 source blob `4424eadef179996ff491911efadfbe4e07761062`. Preregistration FIRST: `834bae4b9afeca77849c6de71789b2c852246c17`.
- One new source file, `public_policy.py`, composed of existing CVH-01 `EarnedReturnMemory`. It selects an action from public support-conditioned four-step earned-return means **only when both actions have at least two complete samples**. Otherwise it deterministically explores the less-attempted public action. It neither trains on unseen outcomes nor predicts hidden source labels.
- Strict history equality checks reject missing, reordered, extra-private-field, nonbinary and stale public records. Every `choose` opens exactly one pending action; `observe` must match the source-observed state/action to commit memory. A second `choose` before the public consequence, or an unexpected `observe`, **fails closed** with no memory mutation. No uncertain-effect replay.
- A genuinely source-reported termination or truncation flushes CVH-01's pending consequence trace and allows retaining accumulated learning across subsequent independently completed episodes. If an episode simply exhausts the caller's action budget **without an observed source-terminal flag**, the wrapper refuses a fresh reset rather than invent an end-of-episode reward or mix experiences.
- Snapshots include all inherited numeric memory, learned action attempts, public current-episode history and a canonical SHA-256 checksum. Restoring after a fully observed action can continue on the **same still-live mock source session**; snapshotting an outstanding unobserved action is forbidden. The digest is corruption detection, not authenticated provenance.

## Source-free measured proof

The **9/9 locally executable mock tests pass** on Linux CPython 3.13.5. They exercise two completed mock episodes and ten public chose/observed actions; all online counts and earned returns exactly match the independent conventional batch return-to-go estimator, with nine supported context keys. After completing those two mock episodes the saved policy checkpoint is **781 bytes**, SHA-256 `0c10281e32d7a4372b86dd8e4887380caec16eb2e68d2e13b5bfd7e0842225e6`. Cold restored policies make identical subsequent public-only decisions; invalid records, forged private fields, ambiguous episode boundary, source action mismatch and tampered/semantically invalid snapshots are refused.

**Critical missing qualification:** The special test `test_exact_fkp24_mock.py` requires the original inherited `FKP-24/native_public_mdp.py` blob **exactly** `4424eadef179996ff491911efadfbe4e07761062` and drives its real `public_mechanical_episode` function **only against a dummy mock with forbidden private info**. The ephemeral local runtime has only a **165-byte stand-in with PublicConsequence's six-field type**, so this exact-source test was correctly **SKIPPED (1)**. It is included for independent execution in a complete exact-source GitHub checkout. Neither original adapter integration nor cross-platform final CI is claimed PASS.

From an actual checkout:

```bash
cd research/contrib/chatgpt/CVH-02
python -m compileall -q .
python -m unittest discover -p 'test_*.py' -v
```

Source byte receipts of all three new Python files match the locally executed content and GitHub exact blobs in `provenance.json`. The original FKP-24 module remains inherited and unmodified. No new workflow or PR was created, and existing FKP-25 [#1122](https://github.com/spoonman136668-ai/Yggdrasil/pull/1122) and independently trained WSP-121 [#1121](https://github.com/spoonman136668-ai/Yggdrasil/pull/1121) owners are untouched.

**Engineering status:** Source-free mock policy lifecycle PASS; original FKP-24 byte-pinned mock integration **UNVERIFIED**, mandatory exact-candidate full Ubuntu/Windows root regression and G29 **UNVERIFIED**. **Scientific:** No real native CausalGym original actions, training/transfer, long-horizon causal planning, fully trained baseline superiority or whole-process efficiency proof. Existing CVH-01 conventional exact table ties. `scientific_pass=false`, native admission **NONE**. The following independent challenge remains source-owner-approved original action-consequence training with disjoint held transfer, conventional trained controls and matched cost, not simply passing more mocks.
