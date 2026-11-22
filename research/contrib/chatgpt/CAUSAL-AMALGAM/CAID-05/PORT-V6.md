# CAID-05 — exact-Amalgam-v6 read-only compatibility port

**Status:** STATIC_SOURCE_PIN_PASS; native Python tests **NOT RUN**; native engineering, scientific learning and deployment **UNVERIFIED**.

## Why this detached contributor branch exists

Original CAID-05 code/tests were added at detached research commit
`70f217d5d00b85e536ed5856905925bc08dec9bb`, whose own historical native
module is a **different v8 extension** (Git blob
`25191b36c3bc631bffc74fd092b0f194f40df4d1`).
That contradicts the explicit original-Amalgam-v6 source pin in its frozen
`test_native_source_blob_is_exactly_the_pinned_architecture` test.

This port copies **two byte-identical CAID-05 files only** onto the existing
PR #1329 source commit **`bbcca1d06d394a7bcfdc514f4e04bb269cb023cb`**.
No source module, weights, checkpoint, owner ref, actor, renderer, or research
controller is edited. There is no new learner/PR and no claim of scientific
improvement.

| Source identity | Exact Git blob SHA-1 | Gate |
| --- | --- | --- |
| `native_episode_experience.py` (v6) | `5a18b00a4c4131526e71f51d63dfd9eb9471c81e` | STATIC MATCH |
| `native_cumulative_learner.py` | `1bdeaa4277fc9b34bbf7c0f36c6d0a4cc00e1ca4` | STATIC MATCH |
| `native_causal_amalgam.py` | `287e6fbb9d1f9612f88f9d5ed5dda88be4bb7952` | STATIC MATCH |
| `native_history_support.py` (unchanged transfer) | `3bc68d1189c422bd3f0cbf29f570e0131bc1d12c` | STATIC MATCH |
| `test_native_history_support.py` (unchanged transfer) | `c63e94c4f3e635c0eb1bd69133977d9a55bb0cb0` | STATIC MATCH |

The two added code/test files were first staged in Git commit
`840e4cac27116349809e50d4c1ad73b7f7f519eb`.
GitHub's exact comparison to the original retention parent reports only these
two ADDED files, no native edits. This fixes the specific static source
mismatch **without** weakening the frozen pin.

## Existing native API and limits

This base carries v6 `NativeEpisodeExperience` and a default
`MAX_EPISODES=1024`; `GROWN_MAX_EPISODES=1152` is contingent on the
preexisting saturated refresh-mode parent. A separate experimental v8
extension to 2048 in the original CAID-05 detached history is **not** a
qualified feature in this v6 port. The read-only Beta public-key estimator
does not establish causal identification or additional capacity.

## Qualification not yet executed

From an isolated **exact** branch checkout with source/cold state verified:

```sh
python -m unittest discover -s research/contrib/chatgpt/CAUSAL-AMALGAM/CAID-05 -p 'test_native_history_support.py' -v
```

The suite defines 8 source-free tests and 4 real-native tests. A historical,
different-checkout report of 8/8 source-free tests is **not** an execution
receipt for this candidate. The native four (source pin, immutable observed
rows, full checkpoint cold restore, capacity/replay denials) have not been
executed here. The ChatGPT container has no GitHub network route or exact
native checkout. Do not substitute a native-shaped stub or inferred PASS.
No GitHub check contexts or exact-source CI acceptance are asserted.

After a real focused source-exact run, qualify the frozen negative controls,
interfaces, changed-candidate **full final regression on Ubuntu and Windows**,
and an independent owner acceptance if requested. This code is a
**research-only candidate** and cannot bypass original-world first-use
[owner issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426).

**ENGINEERING:** static source-pin mismatch resolved on research branch;
runtime tests UNVERIFIED.

**SCIENCE:** no new fully-trained, prospective held-out transfer, warm/cold
functional retention, or quality advantage measured.

**DEPLOYMENT:** none. `main`, PR #1278, and PR #1329 remain unchanged.
