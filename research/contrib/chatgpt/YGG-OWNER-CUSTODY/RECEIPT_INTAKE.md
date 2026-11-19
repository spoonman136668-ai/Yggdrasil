# Supplemental owner checkpoint receipt intake — optional, untrusted, read-only

**Scope: integrity verification of a separately owner-supplied file bundle, NOT owner discovery or accepted training.** This follows the original YGG-LINEAGE01 owner-custody audit in [draft PR #1322](https://github.com/spoonman136668-ai/Yggdrasil/pull/1322). Source and test code remain on the separate supplemental `research/ygg-owner-native-custody-baseline-20261119` research branch to avoid overlapping writes to PR #1322 and the protected Yggdrasil owner. This is engineering preparation, not a request to run it on the workstation.

## A concrete, falsifiable next custody artifact

The existing owner audit established exactly what is missing: **actual original bytes and a trustworthy cold-restored lineage** tied to an authorized owner. Read-only GitHub metadata and published experimental checkpoints cannot fill that gap. This optional intake exposes a narrowly bounded, explicit-only directory interface for a future **independently authorized** owner to supply a candidate research checkpoint pair and source readouts. It never guesses where state is stored; never selects a private owner path; never fetches models or datasets; never starts scientific training or an external API; and never writes a checkpoint or the owner's filesystem.

The proposed owner bundle is a directory explicitly passed on the command line with `receipt.json` and these seven opaque regular files (file names literal):

| Role | Required meaning and verification |
| --- | --- |
| `prior_checkpoint` | Previous complete serialized trained checkpoint; measured full byte digest |
| `continued_checkpoint` | Post-learning serialized checkpoint; different SHA from prior |
| `cold_restored_checkpoint` | A separate already-produced cold-restored serialization with SHA exactly matching the continued checkpoint |
| `prior_source_log` | The previously pinned original append-only source ledger **bytes** |
| `continued_source_log` | Extended source log; byte-for-byte prefix identical to old source log and strictly larger |
| `prior_capability_probe` | Already-produced canonical output for a frozen previous-knowledge probe set |
| `continued_prior_capability_probe` | Canonical output for exactly the same prior probes after further learning; SHA must match previous |

For every file the receipt supplies only `{"bytes": integer, "sha256": "64 lowercase hex chars"}`; the verifier hashes and bounds the actual bytes, rejects missing/changed file contents, nonregular files and symlinks, requires strictly extending byte-prefix source history, and confirms independent cold-serialization hash equality and frozen old-probe output hash equality. The baseline source anchor is the **known protected Yggdrasil research branch**, not a claimed new accepted model:

- `repo = spoonman136668-ai/Yggdrasil`
- `branch = research/autonomy-yggdrasil-active`
- `git_sha = 92c421a5475a27015a390efb88c373eb5f15379d`
- `tree_sha = e7a9cef8a7c31fd77f086915bab7c639411ac6cc`
- `scope = research-only-candidate-integrity`
- `external_owner_acceptance = null` — it is **rejected** if self-declared accepted.

The fixed receipt schema is `yggdrasil.owner.continuation-receipt-candidate.v1` with keys `schema, source, scope, checkpoint_schema, lineage, files, old_ledger_entries, new_ledger_entries, external_owner_acceptance`. `lineage` carries parent/current checkpoint SHA256 and old/new source log SHA256. Numeric entry counts are syntactically checked but **are not parsed from opaque source records**; they must never be reported as scientifically verified counts. Any source SHA/tree drift requires a fresh owner identity check **before use**; do not relabel a new owner SHA as the same frozen baseline.

**A positive integrity result does not verify a trained model:** it merely says the user-supplied bytes and self-declared receipt internally agree. A malicious or misidentified provider could still fabricate such a bundle, the source ledger could contain inauthentic or replayed events, the cold image may not have been restored by a real independent process, and old-probe output equality alone cannot prove general retention. The emitted classification is *always* `INTEGRITY_CONSISTENT_BUT_UNTRUSTED`; fields `owner_authority`, `training_source_authenticity`, `native_learning_efficacy`, `independent_science`, `accepted_owner_state` remain `UNVERIFIED`; `deployment=NONE`.

**No automatic execution:** the explicit CLI below is documented as an interface only, not an instruction or an authorization to run on a local or remote owner. No actual private artifact was fetched or touched in this change.

```sh
python -B research/contrib/chatgpt/YGG-OWNER-CUSTODY/verify_owner_receipt_candidate.py --bundle /separately/approved/read-only/bundle
```

The GitHub-hosted qualification workflow calls **only synthetic `TemporaryDirectory` fixtures**, never this CLI with a genuine bundle and never a self-hosted owner runner. The fixtures assert self-declared owner acceptance, spoofed source refs, corrupted checkpoint, cold mismatch, original source-history rewrite, original capability regression, malformed ledger growth, duplicate JSON keys and symlink redirection all fail closed. Linux/Windows can differ on whether nonprivileged fixture symlink creation is allowed; tests skip only that specific setup when the host OS forbids the operation.

## What must happen to close the real owner-custody blocker

An independently authorized **actual Yggdrasil owner** must select the true live persistent source and approved location, confirm checkpoint source SHA/tree/owner/runner, expose a read-only exact-source source-ledger and cold-readback receipt, and establish its scientific first-use lease and old-capability baseline. A signed/trusted independent authority chain is outside this optional integrity checker. The existing NKR05 21.3m-record factual image and the CAP02→CAP03 cumulative research sidecar **cannot be substituted** without that qualification. The original [YGG-LINEAGE01 PR #1322](https://github.com/spoonman136668-ai/Yggdrasil/pull/1322) remains the canonical open owner audit; this branch only provides supplemental engineering instrumentation.

**Only after that external custodian evidence:** preregister a source-protected, truly unfamiliar causal-relationship test, matched independently trained controls, cold old-domain retention/interference, actual action utility, whole-process time/memory/compute, deterministic checkpoints and full final required-platform regression. A green receipt parser or CI is not scientific acceptance.

## Fixture qualification commands (no owner state)

```sh
python -B -m unittest discover -s research/contrib/chatgpt/YGG-OWNER-CUSTODY -p test_owner_receipt_candidate.py -v
python -B -m unittest discover -s research/contrib/chatgpt/YGG-OWNER-CUSTODY -p test_verify_readonly.py -v
```

Do not attach a checkpoint or its contents to ChatGPT, print secrets, upload private model bytes into the repo, create a new controller/schedule or replay any consumed science cohorts.
