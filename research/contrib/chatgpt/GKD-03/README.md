# GKD-03 — GPT donor, unique causal witness identities, and non-identifiable worlds

**Research-only synthetic development, not native Yggdrasil learning or trusted live source intake.** The GPT donor from GKD-01 supplied an ideal thermal cause/effect rule. GKD-02 showed correction from observations but accepted the exact same observation twice as two independent confirmations. This successor freezes replay, evidence-custody, and indistinguishability experiments in [prereg.json](prereg.json).

**Preregistration FIRST:** `88c466ee61204ee85f2b7cc93fd56a9baa258167`. **Accepted main before project:** `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Earlier GKD-01–02 qualified source and results remain unchanged in draft [PR #1348](https://github.com/spoonman136668-ai/Yggdrasil/pull/1348).

## Mechanism and exact limitations

This standalone test uses an Ed25519 **publicly known test-only fixture signing seed**. An event's signed canonical payload carries issuer, stable physical event ID, context, numerical inputs and observed effect. The candidate verifies the test signature; a 16-slot bounded ledger stores 32-byte source-event ID hashes and distinct 32-byte payload hashes, preventing an exact replay from increasing evidence counts or an altered event from silently occupying the same ID. Signatures made with the publicly embedded test key **cannot authenticate any real physical observation**. The test does **not** address colluding issuers, forged source authority, renamed physical events or proof of world identity.

The candidate's fixed **1,140-byte** checkpoint includes four context-local numeric correction states, a finite event fingerprint ledger, header and SHA256 integrity check. It cannot acquire new knowledge if slots are exhausted, and digest protection is **not** a cryptographic author signature of persisted state. An identical previously observed event is idempotent; a signed altered payload using the same source-event identity raises an error without updating native knowledge.

The separate unfamiliar-law check constructs **16 matched pairs** with identical observations at voltage 4 and 18: one world has constant thermal efficiency, the other has an added quadratic term that vanishes at the observed voltages. This creates a genuine identifiability barrier for the *fixture* even if all initial observations are accurate. The candidate abstains because the supplied two-feature basis [1,(V-4)(V-18)] is rank-deficient after those observations. A third distinguishing intervention at V=11 permits **within-supplied-grammar** two-parameter learning. Compare heldout voltages V=7,15 against independent exact symbolic algebra and conventional fully fitted two-feature OLS on exactly the same three observations.

**No new unknown primitive or general causal mechanism is discovered:** the quadratic feature itself is preprogrammed. The paired-world prior impossibility is a structural bound, not independent real-world transfer.

## Qualification and reproducibility

After exact-source qualification: `node research/contrib/chatgpt/GKD-03/run.mjs`.

Frozen 32 known-family worlds require 320 distinct admitted signed event IDs, 800 duplicate replay ignores, 32 signed event-ID conflicts rejected, 32 unsigned/altered-signature source rejections, 32 local repairs without other-context damage, 64 cold restorations and a 1,140-byte checkpoint. The 16 paired ambiguous worlds require 32 preprobe abstentions and 64 correct postprobe predictions tying exact symbolic and fully fitted OLS controls. The old GKD-02 naive learner serves as a replay-hazard negative, not an independently trained comparator.

Any favorable numerical score is **ENGINEERING DEV only** until full exact-head Linux/Windows tests, source atlas, real source custody, independent novel-world controls and an authorized owner qualify further use. **SCIENTIFIC_PASS=false, native integration=NONE, no first-use protected CausalGym action**. The Unified Causal Intelligence Amalgam Work chat remains the only learner-integration coordinator.
