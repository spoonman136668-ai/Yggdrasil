# CAP04 v2 source-identity and commitment binding — scope-limited repair

This adds a focused **source-collision negative control** to the isolated v2 engineering source protocol. It inherits the source-only G29-qualified v2 candidate `3992e4aa72410c51536179e863f166310cd88a34` and does **not** overwrite the active CAP04 PR or the independent alternative research branches.

## Original verified failure

The initial v2 used a secret entropy value without the source identity in the HMAC key derivation. Two different fixture labels supplied the **same entropy** produced identical actions, source worlds and event IDs. This was independently detected at [PR #1324 review](https://github.com/spoonman136668-ai/Yggdrasil/pull/1324#issuecomment-7015258018). The initial focused/atlas tests did not test cross-source secret reuse. That is an engineering source-custody **FAIL** for initial v2, irrespective of its passing unchanged-code regression.

## Minimal repair

- Every action-shuffle, witness-ID and private-world HMAC role derives from **(source_label, entropy, role)**. A changed public source identity changes all three derived keys even if the same input bytes are accidentally reused.
- The proposed source-only commitment now binds `source_label`, an **externally verified, exact 40-hex Git source tree SHA**, the frozen `prereg.json` Git blob SHA, and the private entropy. All inputs are domain-separated; the secret itself is never serialized or returned.
- A new negative regression repeats the original failure condition using **identical deliberately public engineering entropy** in both fixture identities, proving the revised public tapes, action keys, event IDs and commitments differ. Separate tests reject wrong refs, unknown source identities and all seven protected registered first-use requests.
- The secret entropy **must still be independently generated using an approved CSPRNG and privately stored uniquely per protected source**, with a permissioned uniqueness ledger. Domain separation does NOT verify randomness or prevent key reuse. A user-supplied Git hash is not automatically an authenticated source: project owner must pin/validate it at first-use.

## Scientific and authority fence

The existing `generate_registered` function remains unconditionally disabled. Neither real entropy nor any reserved DEV/pilot/primary source has been generated or scored. Public engineering keys are nonsecret and never qualify cryptographic secrecy. This candidate remains an engineering fixture until independent full source-exact two-OS regression and separate source-owner first-use custody checks. No native/JEPA model restart, Forge, scheduled task, runner, acceptance or deployment change.
