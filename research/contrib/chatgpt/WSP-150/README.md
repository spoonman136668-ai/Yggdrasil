# WSP-150 — A source-free identifiability limit of exact GF(2) weights

**Status:** isolated research falsification. Neither native Yggdrasil training nor action-consequence science.

Parent: WSP-149 candidate `55dd1e9e9f79a8a944a841330bb0ddcd93143a22` (full Linux/Windows and independent G29 PASS, transfer science NO-GO). The WSP-150 preregistration was committed **alone before implementation**. Accepted `main` and previously sealed research outcomes are unchanged.

## Question and mathematical certificate

The current direct-weight readout assigns 64 numerical GF(2) monomial coefficients to six binary factors, with output at context `x` equal to the XOR of coefficients for masks contained in `x`.

Its 64-by-64 evaluation matrix is an invertible Boolean-lattice zeta transform. For **any** unobserved context `q`, toggle every coefficient indexed by a superset of `q`; its readout changes **only at q**, and remains bit-identical on every other context. The number of toggled coefficients is `2**(6-popcount(q))`.

Therefore, after 32 distinct genuinely observed (context,effect) pairs, an unrestricted 64-coefficient GF(2) model still permits opposite predictions at **each of the other 32 contexts**, even when it interpolates the observed effects perfectly. Training fit and cold coefficient restoration alone cannot logically certify a held-out answer. This proof does **not** rule out learning with independently justified structural priors, a smaller true hypothesis class, additional causal observations, or a recurrent native architecture.

## Falsification controls

`identifiability.py` is independently implemented from the existing WSP149 elimination code. Source-free tests check full matrix rank, 4,096 Kronecker-delta identities, 128 held-context alternative fits across four deterministic fabricated 32-observation splits, inversion consistency, invalid/duplicate inputs, negative spike corruption, and unchanged WSP149 readout semantics on a full checkout.

Run: `python -B -m unittest discover -s research/contrib/chatgpt/WSP-150 -p 'test_*.py' -v` from the checkout root. No synthetic source owner, protected first-use, original science dataset, or previous scored truth is imported or replayed.

**Classification:** a proof of underidentification **within the unconstrained complete GF(2) model**, not a behavioral intelligence gain. The next scientifically useful test must learn *restricted, reusable operator-level causal structure*, evaluate unfamiliar composition and cold retention, and outperform fully trained conventional and symbolic controls on independently fresh action-consequence worlds under a separately frozen, authorized source protocol. Do not merge or promote on this proof alone.
