# LR-92AC — Context-conditioned causal-memory retrieval

**Disposition: DEVELOPMENT NO-GO.** External synthetic contribution only; **not** native Yggdrasil training or official science.

## Frozen primary boundary

The exact [preregistration](prereg.json) was committed at `ec509416c1ba99f9c18419212c82646446812fd3` **before scoring**. The precursor LR-92AB raw evidence is a train-only archive, SHA-256 `c7d195a115169926988cd9ad0e369728f7fd846fc99b0814519ca90685118566`, from [PR #1257](https://github.com/spoonman136668-ai/Yggdrasil/pull/1257).

New, disjoint synthetic evaluation: seeds 929200301–303; 240 worlds (156 stationary, 36 switching, 24 foreign, 24 null); 144 fitting and 288 separate validation probes/world; 35% independent outcome noise. All models share the action/observation budgets. Past labeled stationary episodes are used for the retrieval memory; test labels cannot enter memory.

## Mechanism

Store each of 52 archived stationary episodes as its first-36-observation four-action outcome-rate feature and its posterior from 144 training probes. On a new world use the first 36 fitting observations to find the eight nearest episodes. Form a 50% uniform + 50% retrieved-episode Bayesian prior. Fit all 144 observations. Compare against uniform Bayes, global historical posterior, old learned prior, seeded random retrieval, CART and RF16.

The nearest neighbor metric, eight-neighbor count, mixing weight, training source, seeds, controls, thresholds and classification criteria were frozen in the preregistration. No postscore tuning or extra evaluation cohort.

## Result (one scored run)

| Policy | Exact stationary / 156 | False constructions | Accepted foreign/null | Heldout accuracy |
|---|---:|---:|---:|---:|
| Context retrieval (8) | 94 | 6 | 0 | 59.6875% |
| Uniform prior | 97 | 6 | 0 | 59.8958% |
| Global episodic prior | 95 | 4 | 0 | 59.7541% |
| Random episodic prior | 95 | 6 | 0 | 60.0839% |
| Old historical prior | 83 | 6 | 0 | 59.2101% |
| CART | 132 | 27 | 1 | 59.9074% |
| RF16 | 131 | 31 | 1 | 59.8900% |

The retrieval rule did not improve exact causal-rule recovery over uniform inference, global episodic memory or random retrieval. It missed three of the six preset GO checks for comparison gains and held-out accuracy (four conditions failed overall). It is a **development scientific NO-GO**, not an infrastructure failure. The conventional classifiers were not matched on Bayesian posterior acceptance, so their exact-success and false-construction tradeoffs are descriptive.

## Source, custody and reproduction

The frozen protocol and compact `result.json` and `provenance.json` are readable in this directory. The exact source is in `lr92ac_run.py.zlib.b64` (7,531-byte decoded Python), and the independent audit is in `audit_readonly.py.zlib.b64` (3,911-byte decoded Python). These are compressed solely for source custody; decode to review and run.

| Artifact | SHA-256 of decoded original |
|---|---|
| `prereg.json` | `40a8dae7fd06863e97a13e7aa8f507e8d948c267b26385d0ff664882cd142b52` |
| `lr92ac_run.py` | `67eacbba21dbb4ec14389e8c9b3c59de49793243f94917bbfaade51e77b1315c` |
| `audit_readonly.py` | `f8441c4a1d7ffdd35c6e8f87d9faa99f806f2642203704d201ced8252fd17f9d` |
| One-shot raw `primary_result.json` | `144bd2b95dc662e053a17b3f9c0392ab946b3688c7fa5ea504536cd4267dd567` |
| Independent `audit_result.json` | `7094af983d5542f086bd6a37a025a664b86316c2707f2b65cbbb506dd2ff4aad` |

For each `*.zlib.b64` Python source, decode with:

```bash
python -c "import base64,zlib,pathlib,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_text())))" lr92ac_run.py.zlib.b64
```

Repeat for the audit source. The original LR-92AB raw `result.json` must be supplied as `LR92AB_original_raw_result.json`, with its SHA-256 verified. On **a separate clean checkout** of this exact contribution, install `numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0` under Python 3.13.5; then run `python lr92ac_run.py` once. It refuses to overwrite an existing `primary_result.json`. Verify the frozen raw result SHA, then `python audit_readonly.py`. Independently authored read-only audit passed **16,629 assertions** locally. The committed summary is not a substitute for the raw primary cohort.

**Limitations:** New worlds remain within the familiar 16-table grammar; simulated foreign worlds are effectively random outcomes, not proof of genuine hidden-cause transfer. Memory collection and total end-to-end cost were not fully accounted in CPU per-policy timings. No native Yggdrasil learner, JEPA, cold persistence, outside-world transfer, first-use, official owner acceptance, full regression, or deployment was tested.

**CI caveat:** Current G29 atlas's pinned-source guard rejects newly added indexed `.json`/`.md` contribution files (`YGG_ATLAS_FAIL_CLOSED: indexed file set changed`). Repair is an independent owner-controlled source-index qualification task, not a reason to rewrite or backdate the negative scientific outcome.
