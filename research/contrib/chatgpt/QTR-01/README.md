# QTR-01 — Qwen3.8 representation donor intake (external research, draft)

**ENGINEERING:** source-identification stage only; **SCIENTIFIC:** UNVERIFIED; **DEPLOYMENT:** NONE.

**Plain English:** We can inspect existing, publicly licensed measurements from an open-weight Qwen model without running Qwen. The measurements are *not* a semantically labeled knowledge map. Nothing has been transplanted into Yggdrasil, Wingless, or TTT-Hybrid.

## What was selected

See `donor_sources.json` for pinned source repository revisions and scope.

- General atlas: 64 text layers; structural feature and coactivation tables. The coactivation field is a correlation, not a causal or semantic assertion. The atlas author corrected/retracted corporate-versus-authentic and overinterpreted near-ceiling classifier claims; these are excluded.
- Separate code SAE: all 64 decoder layers; score/feature-list subsets can support a narrow coding-domain read-only investigation. Feature indices are not interoperable with the atlas by default.

Both source repositories publicly declare Apache-2.0. Source model weights revision at capture, underlying artifact byte hashes, feature semantics and independent replication are **not yet verified**. No data binaries are vendored into this repository.

## Admission boundary

The two third-party sources cannot be treated as transplantable weight-edit vectors simply because they cover the same model family. Before any true representation transplant, an independent recipient-native experiment must acquire **(1)** a verifiable concept/behavior interpretation; **(2)** an identifiable source-to-recipient interface; **(3)** paired, blinded tests of feature intervention and counterfactual prediction; and **(4)** a frozen, disjoint evaluation with matched controls.

### Permitted preflight

1. Read bounded source metadata/score tables from the **pinned revisions**, verify exact file hashes and schema, and archive the provenance in the future preregistration.
2. Exclude invalid atlas tables and distinguish source metadata/taxonomy from verified semantic labels.
3. Audit whether any public score, feature sample, or interpretation can be tied to a independently verifiable *causal* relation; do not infer it from high correlation.
4. Only then preregister a QTR-01 primary experiment against each recipient's native state; freeze donor/split/seeds/costs/negative controls/baselines and success/stop rules before first-use.
5. Measure novelty transfer, cold retention, interference, intervention value, and whole-process cost. Report no improvement if it only memorizes examples or ties equal-budget baselines.

**No donor inference, paid API, recipient weight edits, model integration, official research-loop execution, hidden-label access, merge, deployment, new scheduler, or promotion is authorized by this intake.** Do not consume WSP-99 public/reserved worlds or disturb PR #1030.

## Isolated lineage

- Parent: Yggdrasil WSP-99 candidate `ccb8692317c74db71f0f7b8f62fed21a2040ed2a` (draft PR #1030).
- QTR-01 is a separate source-intake branch and must not alter WSP-99's preregistration, result, or acceptance claims.
- A new scientific preregistration must be committed *before* inspecting any primary held-out outcome.
