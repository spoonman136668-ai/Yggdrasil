# WSP-151 — hierarchical Bayesian causal overhypothesis (source-free stage)

**Parent:** qualified WSP-149 at `55dd1e9e9f79a8a944a841330bb0ddcd93143a22`; frozen scientific transfer NO-GO preserved. Sole-file prereg committed first at `e4134c85fa7905694fe74b9db8bbfa48725a0ff6`.

**Question:** Does learning a shared causal form (e.g., AND or OR) help unfamiliar-world few-shot prediction more than coefficient-frequency memory?

**Source-blind learner:** exact Beta(1,1) hyperposterior on OR/AND prevalence; lower-level enumeration of 63 nonempty causal subsets for each form; fixed 5% likelihood noise and explicit UNKNOWN form. Four witnessed demonstration interventions plus four own actions are reserved for prospective study. Current tests use fabricated rows only. Active action selector chooses posterior causal-form information gain. Predicts all 64 binary contexts, abstaining unless posterior predictive confidence is at least 99%.

**Frozen prospective source:** `prereg.json` commits independent FIT/TRANSFER/SHIFT/OFF source namespaces, eight paid effects per arm, postseal unseen queries, fully trained CART and exact symbolic controls, cold retention and wrong-confidence thresholds. No WSP151 source code, labels, first use, native weights, or scientific PASS exists yet. Original WSP149 effects will not be replayed.

**Reproduce fabricated tests:** `python -B -m unittest discover -s research/contrib/chatgpt/WSP-151 -p 'test_*.py' -v`. Source-free engineering only, no accepted-main mutation, scheduler/controller, merge or deployment authority.

**Evidence inspiration (not Yggdrasil success claims):** Kemp et al. 2010; Lucas et al. 2014; Kosoy et al. 2022; Meltzoff et al. 2012; Walker and Gopnik 2014; Legare 2012.
