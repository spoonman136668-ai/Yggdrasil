# DWSA-27 — pretrained predictor identity guard

**Engineering only.** DWSA-25 found that two different Git checkpoint archives (`maze_v1.npz`, `maze_temporal.npz`) had exactly the same learned predictor matrices and biases. Counting file hashes as distinct donors overstated model independence.

This Python 3 standard-library tool fingerprints the four actual trained predictor tensors from the original MIT-licensed `OpenSourceRulesz/tiny-jepa@612b2afa28bc1e05c95ec078f7a4f30fb5fad303`, without importing the donor, evaluating its neural model or running an environment.

It reports both original complete-file Git blob SHA-1 and canonical predictor-only SHA-256, along with each matrix digest. It refuses malformed ZIP/NPY arrays, incompatible shapes, nonfinite values, bad source pins and duplicate predictor cohorts when `--require-distinct` is specified.

On already-acquired, pinned checkpoint files:

```bash
python research/contrib/chatgpt/DWSA-27/predictor_identity.py --require-distinct \
  --expected-blob maze_v1.npz=88def290b67b29087aaed60c79189472c7b472d3 \
  --expected-blob maze_temporal.npz=2031e8ae2eabf944fada94fe1f1d7738e23cb9d2 \
  maze_v1.npz maze_temporal.npz
```

Exit 2 = duplicate predictor. Exit 3 = source validation rejected. Exit 0 = distinct predictor tensors in the provided files; **it does not imply independent trained capabilities or a scientific gain**.

The seven tests use fabricated arrays, no source actions, and run in the existing root Python test discovery on Linux and Windows:

```bash
python -B -m unittest discover -s tests -p 'test_dwsa27_predictor_identity.py' -v
```

Frozen source evidence: [DWSA-25 preregistration](https://github.com/spoonman136668-ai/Yggdrasil/pull/1347#issuecomment-7052970165) and [negative result with matching predictor tensors](https://github.com/spoonman136668-ai/Yggdrasil/pull/1347#issuecomment-7052997676). Protected first use remains denied at [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426). The guard is contributor-only; it changes no native model, trainer, controller, workflow, experimental threshold or source-first-use permission.
