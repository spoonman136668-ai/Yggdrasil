"""Bounded local sensory specialization for R7 cells.

Each cell observes only its own public sensor and its ring neighbor. It owns
at most two receptive-field slots, each containing the last two completed
public outcomes. There is no centrally keyed context-to-answer table: votes
come from distinct independently updated local receptive fields. Three
nonconflicting cell votes are required, otherwise abstain.
"""
import hashlib
import json
from local_cell_reversal_candidate import ReversalColony

class SpecializedColony(ReversalColony):
    def __init__(self):
        super().__init__()
        self.slots = {ctx: [{} for _ in range(4)] for ctx in ("A", "B")}

    def learn_completed_public_feedback(self, context, sensors, public_outcome, delay_steps):
        # Validate before any mutation; original native R7 updates remain local.
        self._validate(context, sensors)
        if type(delay_steps) is not int or delay_steps < 2 or type(public_outcome) is not bool:
            raise ValueError("COMPLETED_PUBLIC_FEEDBACK_REQUIRED")
        for i, slot in enumerate(self.slots[context]):
            receptive = (sensors[i], sensors[(i + 1) % 4])
            if receptive not in slot and len(slot) >= 2:
                raise ValueError("LOCAL_RECEPTIVE_FIELD_CAP")
        super().learn_completed_public_feedback(context, sensors, public_outcome, delay_steps)
        for i, slot in enumerate(self.slots[context]):
            receptive = (sensors[i], sensors[(i + 1) % 4])
            slot[receptive] = (slot.get(receptive, ()) + (public_outcome,))[-2:]

    def predict_public(self, context, sensors):
        self._validate(context, sensors)
        yes = no = 0
        for i, slot in enumerate(self.slots[context]):
            evidence = slot.get((sensors[i], sensors[(i + 1) % 4]), ())
            if len(evidence) == 2 and evidence[0] == evidence[1]:
                if evidence[0]:
                    yes += 1
                else:
                    no += 1
        # Three separately trained local receptive fields must agree.
        if yes >= 3 and no == 0:
            return True
        if no >= 3 and yes == 0:
            return False
        return None

    def checkpoint(self):
        cells = super().checkpoint().decode("utf-8")
        slots = {ctx: [[{"receptive": list(key), "recent": list(values)}
                         for key, values in sorted(slot.items())]
                        for slot in self.slots[ctx]] for ctx in ("A", "B")}
        body = {"schema": "ygg.r7.local_specialized.v1", "base": cells, "slots": slots}
        raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        signed = json.dumps({"payload": body, "sha256": hashlib.sha256(raw).hexdigest()},
                            sort_keys=True, separators=(",", ":")).encode()
        if len(signed) > 32768:
            raise ValueError("SPECIALIZED_CHECKPOINT_CAP")
        return signed

    @classmethod
    def restore(cls, blob):
        if type(blob) is not bytes or not 0 < len(blob) <= 32768:
            raise ValueError("SPECIALIZED_CHECKPOINT_INVALID")
        packet = json.loads(blob)
        if type(packet) is not dict or set(packet) != {"payload", "sha256"}:
            raise ValueError("SPECIALIZED_CHECKPOINT_FIELDS")
        body = packet["payload"]
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        if hashlib.sha256(canonical).hexdigest() != packet["sha256"]:
            raise ValueError("SPECIALIZED_CHECKPOINT_HASH")
        if body.get("schema") != "ygg.r7.local_specialized.v1" or set(body["slots"]) != {"A", "B"}:
            raise ValueError("SPECIALIZED_CHECKPOINT_SCHEMA")
        restored_base = ReversalColony.restore(body["base"].encode())
        result = cls()
        result.cells = restored_base.cells
        result.feedback_updates = restored_base.feedback_updates
        result.neighbor_messages = restored_base.neighbor_messages
        for ctx in ("A", "B"):
            if len(body["slots"][ctx]) != 4:
                raise ValueError("SPECIALIZED_CELL_COUNT")
            for i, entries in enumerate(body["slots"][ctx]):
                if type(entries) is not list or len(entries) > 2:
                    raise ValueError("SPECIALIZED_SLOT_CAP")
                for item in entries:
                    if type(item) is not dict or set(item) != {"receptive", "recent"}:
                        raise ValueError("SPECIALIZED_SLOT_FIELDS")
                    bits, values = item["receptive"], item["recent"]
                    if (type(bits) is not list or len(bits) != 2 or
                        any(type(v) is not bool for v in bits) or
                        type(values) is not list or len(values) > 2 or
                        any(type(v) is not bool for v in values)):
                        raise ValueError("SPECIALIZED_SLOT_VALUES")
                    key = tuple(bits)
                    if key in result.slots[ctx][i]:
                        raise ValueError("SPECIALIZED_DUPLICATE")
                    result.slots[ctx][i][key] = tuple(values)
        return result
