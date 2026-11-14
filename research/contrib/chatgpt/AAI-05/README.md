# AAI-05 — Direct causal-motif learning, unfamiliar operators and cold retention

This is an isolated **external research contribution**, independently based on Yggdrasil `main`. Unlike AAI-03A/04R1, this is an actual candidate learning mechanism evaluated against strong fully trained conventional baselines, rather than another attempt to admit a synthetic benchmark by choosing difficulty.

Each world has two hidden causal rules relating six intervention bits to two consequence bits. The learner receives 16 noisy, real `do(state,action)` observations, directly edits causal motif scores, and must act on 12 states excluded from training while selecting an action to match a target consequence. The development worlds use XOR/AND and the transfer worlds OR/XNOR, with no labels or gradients for the proposed direct mechanism. The hypothesis vocabulary **is predefined** for all methods, so this is not proof of learning truly unknown physics. Training data and terminal goal are equal across arms.

Strong controls: 300-epoch logistic regression with all pairwise features; fully fit CART depth 3; exact rule-mixture Bayesian posterior over the same 60 per-bit operators; lookup; and shuffled-label negative. Every learned inference state is serialized, restored after two separate-world fits, and tested for exact prediction parity.

Preregistration was committed separately at `d417e2aff50db08d2b12af7d02ced094d17983cc`, before the evaluator was added or any scientific outcome observed. Do not tune thresholds, evaluate consumed cohorts twice, or introduce new acceptance authority.

Engineering-only preflight (reserved seed inputs):

```bash
python -B -m unittest discover -s research/contrib/chatgpt/AAI-05 -p 'test_aai05.py' -v
```

Primary evaluation (exact frozen source **once** only, outside official loop):

```bash
python -B research/contrib/chatgpt/AAI-05/run.py
```

Results, provenance, raw artifact fingerprints and cross-platform qualification live in this repository, not the user's file library. **No changes to native Yggdrasil, FORGE autonomy, model weights, controller, research loop or accepted state.**
