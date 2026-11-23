"""Research-only public-witness action-signature store; NOT native action-ID support.

This file deliberately does not import the illustrative law/role harness. Every
bit in a signature originates from a separately revealed public consequence.
A complete signature supports observational equivalence, not causal transfer.
"""
import hashlib
import json

SCHEMA = "wscm.transfer02.public-action-signature.dev.v1"
MAX_EVENTS = 256
MAX_ACTIONS = 16
MAX_BYTES = 32 * 1024
STATES = ((0, 0), (0, 1), (1, 0), (1, 1))


def _require(condition, code):
    if not condition:
        raise ValueError(code)


def _request(request):
    _require(type(request) is dict and set(request) == {"public_view", "external_action_id"},
             "PUBLIC_ACTION_REQUEST_INVALID")
    view = request["public_view"]
    action = request["external_action_id"]
    _require(type(view) is list and len(view) == 2 and
             all(type(bit) is int and bit in (0, 1) for bit in view) and
             type(action) is int and 0 <= action <= 2**31 - 1,
             "PUBLIC_ACTION_REQUEST_INVALID")
    return tuple(view), action


def _witness_id(value):
    _require(type(value) is str and len(value) == 64 and
             all(char in "0123456789abcdef" for char in value), "PUBLIC_WITNESS_ID_INVALID")
    return value


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


class PublicActionSignatures:
    """Immutable, finite readout of observations indexed by opaque public IDs.

    No model-to-native adapter is implied. A missing/contradictory cell yields
    abstention. In particular, a matching completed truth table proves only
    witnessed functional equivalence on these four visible states.
    """

    def __init__(self, events=()):
        self._events = tuple(events)
        self._by_witness = {event[0]: event for event in self._events}

    def observe(self, request, outcome, witness_id):
        state, action = _request(request)
        _require(type(outcome) is int and outcome in (0, 1), "PUBLIC_OUTCOME_INVALID")
        _witness_id(witness_id)
        event = (witness_id, action, state, outcome)
        previous = self._by_witness.get(witness_id)
        if previous is not None:
            _require(previous == event, "PUBLIC_WITNESS_CONFLICT")
            return self
        _require(len(self._events) < MAX_EVENTS, "PUBLIC_WITNESS_CAPACITY")
        ids = {e[1] for e in self._events}
        _require(action in ids or len(ids) < MAX_ACTIONS, "PUBLIC_ACTION_CAPACITY")
        return PublicActionSignatures(self._events + (event,))

    def signature(self, external_action_id):
        _require(type(external_action_id) is int and
                 0 <= external_action_id <= 2**31 - 1, "PUBLIC_ACTION_ID_INVALID")
        counts = {state: set() for state in STATES}
        for _, action, state, outcome in self._events:
            if action == external_action_id:
                counts[state].add(outcome)
        if any(len(counts[state]) != 1 for state in STATES):
            return None
        return tuple(next(iter(counts[state])) for state in STATES)

    def equivalent(self, first, second):
        a = self.signature(first)
        b = self.signature(second)
        return None if a is None or b is None else a == b

    def checkpoint(self):
        payload = {"schema": SCHEMA, "events": [
            [witness, action, list(state), outcome]
            for witness, action, state, outcome in self._events
        ]}
        raw = _canonical(payload)
        _require(len(raw) <= MAX_BYTES, "PUBLIC_CHECKPOINT_CAPACITY")
        return raw

    @staticmethod
    def checkpoint_sha256(raw):
        _require(type(raw) is bytes, "PUBLIC_CHECKPOINT_TYPE")
        return hashlib.sha256(raw).hexdigest()

    @classmethod
    def restore(cls, raw, expected_sha256):
        _require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES and
                 type(expected_sha256) is str and len(expected_sha256) == 64 and
                 hashlib.sha256(raw).hexdigest() == expected_sha256,
                 "PUBLIC_CHECKPOINT_PIN")
        try:
            payload = json.loads(raw.decode("ascii"))
            _require(type(payload) is dict and set(payload) == {"schema", "events"} and
                     payload["schema"] == SCHEMA and type(payload["events"]) is list and
                     len(payload["events"]) <= MAX_EVENTS and raw == _canonical(payload),
                     "PUBLIC_CHECKPOINT_SCHEMA")
            restored = cls()
            for entry in payload["events"]:
                _require(type(entry) is list and len(entry) == 4,
                         "PUBLIC_CHECKPOINT_ROW")
                witness, action, state, outcome = entry
                _require(witness not in restored._by_witness, "PUBLIC_CHECKPOINT_DUPLICATE")
                restored = restored.observe(
                    {"public_view": state, "external_action_id": action},
                    outcome, witness,
                )
            _require(restored.checkpoint() == raw, "PUBLIC_CHECKPOINT_DRIFT")
            return restored
        except (ValueError, KeyError, TypeError, UnicodeError, RecursionError) as exc:
            raise ValueError("PUBLIC_CHECKPOINT_REJECTED") from exc
