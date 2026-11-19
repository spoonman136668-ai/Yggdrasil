# Checkpoint portability

The bounded replay uses the nine witness traces sealed at
`52a429cc40106b05857dcdf38338c5873c592c35`, plus their existing 1,025-witness
starting state. It inherits the original CKAD26 native and JEPA2-03 donor
pins. Each platform uses its verified local copy of the starting state.
The check creates no new source outcomes and never uses forecast results
for model selection or intervention.

The Linux phase verifies each previously recorded joint SHA-256. Each runner
then cold-restores every reconstructed checkpoint and checks the complete
witness prefix and recorded suffix. The final job requires exact native
checkpoint SHA-256, witness count, witness trace hash, head identities and
training-step counts across platforms. It compares the four heads' numeric
parameters using the unchanged JEPA source tolerance of 1e-9 absolute, and
checks the same bound for 160 probabilities per model over all permitted
paired public inputs and two-stage action combinations. It records the
individual full-checkpoint hashes and reports whether they are identical.

This keeps three distinct claims visible. Each platform can reproduce its
own joint bytes, the native learned state matches exactly across platforms,
and any specialist-only numerical differences must fit the existing bound.
The output is a verification receipt, separate from the sealed negative
results. All historical experiments, protected-source custody, qualification
decisions and deployment stay as recorded in their original sources.

The established integration workflow supplies the starting state and
model inputs. Its `Amalgam-cross-platform-replay-result` artifact carries
the comparison receipt. The two per-platform artifacts contain the detailed
replay manifests. To recheck the receipt with these manifests:

```sh
PYTHONPATH=. python -B research/contrib/chatgpt/CAUSAL-AMALGAM/checkpoint_replay_parity.py \
  compare LINUX_JSON WINDOWS_JSON EXACT_CANDIDATE_SHA
```
