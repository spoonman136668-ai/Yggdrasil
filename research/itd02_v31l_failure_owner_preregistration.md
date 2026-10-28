# ITD-02 V31L — read-only inherited test failure ownership

Frozen before executable. V31K PR #634 parent `707a2baf1f5182607863667942765adea2713125`; pinned V31I and V31J full Ubuntu suites both failed the same six tests plus G29 error. No new failures attributed to V31J.

For each of the seven exact shared failing test IDs, report source path, asserted behavior, and whether it references frozen V8 native schema, native ring behavior, local credit, neighbor trace or G29 pinned code atlas. Execute original full suite on both pinned refs again only as necessary; source owner classification is determined by source test paths and failure lines, not by guessed historical root cause. Record unchanged test file hashes between V31I/V31J. Distinguish an old assertion against native v8 from proof that the native v12 schema is faulty; no source changes or test waivers. G29 requires its own acceptance rather than automatic freshness or exempting it.

This is not scientific acceptance. Preserve Q1–Q3 holdout, native-source hash and untouched V31J ring accounting. Full Windows regression remains outstanding. Classification `V31L_FAILURE_OWNER_IDENTIFIED_INHERITED_BLOCKED__NO_SCIENCE` if all seven assigned and no drift, otherwise `V31L_CUSTODY_BLOCKED__NO_SCIENCE`. No merge, G29/proxy bypass, FORGE/CKB-plane/controller change, promotion or original-world first use.
