# Classical-energy research — preserved original evidence (ENERGY-04 through ENERGY-18)

**Status:** All 15 original evidence ZIPs have been committed byte-for-byte in [the combined archive](./ENERGY-04-18-complete-original-evidence.zip). This branch is archival only, not scientific acceptance or a merge authorization.

## Complete retained evidence

- **Combined archive:** `ENERGY-04-18-complete-original-evidence.zip`, 1,131,498 bytes, SHA-256 `21970d5c8b2b809ea6cc0f87359e13f4fc1aa09cad2679e44ee533dd681de09a`.
- Git object identity: `6bb6c8451a9e86000c391479b9945cfb778b9000`; computed independently from the local archive using `git hash-object`, then matched the GitHub-created blob object.
- 15 nested original ZIPs, including executable source, frozen protocols, scored results, model/experiment receipts and negative outcomes where those were part of the respective historical archives.
- Two additional original ZIPs remain individually stored under `original-zips/`: ENERGY-15 and ENERGY-16.
- 15 readable report copies (ENERGY-04–18) and seven preserved first-score, invalid-run or audit-failure narratives.
- Machine-readable `custody.json` records exact expected ZIP file hashes and counts for verification.

## Validate all original ZIPs

From this directory, using Python 3.11 or later:

```sh
python verify_bundle.py
```

The verifier checks the combined ZIP hash, size, CRC, exact 17-member set, all 15 original ZIP hashes and sizes, nested CRCs and member counts, and consistency with `custody.json`. It fails closed on corruption, missing evidence or inventory divergence. `verify_raw_archive.py` separately audits individually unpacked ZIP files and is **not** the default verification for this consolidated archive.

## Original ZIP fingerprints

| Gate | Original ZIP | Bytes | Nested members | SHA-256 |
|---|---|---:|---:|---|
| 04 | ENERGY-04-evidence.zip | 21379 | 8 | `ac5b3a992663d7d2c98b966e13dc1f583aca90cf62b7c7f578cbaed8f1329a14` |
| 05 | ENERGY-05-evidence.zip | 44574 | 8 | `c1971b5a7081e93b80b6462ea696fbaabc78928a1129c50a73886b9562c313b6` |
| 06 | ENERGY-06-evidence.zip | 84261 | 17 | `0994d793fec80b1cf1a3e3d21c3e32c708919bf659f3cc1ea065bb4df8a93561` |
| 07 | ENERGY-07-evidence.zip | 105502 | 38 | `2cd6e7306dd1b3248bd3ab6038a28ee8cbdb483e2fcb8e7c48c93326bc26e82f` |
| 08 | ENERGY-08-evidence.zip | 44178 | 13 | `32322c75071af5e6f8400a9370a562c4586a9efad87a5ad0a239533bc6dec765` |
| 09 | ENERGY-09-evidence.zip | 49756 | 14 | `34f344d31cc18287b39f2f5be3378635242a84b91138571cd34bed8904648519` |
| 10 | ENERGY-10-evidence.zip | 66871 | 14 | `309fe34e79d73a58a11e5691bb09d99390256ad09a3531fb4ff288fd365f151a` |
| 11 | ENERGY-11-evidence.zip | 201748 | 13 | `4339fe03a9e962defffe791c35e4e5191c26dd15d09b7cf934eb59363f6b2f67` |
| 12 | ENERGY-12-evidence.zip | 112695 | 14 | `297c0129450880cf8b7cfce6adcf33977ffe1f13012ed16e30a86f2058452682` |
| 13 | ENERGY-13-evidence.zip | 227408 | 27 | `c1ab63c0decb84b63c2624cd9642708f8e8eb618435c742b987beda4ad4361ba` |
| 14 | ENERGY-14-evidence.zip | 64138 | 17 | `fd3169eb2d14f3d5b96c4fe81e572352d4d97b9a5588b37c88647c3fb3740f45` |
| 15 | ENERGY-15-preflight.zip | 6829 | 3 | `07dfc57ef69deb7981983d80bdc90d8c404713df6b71ecbe1d056ff84a55b87f` |
| 16 | ENERGY-16-record-audit.zip | 8977 | 5 | `afc798310c82177c4ce11d35a86e0612da1be902802d1ccfeef2aa8f21213548` |
| 17 | ENERGY-17-evidence.zip | 34981 | 12 | `45791efe79d3cc51193f731d2eb3c4ca8e767e24b9cf76d5e4f7ad42e516c4d4` |
| 18 | ENERGY-18-evidence.zip | 53991 | 13 | `dabb6ae20c5aa0cd60f02990d62bd77b1e6339851671fb4d7859264007bc13c6` |

## Historical classification

The ENERGY experiments explored classical-energy consistency, inference and learned causal relationships. Several experiments found limited positive effects but repeatedly **failed** the speed/accuracy threshold against exact symbolic controls, and ENERGY-18 found a specific failure to produce branch-free paths in alternate-route mazes. These remain development observations, **not evidence of a fully trained generally intelligent model**.

- **Missing original history:** ENERGY-01 source is retained separately in [draft PR #1201](https://github.com/spoonman136668-ai/Yggdrasil/pull/1201); original ENERGY-02 and ENERGY-03 packages remain unavailable. The combined archive deliberately starts at ENERGY-04.
- No new training, experimental scoring or native Yggdrasil first-use took place when archiving this evidence.
- GitHub branch: `research/archive/energy-evidence-20261117`; original main/base: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Engineering CI and native scientific acceptance remain separate; this archive is not promoted or deployed.

## Follow-on standalone mathematical gate

[ENERGY-19: counterexample to single-witness energy action choice](./ENERGY-19/REPORT.md) is a separate exact-rational safety test, **not included** in the frozen ENERGY-04–18 original bundle. It concludes that choosing a single optimistic low-energy future can lose expected reward versus correct state marginalization. No training, scientific promotion or original Yggdrasil first-use.
