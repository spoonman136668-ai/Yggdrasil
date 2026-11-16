# CVH-02 — Public-policy interface for tokenless earned-return memory

## Latest source-free endurance qualification — 2026-11-16

**Local source-exact engineering: 24/24 PASS (11 inherited CVH-01 + 13 CVH-02); no real CausalGym actions.** Added `test_mock_retention_exploratory.py` as an **exploratory post-result engineering check**, not a new preregistered science test. The actual inherited FKP-24 `public_mechanical_episode` adapter (byte-pinned Git blob `4424eadef179996ff491911efadfbe4e07761062`) drove **240 fully completed deterministic MOCK episodes for each of two policies**: one cold-restored after every episode and one uninterrupted. Both received **3,720 earned public action observations each / 7,440 mock callbacks in total**. All public transcript SHA receipts and learned checkpoints matched after every episode, all sampled online return tables matched an independently implemented conventional batch table, private info remained inaccessible, and the largest serialized closed checkpoint was **847 bytes** (not process RSS). Linux Python 3.13.5; compile PASS; exact new test Git blob `04b72bbc0100f3a3f769d42cc649df365fc62512`.

Latest evidence: `qualification_mock_retention_stress.json`; the earlier original `result.json` (9 PASS + 1 SKIP) and subsequent `qualification_exact_adapter.json` (23/23 PASS) are preserved without rewriting prior results. This extension yields **no native learning, unfamiliar causal transfer or unique algorithmic gain**; same-data conventional returns still tie.

**CI classification correction:** The latest candidate push's GitHub Actions run **#43850619624** is a zero-job **proxy-preparation workflow** whose configured push branch is `repair/ckb-research-write-proxy-fanout-r3`, **not** this CVH-02 branch. It is **not** evidence that CVH-02 root tests ran or failed. No exact-final-commit root Ubuntu/Windows regression or generated G29 qualification has been executed for this branch. The upstream FKP-25 separately qualified two-OS results cannot substitute for candidate-specific final acceptance. No new workflow, PR, runner, scheduler, controller, protected first-use, merge, deployment or paid API.

---


## Follow-up exact-source local qualification — 2026-11-16

**Latest scoped result: 12/12 CVH-02 local tests PASS (zero skips), plus inherited CVH-01 11/11 local tests PASS; combined 23/23.** The original FKP-24 `native_public_mdp.py` was fetched from the inherited private GitHub repository and **matched byte-for-byte** to original Git blob `4424eadef179996ff491911efadfbe4e07761062` (6,920 bytes, SHA-256 `ea086f70c17e203c29a8ed6183841f2c0fcfa7e735768d57793b5ba9b2a975af`). The exact **original adapter function** `public_mechanical_episode` ran against deliberately fabricated mock environments twice, completing 5 observed actions per episode. The policy received no private info, retained all 10 witnessed consequences, and the inherited 700-stream/21,231-record CVH-01 offline stress also passed locally.

The original `test_exact_fkp24_mock.py` has been changed to **fail rather than skip** when that original adapter is missing or its Git blob has drifted. Two extra source-safe negative tests pass: (1) exhaustion after two real *mock* actions cannot silently start a new episode or replay an unknown outcome—the next mock source receives **zero** `do` calls; and (2) protected seed 996500 is refused by the exact adapter **before** invoking any factory. No original CausalGym source factory, reset, or `do` was executed. The source-boundary remains mock-only.

The chronology is preserved: the existing `result.json` below records the **earlier** 9-pass/1-skip evidence without retroactive rewriting. The **newer** `qualification_exact_adapter.json` records this successful exact-adapter requalification and exact source custody. The qualified test revision is `b2a95956613401daf8539f1d0a2fcf78db3eaae3`; source policy itself remains unchanged. Mandatory exact-final-source **full Ubuntu/Windows repository regression and G29 remain UNVERIFIED**. Independent native scientific first-use, trained controls, and native admission **NOT RUN**; no merge, scheduler, controller, workflow or deployment.

---


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
