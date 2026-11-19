# YGG-ACT01 — native four-action/four-outcome causal-cell representation

**Status: source-only native engineering candidate. No new scientific claim,
no original-world first-use, no automatic native model integration.**

Original source parent: <https://github.com/spoonman136668-ai/Yggdrasil/pull/1307>
qualified RET05 head `c3813176b5058c29b082d110dce918bd6dae1bd9`.
ACT01 frozen engineering hypothesis **before implementation** at
`bc1542e037a77cd2ca518b34cd9187f47961d85a`.

## Why this is the next gap, not another readout selector

Original `yggdrasil/public_causal_cells.py` has 16 native causal memory
addresses, but only **2** action identities and **2** observed public
outcomes. Current native episode training also uses binary actions.
This means an unfamiliar four-action motor family must currently be
mapped onto two known identities through an external adapter. The
genuinely source-trained [CKAD46 trial](https://github.com/spoonman136668-ai/Yggdrasil/pull/1309)
found that such an inferred binary mapping lost to an exact trained
Bayesian assignment control; its original development finding remains
**NO-GO**, not rescued here.

`yggdrasil/public_multiaction_cells.py` adds an **opt-in native cell
extension**, alongside and not replacing the original:
`NativeMultiActionCells`. It represents four distinct *numeric physical
actuation classes* `0..3` and four distinct *observed physical outcome
classes* `0..3` directly. These are bounded internal causal-state
integers, **not text tokens**, string-identified actions to guess,
latent source labels, or oracular semantic mappings. Original 7 active
plus 9 retained addresses persist, with 512 bytes of 16-bit bounded
categorical learned observations instead of 128.

An explicit `migrate(original_pyc1_checkpoint)` transfers all 16
original native addresses and binary 2x2 learned counts without
retraining or erasing them. The **original 164-byte PYC1 checkpoint
remains byte-exact** inside the new `YAC2` snapshot and is independently
validatable by the original `PublicCausalCells.restore`.
The original class and all its existing APIs remain completely unchanged.

Every *new* observation requires a public 64-character source digest
identity, native address, action identity, actual witnessed outcome and
active/retained slot. Duplicate identical witnesses are idempotent;
conflicting reused identities, invalid bits/types, illegal actions,
or observations beyond 256 new source receipts fail closed. The
new **versioned checkpoint** is
`4 magic + 164 original + 2 event count + 512 native counts +
36 * new events + 32 SHA-256` = **714 + 36N bytes**, with
`0 <= N <= 256`; maximum **9,930 bytes**.
These sizes are exact engineering bounds, not learning efficiency claims.

The reader supports exact multicategorical public count retrieval,
a conventional Dirichlet(1) count rational for an action with observed
evidence, and **abstains** when action evidence is absent or when
all four actions have not been independently sampled before picking
a preferred outcome. This deliberately **does not** impose unfamiliar
physical action semantics, infer unseen counterfactual outcomes, or
claim superiority over a fully fitted count/Bayesian model.

New checkpoints require an externally provided expected source SHA256
pin; cold restoration replays the original PYC1 source plus every
ordered witnessed new event and verifies the counts and exact raw
bytes. **Security limitation:** a self-consistent forged different
source tape *can be rehashed and restored if a caller also substitutes
a new trusted pin*. A digest is **not** a source-owner signature.
ACT01 explicitly tests this limitation; only an independently signed
source-owner actor/effects ledger can establish original first-use.

## Engineering and scientific verdicts are different

The new source-only mechanical unit controls cover four genuine
*representable* action and outcome identities, original PYC1 byte
preservation and continuity, exact native/retained address isolation,
cold restoration across subsequent public events, duplicate and
conflicting source receipts, 256-event budget, count saturation,
invalid-source/type failures, checksum/rehash/legacy corruption,
unseen abstention, and the source-signature trust boundary.
This is **not** new protected source training, a fresh held cohort,
transfer beyond binary, or scientific validation.

The candidate does **not yet modify accepted Yggdrasil's
`NativeEpisodeExperience`** or make the existing RET05 trained model
predict on four-action worlds. That requires a separately gated
adapter between real independently authorized 4-action source
observations, native state evolution, the new categorical causal
cells, and trained independent fully fitted controls. It should
not be sold as finished multi-action scientific integration.

Do not replay consumed CKAD46 seeds `46111/46112`, LR-92AN worlds,
RET01-RET05 scored development data, or original CausalGym worlds.
The original protected new-world source owner [#426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426)
explicitly states **NO new original protected-world first-use**.
The next scientific evaluation must first freeze genuine new
independently owner-permitted action/state identities and source
actor journals, disjoint TRAIN/VALID/HELD/TRANSFER and fully
fitted multicategorical Bayesian/Dirichlet, symbolic and recurrent
controls under matched actions/observations/compute, intervention
benefit, unfamiliar causal mechanisms, cold retention/interference
and whole-process costs.

**No controller, scheduler, new source actor, merge, accepted main
change, Forge integration, paid API or deployment. Source-only
engineering PASS must not be represented as scientific PASS.**
