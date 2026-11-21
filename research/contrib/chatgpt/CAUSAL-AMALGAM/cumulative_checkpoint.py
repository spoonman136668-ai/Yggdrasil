"""Cumulative Amalgam resume envelope. Research only; no source actions or I/O.

Preserves exact v1 native+JEPA core bytes while sealing external policy and
witness custody state. An SHA or owner-lease string is not execution authority.
"""
import json
from yggdrasil.native_context_basis import canonical, digest, pin

SCHEMA = "yggdrasil.amalgam.cumulative-envelope.v1"
VETO_SCHEMA = "yggdrasil.amalgam.charged-veto-receipt.v1"
LIMIT = 96 * 1024 * 1024
CURSOR_KEYS = {"source_sha256", "owner_lease_sha256", "next_ordinal"}
MODEL_KEYS = {"core_ascii", "core_sha256", "policy_sha256",
              "ledger_sha256", "selector", "historical_readout_sha256"}
BUNDLE_KEYS = {"schema", "anchor", "active", "quines_ascii", "quines_sha256",
               "vetoes", "cursor", "owner_custody_verified", "scientific_pass"}
RECEIPT_KEYS = {"schema", "event", "source_sha256", "packet_sha256",
                "active_before_sha256", "rejected_candidate_sha256"}


def _load(raw):
    if type(raw) is not bytes or not raw or len(raw) > LIMIT:
        raise ValueError("CUMULATIVE_ENVELOPE_BYTES")
    try:
        item = json.loads(raw)
    except (UnicodeError, ValueError) as error:
        raise ValueError("CUMULATIVE_ENVELOPE_JSON") from error
    if type(item) is not dict or canonical(item) != raw:
        raise ValueError("CUMULATIVE_ENVELOPE_NONCANONICAL")
    return item


def _cursor(value):
    if (type(value) is not dict or set(value) != CURSOR_KEYS
            or not pin(value["source_sha256"])
            or not pin(value["owner_lease_sha256"])
            or type(value["next_ordinal"]) is not int
            or value["next_ordinal"] < 0):
        raise ValueError("CUMULATIVE_CURSOR_INVALID")
    return value


def _vetoes(values, accepted):
    if type(values) not in (list, tuple):
        raise ValueError("CUMULATIVE_VETO_COLLECTION")
    seen, records = {}, []
    for raw in values:
        item = _load(raw)
        if (set(item) != RECEIPT_KEYS or item["schema"] != VETO_SCHEMA
                or type(item["source_sha256"]) is not str
                or not item["source_sha256"]
                or not all(pin(item[k]) for k in (
                    "packet_sha256", "active_before_sha256",
                    "rejected_candidate_sha256"))):
            raise ValueError("CUMULATIVE_VETO_SCHEMA")
        event = item["event"]
        if (type(event) is not list or len(event) != 6
                or type(event[0]) is not str or not event[0]
                or type(event[1]) is not list or len(event[1]) != 2
                or any(type(view) is not list or len(view) != 2
                       for view in event[1])
                or any(type(v) is not int or v not in (0, 1)
                       for v in event[2:])):
            raise ValueError("CUMULATIVE_VETO_EVENT")
        identifier, views, first, state, second, reward = event
        row = {"s1": views[0][0], "x1": first,
               "s2": state, "x2": second, "y": reward}
        if digest(canonical([identifier, views, row])) != item["packet_sha256"]:
            raise ValueError("CUMULATIVE_VETO_PACKET")
        if identifier in accepted:
            raise ValueError("CUMULATIVE_VETO_ACCEPTED_ID")
        if identifier in seen:
            if seen[identifier] != raw:
                raise ValueError("CUMULATIVE_VETO_CONFLICT")
            continue
        seen[identifier] = raw
        records.append({"sha256": digest(raw), "ascii": raw.decode("ascii")})
    return records


def _model_record(value, historical, guard):
    core = guard._system(value).checkpoint()
    if type(core) is not bytes or not core or len(core) > LIMIT:
        raise ValueError("CUMULATIVE_CORE_INVALID")
    ledger = guard._ledger(value)
    return {
        "core_ascii": core.decode("ascii"),
        "core_sha256": digest(core),
        "policy_sha256": digest(guard._checkpoint(value)),
        "ledger_sha256": digest(canonical(ledger)),
        "selector": (guard._selector_receipt(value)
                     if guard._selector(value) else None),
        "historical_readout_sha256":
            digest(canonical([guard._loss(value, row) for row in historical])),
    }


