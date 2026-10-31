# MG93-AL — fixed-horizon teacher action-entropy falsification

Classification: RETROSPECTIVE EXPLORATORY ASSOCIATION, NOT CAUSAL.

## Immutable input and exact source execution

- Original workflow run: `41047254253`
- Artifact: `12972852607`
- Artifact ZIP SHA-256: `9f284ce2b793a2f6e0d0d8a1cb097efb5a9e5ce9b5d75f5c53a77f8474d0104a`
- `heldout.json` SHA-256: `0cdb155ce150717c3a678f6c536a81f5f4203dd96acafee459b2fdc1d2a36427`
- Diagnostic source commit: `a1f6a6bae16f53e7b8c310311f6d24f72cca1013`
- Diagnostic source Git blob: `e599d8007500237e0fb87807a4e7fbc090707632`
- Diagnostic source raw SHA-256: `c4566ca3a450d844c54ec05cc4a163a7329a54776042877b4caa931b3a6d162e`
- Result JSON SHA-256: `20a08640e94c95a4b9c7a4fec37bdd0820c0e164f93aa1430b6b1e43ad73e8dd`

The exact GitHub-fetched diagnostic source blob was executed against the hash-verified original ZIP. No environment was reset or stepped; no model was trained or altered.

## Result

Only the frozen hand-coded MG86 teacher role was analyzed: 12 episodes, 10 terminal successes, 2 failures, across four task families.

| Prefix | Fixed horizon for all? | AUC of action entropy ranking terminal success | Interpretation |
|---|---|---:|---|
| 8 actions | Yes | 0.725 | Weak descriptive ranking |
| 16 actions | No; one episode terminated at 14 | 0.950 | Outcome-dependent termination contaminates comparison |
| 32 actions | No; multiple successes terminated before 32 | 1.000 | Strongly contaminated by variable episode duration |

At the only uniform horizon, the successful episodes had mean action entropy 1.786 bits; failed episodes 1.383 bits. The two failures are one in KeyCorridor S3R2 and one in KeyCorridor S4R3. The descriptive unstratified label-reallocation reference at eight actions is 0.197, but is **not a valid inferential p-value**: the sample is tiny, failures are clustered across families, and it was not a randomized/exchangeable design.

## Decision

**Do not optimize action entropy.** The clean common eight-action prefix gives only weak rank discrimination (AUC 0.725). The apparently excellent 16/32-step metrics are confounded because successful episodes terminate sooner, making later windows outcome-dependent. The hand-coded teacher is not an equally trained conventional baseline. There are no unselected action outcomes or intervention-based causal contrasts.

This diagnostic does not support an entropy bonus, novelty objective, native learned mechanism, or policy change. The next valid positive claim requires prospectively frozen, independently sourced cohorts and actual terminal task outcomes under matched controls; original first-use remains blocked by the independent FSA authority gate.

## Evidence files

- `teacher_prefix_entropy_diagnostic.py` — exact source diagnostic.
- `teacher_prefix_entropy_execution.json` — machine-readable summary and caveats.
- `teacher_prefix_entropy_execution.md` — this receipt.
