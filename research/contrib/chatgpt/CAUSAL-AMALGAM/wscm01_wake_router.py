"""WSCM-01 development-only bounded router for charged causal-role signatures.

No model/Genome writes, LSH claims, sleep consolidation, or protected-world use.
Templates must be established separately on a complete, charged 128-probe
basis; at most two caller-asserted development probes are accepted per action.
Caller-supplied charged/controlled flags are NOT authenticated source custody.
"""

WIDTH = 128
FULL_MASK = (1 << WIDTH) - 1
MAX_ROLES = 16
MAX_ACTIONS = 64
MAX_PROBES = 2


class WakeRoleRouter:
    """Phenotype-only exact partial-Hamming router with explicit abstention.

    Fixed caps bound the worst-case template scan. This is an engineering
    reference, NOT a learned LSH index or a causal-identification result.
    A single matching template is always PROVISIONAL in an open world;
    two observations cannot certify equivalence across 128 basis points.
    """

    def __init__(self, templates):
        if type(templates) is not dict or not 1 <= len(templates) <= MAX_ROLES:
            raise ValueError("WSCM_ROLE_CAPACITY")
        for role, bits in templates.items():
            if type(role) is not int or role < 0 or type(bits) is not int or not 0 <= bits <= FULL_MASK:
                raise ValueError("WSCM_TEMPLATE_CONTRACT")
        self._templates = tuple(sorted(templates.items()))
        self._observed = {}
        self._receipt_index = {}

    @staticmethod
    def _check_action(action):
        if type(action) is not int or action < 0:
            raise ValueError("WSCM_ACTION_CONTRACT")

    def _candidates(self, observations):
        mask = 0
        observed = 0
        for bit, (value, _) in observations.items():
            mask |= 1 << bit
            if value:
                observed |= 1 << bit
        return tuple(role for role, template in self._templates
                     if ((template ^ observed) & mask).bit_count() == 0)

    def status(self, action):
        self._check_action(action)
        observations = self._observed.get(action)
        if not observations:
            return "UNSEEN", None
        candidates = self._candidates(observations)
        if not candidates:
            return "UNKNOWN", None
        if len(candidates) > 1:
            return "AMBIGUOUS", None
        return "PROVISIONAL", candidates[0]

    def next_probe(self, action):
        """Choose a deterministic distinguishing basis bit; None means abstain."""
        self._check_action(action)
        observations = self._observed.get(action, {})
        if len(observations) >= MAX_PROBES or self.status(action)[0] == "UNKNOWN":
            return None
        candidates = self._candidates(observations)
        if not candidates:
            return None
        table = dict(self._templates)
        best_bit, best_split = None, -1
        for bit in range(WIDTH):
            if bit in observations:
                continue
            ones = sum((table[role] >> bit) & 1 for role in candidates)
            split = min(ones, len(candidates) - ones)
            if split > best_split:
                best_bit, best_split = bit, split
        return best_bit if best_split > 0 or len(candidates) == 1 else None

    def observe(self, action, basis_bit, delta, receipt_id, *, charged, controlled):
        """Accept development asserted basis data, NOT an authenticated do(action) receipt.

        Only a separately qualified evidence adapter may enable source use.
        In particular, boolean flags alone are no proof of a charged action.
        """
        self._check_action(action)
        if (type(basis_bit) is not int or not 0 <= basis_bit < WIDTH
                or type(delta) is not int or delta not in (0, 1)
                or type(receipt_id) is not int or receipt_id < 0
                or charged is not True or controlled is not True):
            raise ValueError("WSCM_CHARGED_RECEIPT_REQUIRED")
        if action not in self._observed and len(self._observed) >= MAX_ACTIONS:
            raise ValueError("WSCM_ACTION_CAPACITY")
        current = self._observed.get(action, {})
        prior_receipt = self._receipt_index.get(receipt_id)
        if prior_receipt is not None and prior_receipt != (action, basis_bit, delta):
            raise ValueError("WSCM_RECEIPT_REUSE")
        if basis_bit in current:
            if current[basis_bit] != (delta, receipt_id):
                raise ValueError("WSCM_CONFLICTING_RECEIPT")
            return self.status(action)
        if len(current) >= MAX_PROBES:
            raise ValueError("WSCM_PROBE_CAPACITY")
        updated = dict(current)
        updated[basis_bit] = (delta, receipt_id)
        self._observed[action] = updated
        self._receipt_index[receipt_id] = (action, basis_bit, delta)
        return self.status(action)

    def snapshot(self):
        """Immutable, bounded phenotype evidence; excludes derived bindings."""
        return tuple((action, tuple(sorted((bit, *pair) for bit, pair in evidence.items())))
                     for action, evidence in sorted(self._observed.items()))

    @classmethod
    def restore(cls, templates, snapshot):
        router = cls(templates)
        if type(snapshot) is not tuple:
            raise ValueError("WSCM_SNAPSHOT_CONTRACT")
        for action, evidence in snapshot:
            if type(evidence) is not tuple:
                raise ValueError("WSCM_SNAPSHOT_CONTRACT")
            for bit, delta, receipt_id in evidence:
                if bit in router._observed.get(action, {}):
                    raise ValueError("WSCM_DUPLICATE_RESTORE")
                router.observe(action, bit, delta, receipt_id, charged=True, controlled=True)
        if router.snapshot() != snapshot:
            raise ValueError("WSCM_NONCANONICAL_SNAPSHOT")
        return router