def seal(anchor, active, quines, quine_sha256, *, cursor, veto_receipts=(), guard):
    """Bundle the same learner; existing native+JEPA v1 core stays byte-identical."""
    guard._verify_frozen_inputs(anchor, active, quines, quine_sha256,
                                guard.TOLERANCE)
    _cursor(cursor)
    old, current = guard._ledger(anchor), guard._ledger(active)
    identifiers = [row[0] for row in current]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("CUMULATIVE_DUPLICATE_ADMITTED")
    qraw = canonical(quines)
    if digest(qraw) != quine_sha256:
        raise ValueError("CUMULATIVE_QUINE_PIN")
    data = {
        "schema": SCHEMA,
        "anchor": _model_record(anchor, old, guard),
        "active": _model_record(active, old, guard),
        "quines_ascii": qraw.decode("ascii"),
        "quines_sha256": quine_sha256,
        "vetoes": _vetoes(veto_receipts, set(identifiers)),
        "cursor": cursor,
        "owner_custody_verified": False,
        "scientific_pass": False,
    }
    raw = canonical(data)
    if len(raw) > LIMIT:
        raise ValueError("CUMULATIVE_CAPACITY")
    return raw, digest(raw)


def recover(raw, expected_sha256, *, restore_core, build_selector, guard):
    """Caller provides independently source-pinned existing native+JEPA restorer."""
    if not pin(expected_sha256) or digest(raw) != expected_sha256:
        raise ValueError("CUMULATIVE_BUNDLE_PIN")
    data = _load(raw)
    if (set(data) != BUNDLE_KEYS or data["schema"] != SCHEMA
            or data["owner_custody_verified"] is not False
            or data["scientific_pass"] is not False):
        raise ValueError("CUMULATIVE_BUNDLE_SCHEMA")
    _cursor(data["cursor"])
    if not callable(restore_core) or not callable(build_selector):
        raise ValueError("CUMULATIVE_RESTORE_CALLBACKS")
    qraw = data["quines_ascii"].encode("ascii")
    if digest(qraw) != data["quines_sha256"]:
        raise ValueError("CUMULATIVE_QUINE_HASH")
    quines = _load(qraw)
    result = []
    for name in ("anchor", "active"):
        item = data[name]
        if type(item) is not dict or set(item) != MODEL_KEYS:
            raise ValueError("CUMULATIVE_MODEL_SCHEMA")
        core = item["core_ascii"].encode("ascii")
        if not pin(item["core_sha256"]) or digest(core) != item["core_sha256"]:
            raise ValueError("CUMULATIVE_CORE_PIN")
        model = restore_core(core, item["core_sha256"])
        if guard._system(model).checkpoint() != core:
            raise ValueError("CUMULATIVE_CORE_REPLAY")
        if item["selector"] is not None:
            model = build_selector(model, item["selector"])
            if guard._selector_receipt(model) != item["selector"]:
                raise ValueError("CUMULATIVE_SELECTOR_REPLAY")
        if (digest(guard._checkpoint(model)) != item["policy_sha256"]
                or digest(canonical(guard._ledger(model))) != item["ledger_sha256"]):
            raise ValueError("CUMULATIVE_POLICY_OR_LEDGER_REPLAY")
        result.append(model)
    anchor, active = result
    guard._verify_frozen_inputs(anchor, active, quines,
                                data["quines_sha256"], guard.TOLERANCE)
    old = guard._ledger(anchor)
    for name, model in zip(("anchor", "active"), result, strict=True):
        probe = digest(canonical([guard._loss(model, row) for row in old]))
        if probe != data[name]["historical_readout_sha256"]:
            raise ValueError("CUMULATIVE_OLD_READOUT_REPLAY")
    receipts = []
    for entry in data["vetoes"]:
        if type(entry) is not dict or set(entry) != {"sha256", "ascii"}:
            raise ValueError("CUMULATIVE_VETO_ENTRY")
        raw_receipt = entry["ascii"].encode("ascii")
        if digest(raw_receipt) != entry["sha256"]:
            raise ValueError("CUMULATIVE_VETO_PIN")
        receipts.append(raw_receipt)
    if _vetoes(receipts, {row[0] for row in guard._ledger(active)}) != data["vetoes"]:
        raise ValueError("CUMULATIVE_VETO_REPLAY")
    return {"anchor": anchor, "active": active, "quines": quines,
            "quines_sha256": data["quines_sha256"],
            "veto_receipts": tuple(receipts), "cursor": data["cursor"],
            "owner_custody_verified": False, "scientific_pass": False,
            "source_actions": 0}
