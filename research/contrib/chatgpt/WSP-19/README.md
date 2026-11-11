# WSP-19: whole-process cost of direct compilation versus training

This is a resource-accounting experiment. WSP15/16's internal construction failures are preserved; the compiled arm explicitly uses the working WSP14 external exact synthesizer. It compares that compiled numeric circuit with the same exact symbolic evaluator and two genuinely converged conventional models: an eight-logit Adam learner and a41-scalar3-8-1 tanh MLP.

All32 five-label signatures, three fixed repeat seeds, all construction/search/catalog and checkpoint/restore costs, and1/32/1024 raw-context queries per task are counted. All methods must fit every exposed label; hidden uniformly arbitrary labels remain unidentifiable. Tracemalloc is enabled for construction and custody on every arm; its overhead is included and disclosed. Inference is untraced. A construction is measured once, then charged to each declared workload projection; this is not three separate construction executions. Actual assay elapsed time is reported separately.

The frozen efficiency hypothesis requires a2x advantage over the faster converged trained control at EVERY declared workload, not a selected favorable point. Exact symbolic cost is also reported and cannot be omitted. Different representations/priors/capacities and Python overhead prevent a universal hardware/energy claim. There is no protected independent scientific first-use or scientific superiority claim.

Remote preregistration `a5c12300c29f0db9cffd973ba3a288009b42d51a` preceded all implementation and primary outcomes. WSP18 composition is explicitly deferred because acquisition remains deficient; the handoff prioritizes whole-process cost. No WSP18 experiment is claimed.

`python -m unittest discover -s research/contrib/chatgpt/WSP-19 -p 'test_*.py' -v`

`python research/contrib/chatgpt/WSP-19/run_dev.py`

Final full original+WSP01-17+WSP19 unit regression, frozen cost assay, source cleanliness and permanent G29 atlas must pass at one exact SHA/tree on GitHub-hosted Windows2022 and Ubuntu. No merge, main/accepted refs, controller/owner/runner/queue/scheduler, integration, paid API or protected scientific first-use.
