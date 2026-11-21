# NUM06 exact archived run-length comparison — engineering only

BOCPD implements a defined, finite A→B→A model with all B start positions, no
beam pruning, an absorbing return to a frozen archived A posterior predictive
law, and no private phase/seed labels. Under this model, histories with a
common B start and differing return times are exactly coalescible. This is
not an exact posterior for arbitrary recurring regime histories or a claim
of general continual learning. The returned emission law deliberately stays
fixed; the evaluator must report this limitation. No unbounded bank allocation;
one shared public-prefix ledger, at most 512 rows and two logical laws per
hypothesis. Space for posterior hypotheses is additional overhead and must be
counted in actual CPU/RSS/checkpoint measurements.

An independent brute-force enumeration checks prior/posterior and predictions
on a tiny manual stream, including multiple possible return times and a second
action. Other fixtures check return, null, restore, tampering, input validation
and the predeclared 12-point hyperparameter grid.

Neither comparator has been FIT/VALID trained on registered NUM06 data. No
registered source generation, source admission, HELD evaluation, new seed
consumption, native model mutation, owner-branch mutation or deployment is
authorized by this patch. Do not interpret fixture results as scientific gain.
