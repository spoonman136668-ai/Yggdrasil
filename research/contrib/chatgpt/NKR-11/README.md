# NKR-11: subject-disjoint historical relation transfer

**Status:** preregistered read-only research candidate. No scientific or native acceptance asserted.

NKR-10 [PR #1140](https://github.com/spoonman136668-ai/Yggdrasil/pull/1140) induced 83 source-supported but **unvalidated** relation-composition templates from 32,768 of the previously consumed historical TRAIN facts. Independent sibling [PR #1141](https://github.com/spoonman136668-ai/Yggdrasil/pull/1141) tested **one prespecified P31/P279 relation composition**, obtaining masked recall@4 8.346%, below its 10% frozen goal, and tying its symbolic control. These are distinct trials. Do not replay or retune the sibling's consumed test.

This NKR-11 trial tests **subject-disjoint transfer of all TRAIN-mined relation templates**, not fixed P31/P279, on a broader deterministic 65,536-row historical TRAIN sample. It is a *retrospective development diagnostic* on previously consumed facts, **not genuinely fresh blind evaluation**, causal discovery, or invention of unknown semantic operators.

## Frozen protocol
Preregistration FIRST `research/contrib/chatgpt/NKR-11/prereg.json` committed before code. Exact parent NKR-10 qualified head `53c1a07c9931c0e0e334a517b7a407034028b0bc`.

- Select up to 65,536 source rows by even lexicographic index stride, no result-dependent selection. SHA256 of fixed prefix plus subject ID partitions **whole subject identities**, bucket 0 heldout DEV, buckets 1–3 TRAIN.
- Mine `(P1,P2)->P3` only from TRAIN anchor direct edge and both source-witnessed path legs; distinct subject support >=6. First eight sorted outgoing training edges per source/mid; maximum 128 templates; no absent-edge negatives.
- Independently implement a full exact symbolic set-based template fitter on the same TRAIN facts. Both learners must agree on selected keys and supports; their readout paths are separate implementations and exact prediction parity is required. The symbolic comparator is a **strongest information-matched control**, not a deliberately weak baseline.
- For every subject-disjoint heldout `(subject,P3)` group, the evaluator knows the positive source object set, while each predictor receives only `(subject,P3)`. Rule readout requests only `objects(subject,P1)` and `objects(mid,P2)` where `P1,P2 != P3`, never the hidden target object retrieval. Return highest training-support proposals, tied by stable object ID.
- Score **all** sampled heldout positive groups, including no-rule, no-path and abstentions. Report Hits@1, Hits@10 and path coverage. Compare an independent exact-symbolic prediction and fixed TRAIN-only relation-object-frequency top-10 prior; no same-subject leakage.
- Development threshold: >=64 covered groups, >=10% all-heldout Hits@10 and >=5 percentage points over the frequency prior. **Even PASS cannot imply independent scientific superiority**, because the strongest exact symbolic control is designed to tie, all source is previously consumed, and no action/consequence intervention is evaluated.

Source identity: original noncanonical historical TRAIN 21,343,681 triples, packed SHA256 `6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1`, source train SHA `2ef1a279f6393a8edfbb2b44114a2c97944272e5fe2a1bd2a7cbe48f94742f1a`. Original NKR05 artifact 14220169461 only; neither official valid/test nor protected scientific first-use.

## Qualification and authority
The GitHub-hosted lane first runs independently on Ubuntu+Windows, then regenerates only the three existing G29 atlas files from exact source, then runs mandatory entire inherited root regression and independent G29 both OS. Only if these pass does it open the *already consumed* NKR05 image for one read-only score. After source read, repeat the original root regression and retain a small source-bound result artifact (not the 256 MB image). The developer fixture never opens the actual historical image.

No merge, accepted model write, owner install, original scientific first-use, model promotion, new controller, new scheduler, self-hosted runner, paid API, causal fact claim or autonomous intelligence claim. Null outcomes stay frozen. **Genuine unfamiliar causal-law first-use, action/intervention results and a train-to-convergence conventional comparator remain separate future science.**

## Execute an authorized installed historical session
```bash
python -B research/contrib/chatgpt/NKR-11/heldout_transfer.py --installed-session /path/to/existing-pinned-session
```
