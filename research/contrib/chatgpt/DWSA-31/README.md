# DWSA-31 — immutable pretrained checkpoint custody with no pickle execution

**Purpose:** safely inspect the real original publicly released TD-MPC2 `mt30-1M.pt` checkpoint (official Hugging Face source) as **opaque bytes**, verifying original file size and SHA-256 and statically parsing its ZIP/pickle *opcodes*. This **does not** train, infer with, deserialize, compile, extract or integrate any model. It does not exercise a protected causal environment.

**Original repository source:** [nicklashansen/tdmpc2@332f19e4aba4bffe2dc736f45ea7f7bdc585903a](https://github.com/nicklashansen/tdmpc2/tree/332f19e4aba4bffe2dc736f45ea7f7bdc585903a), MIT license; pretrained checkpoint [official Hugging Face immutable source `0d1dfdda7e529f6d3f942787ce2825eccad38935`](https://huggingface.co/nicklashansen/tdmpc2/tree/0d1dfdda7e529f6d3f942787ce2825eccad38935/multitask).

The official LFS pointer states **exact original byte size 7,956,767** and **SHA-256 `40c3eac2ac86d73c5931536dcf6d65b341f17524d5be74ca97d6e4d9d0f9c56e`**. Hugging Face marks its pickle imports unsafe. Original TDMPC2's `load` uses `torch.load(weights_only=False)`; **NEVER invoke it on this downloaded checkpoint**.

`checkpoint_scan.py` uses Python 3.12 standard library only. It verifies byte identity first, rejects duplicate/unsafe ZIP members, unknown pickle layouts, oversized payloads, hidden trailing bytes, and opaque pickle extension opcodes. It lists statically declared globals and storage entry counts. `pickletools.genops` **does not interpret or execute** pickle operations. It never calls `pickle.load(s)`, `torch.load`, imports OmegaConf, or converts storage entries to tensors.

On a *separately acquired exact pinned file*:

```sh
python research/contrib/chatgpt/DWSA-31/checkpoint_scan.py mt30-1M.pt
python -B -m unittest discover -s tests -p 'test_dwsa31_checkpoint_scan.py' -v
```

The existing DWSA-06 branch-only hosted workflow downloads public checkpoint once per OS with a strict 16 MiB streaming cap into job temporary storage, and reports only bounded static receipt JSON. Download or byte mismatch **fails closed**, does not turn into scientific negative. Workflow GitHub permissions remain read-only. No paid API is used.

**Acceptance boundary:** Original checkpoint bytes verified and ZIP/pickle metadata inspected = *engineering-only source-custody pass*; synthetically generated adversarial fixtures = *focused test pass*. Neither means **learned weights have been extracted**, pretrained dynamics have been assimilated into a recipient, unfamiliar-world transfer measured, or scientific gain verified. Protected novel original-world first use remains disallowed under [Yggdrasil source owner #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426). Draft [contributor PR #1347](https://github.com/spoonman136668-ai/Yggdrasil/pull/1347) must remain unmerged unless independently accepted as engineering evidence and never as model-improvement proof.
