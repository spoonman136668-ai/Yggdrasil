# CAP04 public Git source-reference preflight — no owner entropy access

This additive, read-only engineering gate pins the already fully qualified v2 source candidate `5d6a04843c53507b316d94993faafcf08dc04afc` (tree `571cdb44c17cedb0ef6aa35bac9c0a198ae4760a`) and checks **actual Git content** rather than accepting arbitrary caller-provided 40-character strings.

The preflight checks the original source v2 Git blob `fd42459ba94210c97c94b6cf816ac38d7587c26f`, original CAP04 prereg Git blob `1d79e222685ea1a6889bff49e5bf405a9aed9580`, CAP03 original source blob `d5a3fc30846ebbb97eeb8817fc72d9cd5be8c181`, immutable prereg freeze commit `1faf84d4a62f16da2ee4ef5f1c7464eb76bab39c`, repo HEAD ancestry and worktree bytes. The original CAP04 protected seed roster, 96-step/three-phase budget, parent accepted main and `scientific_first_use_not_authorized` flag must match.

The returned JSON explicitly says `PUBLIC_SOURCE_REF_VERIFIED_ONLY`, `registered_first_use_authorized=false`, `private_entropy_custody_verified=false`, and `owner_source_key_uniqueness_verified=false`. The API rejects any attempted conversion of this public receipt into first-use authority, and unit tests exercise malformed SHA, wrong tree, wrong source/prereg blobs, wrong root, and forged approval flags.

**This is not a private-entropy ledger.** Read-only public Git verification cannot establish that a future secret has 256 bits of unpredictability, is unique across sources, is privately stored and access-controlled, or is hidden from learners. No secret values, real first-use requests, protected registered seed scoring or training are performed. The owner must qualify those separately before first use; no process in this branch opens or resumes training.

The active PR #1324 and accepted main remain untouched. The earlier v2 source, original native and all six trained JEPA heads remain byte-identical. Further adoption requires source-only G29 reanchor, exact candidate dual-platform regression, source-owner approval of the protected custody interface, and frozen comparison controls.
