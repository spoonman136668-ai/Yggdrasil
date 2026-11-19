# CAP04 v2 proposed keyed source protocol — first-use LOCKED

This branch introduces an **isolated engineering-only v2 source-protocol candidate**. No registered DEV/pilot/primary source has been generated, trained, scored, or activated. The existing v1 source and previous 494-test qualification remain untouched.

## Threat corrected

The prior publicly enumerable \`SHA256(identity, time)\` witness IDs exposed a small set of source identifiers, potentially recovering the known per-source action schedule without learning past interventions. The fixed public 16-step action pattern also permitted absolute clock to reconstruct previous interventions. A source fixture may appear history-dependent while allowing these shortcuts.

## v2 boundary

The protocol accepts a source-only 32-byte entropy value, **which the owner must generate with an approved CSPRNG, uniquely per protected source, and hold in permissioned private custody**. Length checks do not prove entropy quality. Domain-separated HMAC-SHA256 derives independent action-shuffle, witness-ID and private-world keys. Source events expose only \`id, views, action, s2, y, post\`. A witness ID is a secret-keyed HMAC, **not** SHA256 of a known seed/fixture/time. Each four-event action block is selected with unbiased PRF rejection sampling, independent of any target, private world state, phase, learned model or downstream action choice. A public commitment binds exact secret material; the secret itself must not be committed, logged or passed to the learner.

**The existing registered first-use entrypoint explicitly refuses every 99917/99931 DEV, pilot and primary seed even if passed an entropy value.** There is no live original-science unlock, controller, or runner. The only callable generation path is for two synthetic engineering fixture identities, with **intentionally public, low-entropy sample keys** in its tests. Those values make no security claim: public fixture keys can always be enumerated. The relevant engineering tests instead verify the HMAC key interface, key-domain separation, no public identity strings, strict chronology, action balance, deterministic cold reconstruction, negative-input rejection, and that the source owner cannot accidentally call a registered generator via this module.

### Remaining separate gates

1. Source owner independently verifies 256 bits of real unpredictability, protected entropy custody and pre-first-use commitment without secret exposure.
2. Independent audit rejects oracle recovery from public witness IDs, timestamp, known source set or any exposed seed/identity, **with a secret that is never exposed to the learner**. Enforce branch/SHA and protocol v2 version custody.
3. Reconcile the independently qualified clock/source-ID controls and the full original CAP04 native + six JEPA comparison. Control information, action budgets and compute must match. Requalify exact SHA/tree, G29 and final Ubuntu/Windows regression after reconciliation.
4. Registered source-first-use requires a distinct authorized owner gate, preregistered unchanged controls, preserved cumulative trained weights and functional historical readout. A synthetic engineering pass is **not** scientific evidence.

A public hash commitment cannot certify secret entropy quality, absence of downstream information leakage, or independence of a science source from the learner. Scientific first-use remains **UNVERIFIED and prohibited here**.
