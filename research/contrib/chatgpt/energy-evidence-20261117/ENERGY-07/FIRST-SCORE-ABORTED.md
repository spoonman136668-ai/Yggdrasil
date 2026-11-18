# ENERGY-07 initial scored attempt — invalid test harness

The first frozen attempt on seeds 137, 251 and 419 terminated after the first 8 cases and before writing any scored result. A test assertion erroneously treated a guided-solver timeout solution worse than a certified exact optimum as logically impossible. That is normal on timeout, and is not an optimality violation. Exact comparison must reject a candidate strictly *better* than a certified global optimum, not a candidate worse than it. The initial cohort is retired, not treated as scored scientific evidence. The R1 corrected implementation preserves all search methods and budgets and uses fresh seeds 541, 653, 787.

Initial freeze: {
  "prereg_sha256": "07fdc0e5d10cbb626586506f200745ede0ccd2cf29abfa7441c7b379b0f83965",
  "schema": "energy07.freeze.v1",
  "scored_yet": false,
  "smoke_source_sha256": "e1b77c39725fe57243b830ca8317fff9ce8799a3c023e76aa07efd1e12ef1356",
  "source_sha256": "e1b77c39725fe57243b830ca8317fff9ce8799a3c023e76aa07efd1e12ef1356"
}

First log:

```
completed 137 24 8
Traceback (most recent call last):
  File "/mnt/data/ENERGY-07/experiment.py", line 243, in <module>
    if __name__=='__main__':main()
                            ~~~~^^
  File "/mnt/data/ENERGY-07/experiment.py", line 239, in main
    result=score((997,) if opts.smoke else SEEDS,(12,24) if opts.smoke else SIZES,2 if opts.smoke else TEST_PER_WORLD,opts.smoke)
  File "/mnt/data/ENERGY-07/experiment.py", line 213, in score
    for i in range(count):items.append(query(seed,n,i,None,factor_noise,sensor_noise,graph,smoke))
                                       ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/data/ENERGY-07/experiment.py", line 200, in query
    if xstatus and min(ea,hybrid_cost)>ex['cost']+1e-5:raise AssertionError('hybrid violates exact optimum')
                                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: hybrid violates exact optimum

```