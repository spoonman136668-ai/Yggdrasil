# LINEAGE01-F — local read-only checkpoint inventory

**Problem:** GitHub alone cannot prove that the existing Yggdrasil owner has a recoverable canonical model, its original witness history, a valid source/runner lease, or retained functional competence. The official unattended model executor is disabled by policy.

**Smallest safe improvement:** `custody_probe.py` inspects a *caller-supplied local file* without importing or running a model, scheduling anything, mutating checkpoints, reading a private path automatically, or changing accepted source. It recognizes only the accepted PYC1 164-byte explicit-memory control and the existing draft `NativeCausalAmalgam` v1 envelope. It verifies basic format/integrity, counts public witnessed episodes, and emits hashes/limited metadata **only**. It deliberately cannot prove that a checkpoint belongs to the real owner, that its source history is trustworthy, that cold restored predictions match the originals, or that native/JEPA weights are source-equivalent. Those require separately authenticated owner evidence and a full native read-only restore.

Local owner usage, only by the *existing authorized owner* with the actual file path and optional independently known digest:

```text
python -B research/contrib/chatgpt/YGG-LINEAGE01/custody_probe.py --checkpoint <OWNER_CHECKPOINT_FILE> --expected-sha256 <TRUSTED_CHECKPOINT_SHA256>
```

**Do not put the original checkpoint bytes, secrets, owner-local absolute path, or raw observation ledger into a public PR or Actions artifact.** The report prints only hash identities, safe witness counts and `UNVERIFIED` authority/science fields. A caller-supplied SHA proves byte equality *against that supplied value*, not the source's legitimacy. `--expected-sha256` is optional for inventory; it must come from *independent* authenticated custody before it can support evidence. A PYC1 count file is **not** the accepted cumulative Amalgam.

Focused source-only unit tests use purely constructed fixtures, no real data, original-world actor or model. The existing LINEAGE01 GitHub workflow runs these fixtures on Linux and Windows, then a full original regression and source-atlas qualification. It **does not** run the probe on the owner's disk or perform scientific first-use.

**Owner handoff still required to close P0:** owner/runner identity and lease, source/model/config SHAs, protected source rights, authentic prior checkpoint SHA, append-only public ledger with count, read-only cold restore using actual native code, old-task predictions and memory/specialist equivalence. If any are missing, disposition is `CONTINUITY_UNVERIFIED`; **never restart or promote a new learner silently**.

**Status:** engineering fixture/test candidate until final CI; science UNVERIFIED; official training/first-use/deployment NONE.
