# WSP-37 — multi-axis weight-knowledge frontier

This external **synthetic research draft** tests a broader surface in one frozen qualification instead of incrementing one Boolean gate at a time.

- Three gate arities (2, 3, 4), two function distributions (arbitrary bit tables and structured parity/threshold/multiplexer rules), and three equal-information budgets (zero, half, full): **18 scored conditions**.
- Eight compositional gates per world, 64 DEV and 256 disjoint PRIMARY worlds per arity/family.
- PRIMARY therefore covers **4,608 budget-condition evaluations across 1,536 unique worlds**, **344,064 primitive-row evaluations**, **86,016 composed-output evaluations**, and **86,016 transfer-output evaluations**.
- Directly written numeric one-hot weights are compared with converged sigmoid/BCE table training on identical probes, an exact literal lookup, and an all-zero control. Evaluator ground truth never enters acquisition.
- Negative controls: arbitrary unobserved rows, zero-budget, changed DAG composition, cold checkpoint, tamper rejection, and one-row localized repairs.
- Full-table construction is expected to tie the gradient and table arms, **not** demonstrate intelligence, unrestricted knowledge acquisition, or a defensible end-to-end cost win.

Preregistration: `prereg.json` on preceding commit `f9681f6858d992db060718b6eecdfc6f68d0510a`.

Reproduce from repository root:
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-37 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-37/battery.py --cohort DEV
python research/contrib/chatgpt/WSP-37/qualify.py
python research/contrib/chatgpt/WSP-37/battery.py --cohort PRIMARY
```

This contribution has **no merge, accepted-ref, Yggdrasil loop, FORGE, controller, runner, scheduler, deployment, or paid API authority**.
