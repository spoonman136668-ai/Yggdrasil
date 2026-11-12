# WSP-47 — numerical equation memory from real trajectories

WSP46 exposed a large gap between arbitrary state probes and real action experience. This successor keeps **exactly one shared real trajectory per world**, with the frozen least-visit policy and reset budget. Every learning arm receives the same ordered actual action/state/output replies. It changes the learning rule, not the available source evidence.

Preregistration `5722a12ee3e7cf1bc051d4efcdebb713b91eafbc`; pre-implementation clarification `ef1a32275e4c2c0a884ae0134ce51730e775c55a` assigns the positive threshold to structured linear/quadratic/cubic worlds and keeps arbitrary hash as a negative. Both precede implementation and PRIMARY. Parent WSP46 #937.

Each bank is a preprogrammed fixed gated GF2 elimination machine, implemented with bit-parallel Boolean register operations. Stored pivot rows, rhs and occupancy are numeric state. Column loops have fixed architectural bounds; numeric gates select elimination or row writes. An observed-fact bitplane memory preserves actual facts. Query elimination returns a validity bit only when the feature vector is in the observed equation span and that bank has not seen a contradiction. Generic Python simulates the supplied circuit; this is not invention of a learning algorithm or absence of software.

Four fixed feature banks contain all degree<=1/2/3/full Boolean monomials. A numerical first-consistent winner selects the smallest bank not contradicted by actual observations. The hierarchy, features and memory capacity are preallocated. **Known is relative to the selected prior:** a wrong but still consistent prior can confidently fail on an unobserved/unreachable edge. A dedicated negative test preserves this behavior. No calibrated arbitrary-world confidence is claimed.

PRIMARY:48 worlds,512/1024 real transitions each,96 shared-evidence evaluations;384 fixed-bank and96 adaptive model conditions. State widths8/6/4;linear/quadratic/cubic/hash;4 disjoint seeds. Compare independent batch set-based GF2 identification on identical data/features, frozen WSP46 numerical subcube learning, fully fitted one-hot regression and erasure. Batch inference/prediction validity must exactly match; matched true-family known predictions must have no errors. This is a strongest mathematical control for the supplied vocabulary, not a strongest trained neural comparison.

Local7 tests PASS. Initial12-world DEV recovered all genuinely unseen reachable structured predictions (192/192) and all observed facts; the frozen same-data subcube learner got14/192. Hash unseen facts remained unknown/wrong. Some consistent lower-prior models were confidently wrong outside their explored reachability; those errors are explicitly split out in the final evaluator instrumentation. No local PRIMARY. All full-source/counterfactual errors, invalid predictions and missing-unseen cases remain in the report.

Capacity is larger than WSP46: per action/bank M pivot words of M bits,M output rhs words,M occupied bits,seen bitplanes and fact memory. Four banks are resident; report every bank's rank/fault/payload/snapshot size. Identical evidence does not imply matched architecture/capacity or CPU. No data/compute superiority claim.

Commands:
```
python -m unittest discover -s research/contrib/chatgpt/WSP-47 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-47/qualify.py
python research/contrib/chatgpt/WSP-47/battery.py --cohort PRIMARY
```

Full final Windows/Linux regression,G29 and clean source required. External contributor draft only: no merge/main/accepted refs,official loop,private runner,protected first-use,controller,scheduler,paid API,integration,deployment or live actions. No general intelligence,unrestricted primitive/representation discovery or neural training replacement claim.
