# Calibrate marginal contrast from public observations

Frozen executable `abeb599c668a61811c786eb7138e5499eceaf4a1`, tree `ea26fc8f964390cd3d5a04e8cb17f85a95801716`. Fresh public synthetic
worlds in two new noise families. The learner saw only receipts, with true
marginal laws concealed. The symmetric balance assumption and historical
orientation were prespecified.

**DEV_NO_GO.** Learning the marginal contrasts recovered some signal without
exceeding the independent-case drift bound. Correlated-condition Brier gain
was **0.004316** versus independence, short of 0.005. Worst independent drift
was **0.001407**, inside the 0.002 bound. These are separate pass/fail checks.

| Family | Learned-margin gain | Fixed-margin gain | Gain with true margins supplied |
|---|---:|---:|---:|
| Low contrast | 0.004655 | 0.005269 | 0.009801 |
| Unbalanced contrast strength | 0.003976 | 0.001895 | 0.005678 |

The true-margin control uses the same dependence fit and public evidence.
It exceeded the independent drift limit in both families. This rules out
blaming all null drift on a misspecified point estimate of marginal contrast.
The learner received no held outcomes for fitting. There were 13,248
simulated probes, 0.0257 s timed kernel and zero native training or evidence
admission.

## Information ceiling under the same source

For equal prior donor states and agreement 0.9 (the 0.1 case is symmetric),
let a and b be the two binomial masses at each donor count k, including the
binomial coefficient. The oracle target-shift probability is
`0.1 + 0.8*b/(a+b)`. With the true target laws this gives a probability q
for the held target outcome. The exact expected Brier gain over independence
is the sum of `(a+b)/2 * (q-0.5)^2`. It uses known evaluator parameters and
performs no source actions.

| Family | Two donor probes | Four donor probes | Eight donor probes |
|---|---:|---:|---:|
| Low contrast | 0.004758 | 0.007963 | 0.012208 |
| Unbalanced contrast strength | 0.009185 | 0.011395 | 0.012385 |

Four probes permit the frozen 0.005 criterion in this idealized model. A
retry based only on changing the transfer threshold would conflate
uncertainty in the marginal laws, uncertainty in dependence and the amount
of information actually observed. Freeze a fresh integrated comparison
with the independently fitted joint model as equivalent control and a
matched target-side diagnostic arm. The external circuit intake remains held.
