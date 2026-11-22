"""WSCM DEV-only native-package admission of witnessed opaque action identities.

Passive evidence component, not a second learner or a new source authority.
All inputs are disclosed fixture receipts; SHA pins bytes, not real-world custody.
No private role map, regime label, or binary x1/x2 action alias is accepted.
"""
import hashlib
import json

SCHEMA = "yggdrasil.wscm.external-action-evidence.dev.v1"
RECEIPT_SCHEMA = "yggdrasil.wscm.public-action-fixture.dev.v1"
SOURCE_MODE = "engineering_fixture_only"
MAX_EVENTS = 256
MAX_ACTIONS = 32
MAX_CHECKPOINT_BYTES = 65536
MAX_RECEIPT_BYTES = 2048
STATES = ((0, 0), (0, 1), (1, 0), (1, 1))


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _pin(value):
    return (type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value))


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _public(request):
    _require(type(request) is dict and set(request) ==
             {"public_view", "external_action_id"}, "WSCM_PUBLIC_REQUEST")
    view = request["public_view"]
    action = request["external_action_id"]
    _require(type(view) is list and len(view) == 2 and
             all(type(bit) is int and bit in (0, 1) for bit in view)
             and type(action) is int and 0 <= action < 2**31,
             "WSCM_PUBLIC_REQUEST")
    return tuple(view), action


def _fixture_receipt(raw, expected_sha256):
    _require(type(raw) is bytes and 0 < len(raw) <= MAX_RECEIPT_BYTES
             and _pin(expected_sha256)
             and hashlib.sha256(raw).hexdigest() == expected_sha256,
             "WSCM_RECEIPT_PIN")
    try:
        obj = json.loads(raw.decode("ascii"))
        _require(type(obj) is dict and set(obj) ==
                 {"schema", "source_mode", "source_id", "public_view",
                  "external_action_id", "outcome"}
                 and obj["schema"] == RECEIPT_SCHEMA
                 and obj["source_mode"] == SOURCE_MODE
                 and _pin(obj["source_id"])
                 and type(obj["outcome"]) is int
                 and obj["outcome"] in (0, 1)
                 and raw == _canonical(obj), "WSCM_FIXTURE_ONLY")
        state, action = _public({"public_view": obj["public_view"],
                                 "external_action_id": obj["external_action_id"]})
    except (ValueError, TypeError, UnicodeError, KeyError, RecursionError) as exc:
        raise ValueError("WSCM_FIXTURE_ONLY") from exc
    return (obj["source_id"], action, state, obj["outcome"], expected_sha256)


class NativeExternalActionIdentity:
    """Immutable fixture-only action-ID evidence, never an intervention oracle.

    This is a native-package passive admission seam. It does NOT yet modify
    NativeEpisodeExperience's binary causal counters or prove transfer.
    """
    __slots__ = ("_rows", "_sources")

    def __init__(self):
        self._rows = ()
        self._sources = {}

    def observe_public_receipt(self, public_request, raw, expected_sha256):
        state, action = _public(public_request)
        source_id, observed_action, observed_state, result, pin = (
            _fixture_receipt(raw, expected_sha256))
        _require((action, state) == (observed_action, observed_state),
                 "WSCM_PUBLIC_RECEIPT_MISMATCH")
        row = (source_id, action, state, result, pin)
        previous = self._sources.get(source_id)
        if previous is not None:
            _require(previous == row, "WSCM_SOURCE_REPLAY_CONFLICT")
            return self
        _require(len(self._rows) < MAX_EVENTS, "WSCM_EVENT_CAPACITY")
        ids = {entry[1] for entry in self._rows}
        _require(action in ids or len(ids) < MAX_ACTIONS,
                 "WSCM_ACTION_CAPACITY")
        candidate = type(self)()
        candidate._rows = self._rows + (row,)
        candidate._sources = {**self._sources, source_id: row}
        candidate.checkpoint()  # Never admit state that cannot cold-restore.
        return candidate

    def observed_signature(self, external_action_id):
        _require(type(external_action_id) is int and
                 0 <= external_action_id < 2**31, "WSCM_ACTION_ID")
        values = {state: set() for state in STATES}
        for _, action, state, outcome, _ in self._rows:
            if action == external_action_id:
                values[state].add(outcome)
        if any(len(values[state]) != 1 for state in STATES):
            return None
        return tuple(next(iter(values[state])) for state in STATES)

    def observed_equivalent(self, first_id, second_id):
        first = self.observed_signature(first_id)
        second = self.observed_signature(second_id)
        return None if first is None or second is None else first == second

    def checkpoint(self):
        data = {"schema": SCHEMA, "source_mode": SOURCE_MODE,
                "records": [[source_id, action, list(view), outcome, pin]
                            for source_id, action, view, outcome, pin in self._rows]}
        raw = _canonical(data)
        _require(len(raw) <= MAX_CHECKPOINT_BYTES, "WSCM_CHECKPOINT_CAPACITY")
        return raw

    @staticmethod
    def sha256(raw):
        _require(type(raw) is bytes, "WSCM_CHECKPOINT_TYPE")
        return hashlib.sha256(raw).hexdigest()

    @classmethod
    def restore(cls, raw, expected_sha256):
        _require(type(raw) is bytes and 0 < len(raw) <= MAX_CHECKPOINT_BYTES
                 and _pin(expected_sha256)
                 and hashlib.sha256(raw).hexdigest() == expected_sha256,
                 "WSCM_CHECKPOINT_PIN")
        try:
            obj = json.loads(raw.decode("ascii"))
            _require(type(obj) is dict and set(obj) ==
                     {"schema", "source_mode", "records"}
                     and obj["schema"] == SCHEMA
                     and obj["source_mode"] == SOURCE_MODE
                     and type(obj["records"]) is list
                     and len(obj["records"]) <= MAX_EVENTS
                     and raw == _canonical(obj), "WSCM_CHECKPOINT_SCHEMA")
            restored = cls()
            for record in obj["records"]:
                _require(type(record) is list and len(record) == 5,
                         "WSCM_CHECKPOINT_ROW")
                source_id, action, view, outcome, pin = record
                _require(_pin(source_id) and _pin(pin)
                         and source_id not in restored._sources
                         and type(outcome) is int and outcome in (0, 1),
                         "WSCM_CHECKPOINT_ROW")
                state, action = _public({"public_view": view,
                                         "external_action_id": action})
                receipt = _canonical({
                    "schema": RECEIPT_SCHEMA, "source_mode": SOURCE_MODE,
                    "source_id": source_id, "public_view": list(state),
                    "external_action_id": action, "outcome": outcome,
                })
                _require(hashlib.sha256(receipt).hexdigest() == pin,
                         "WSCM_CHECKPOINT_RECEIPT_DRIFT")
                _require(len({x[1] for x in restored._rows} | {action})
                         <= MAX_ACTIONS, "WSCM_CHECKPOINT_ACTION_CAPACITY")
                row = (source_id, action, state, outcome, pin)
                restored._rows += (row,)
                restored._sources[source_id] = row
            _require(restored.checkpoint() == raw, "WSCM_CHECKPOINT_DRIFT")
            return restored
        except (ValueError, UnicodeError, KeyError, TypeError,
                RecursionError) as exc:
            raise ValueError("WSCM_CHECKPOINT_REJECTED") from exc
