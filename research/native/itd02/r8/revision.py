"""R8 source-only action-owned structural revision, layered on immutable R7.

This is bounded causal-model development, not external-world scientific acceptance.
Source learns only physically returned public before/action/after tuples.
"""
import hashlib
import itertools
import json
from research.native.itd02.r7.learner import NonlinearLocalLearner, canon

SCHEMA = "yggdrasil.itd02.r8.action-owned-structural-revision.v1"
PARENTS = tuple(itertools.combinations(range(8), 3))
WINDOW = 48
MIN_ROWS = 32
MIN_GAIN = 4


def _index(state, parents):
    return sum(((state >> bit) & 1) << idx for idx, bit in enumerate(parents))


def _model_fit(rows):
    """Learn only from observed selected-action effects, with 56 same-class hypotheses."""
    output = []
    for bit in range(8):
        winner = None
        for parents in PARENTS:
            counts = [0] * 8
            positives = [0] * 8
            for before, after in rows:
                slot = _index(before, parents)
                counts[slot] += 1
                positives[slot] += (after >> bit) & 1
            loss = sum(min(pos, n - pos) for pos, n in zip(positives, counts))
            if winner is None or loss < winner[0]:
                table = [int(2 * pos >= n) if n else 0 for pos, n in zip(positives, counts)]
                winner = (loss, parents, table)
        output.append({"parents": list(winner[1]), "table": winner[2], "fit_errors": winner[0]})
    return output


def _step(model, before):
    after = 0
    for bit, entry in enumerate(model):
        after |= entry["table"][_index(before, entry["parents"])] << bit
    return after


class RevisionCells:
    """Preserve the R7 stable model and revise only contradicted world/action cells.

    Each action/world owns its own bounded evidence FIFO and revisable fast model;
    original R7's frozen checkpoint never changes. No hidden change-point label.
    """
    def __init__(self, original_checkpoint):
        self.base = NonlinearLocalLearner.restore(original_checkpoint)
        self.original_checkpoint = original_checkpoint
        self.recent = {world: {str(a): [] for a in range(3)}
                       for world in self.base.models}
        self.mode = {world: {str(a): "stable" for a in range(3)}
                     for world in self.base.models}
        self.fast = {world: {str(a): None for a in range(3)}
                     for world in self.base.models}
        self.revisions = 0
        self.online_events = 0

    def step(self, world, action, before):
        if world not in self.mode or type(action) is not int or action not in (0, 1, 2) or type(before) is not int or not 0 <= before < 256:
            raise ValueError("R8_INVALID_SOURCE_OR_ACTION")
        a = str(action)
        if self.mode[world][a] == "fast":
            return _step(self.fast[world][a], before)
        return self.base.step(world, action, before)

    def observe(self, world, action, before, after):
        if world not in self.mode or type(action) is not int or action not in (0, 1, 2) or type(before) is not int or not 0 <= before < 256 or type(after) is not int or not 0 <= after < 256:
            raise ValueError("R8_INVALID_PUBLIC_CAUSAL_EFFECT")
        if self.online_events >= 2**52:
            raise ValueError("R8_EXPOSURE_LIMIT")
        a = str(action)
        rows = (self.recent[world][a] + [[before, after]])[-WINDOW:]
        proposed = None
        if len(rows) >= MIN_ROWS:
            stable_error = sum(self.base.step(world, action, x) != y for x, y in rows)
            if stable_error <= 2:
                proposed = ("stable", None)
            elif stable_error >= MIN_GAIN:
                model = _model_fit(rows)
                new_error = sum(_step(model, x) != y for x, y in rows)
                if new_error + MIN_GAIN <= stable_error:
                    proposed = ("fast", model)
        # Commit exactly once, after validated selected public evidence.
        self.recent[world][a] = rows
        self.online_events += 1
        if proposed is not None:
            mode, model = proposed
            if mode != self.mode[world][a]:
                self.revisions += 1
            self.mode[world][a] = mode
            self.fast[world][a] = model

    def checkpoint(self):
        state = {"schema": SCHEMA, "original": self.original_checkpoint.decode(),
                 "recent": self.recent, "mode": self.mode, "fast": self.fast,
                 "revisions": self.revisions, "online_events": self.online_events}
        body = canon(state)
        if len(body) > 350000:
            raise ValueError("R8_SNAPSHOT_TOO_BIG")
        return canon({"body": state, "sha256": hashlib.sha256(body).hexdigest()})

    @classmethod
    def restore(cls, blob):
        if type(blob) is not bytes or not 0 < len(blob) <= 350000:
            raise ValueError("R8_CHECKPOINT_SIZE")
        try:
            record = json.loads(blob)
            if set(record) != {"body", "sha256"}:
                raise ValueError("R8_CHECKPOINT_STRUCTURE")
            state = record["body"]
            if hashlib.sha256(canon(state)).hexdigest() != record["sha256"] or state["schema"] != SCHEMA:
                raise ValueError("R8_CHECKPOINT_AUTHENTICATION")
            obj = cls(state["original"].encode())
            if (set(state) != {"schema", "original", "recent", "mode", "fast", "revisions", "online_events"}
                or set(state["recent"]) != set(obj.recent)
                or set(state["mode"]) != set(obj.mode)
                or set(state["fast"]) != set(obj.fast)
                or type(state["revisions"]) is not int
                or type(state["online_events"]) is not int
                or not 0 <= state["revisions"] <= state["online_events"] < 2**52):
                raise ValueError("R8_UNTRUSTED_STATE")
            total = 0
            for w in obj.recent:
                if (set(state["recent"][w]) != {"0", "1", "2"}
                    or set(state["mode"][w]) != {"0", "1", "2"}
                    or set(state["fast"][w]) != {"0", "1", "2"}):
                    raise ValueError("R8_UNTRUSTED_ACTION_SET")
                for a in ("0", "1", "2"):
                    rows = state["recent"][w][a]
                    mode = state["mode"][w][a]
                    fast = state["fast"][w][a]
                    if (type(rows) is not list or len(rows) > WINDOW or
                        any(type(v) is not list or len(v) != 2 or
                            any(type(x) is not int or not 0 <= x < 256 for x in v) for v in rows) or
                        mode not in ("stable", "fast") or
                        (mode == "fast") != (fast is not None)):
                        raise ValueError("R8_UNTRUSTED_EVIDENCE")
                    if fast is not None:
                        if type(fast) is not list or len(fast) != 8:
                            raise ValueError("R8_INVALID_FAST_MODEL")
                        for entry in fast:
                            if (type(entry) is not dict or set(entry) != {"parents", "table", "fit_errors"} or
                                type(entry["parents"]) is not list or tuple(entry["parents"]) not in PARENTS or
                                type(entry["table"]) is not list or len(entry["table"]) != 8 or
                                any(type(v) is not int or v not in (0, 1) for v in entry["table"]) or
                                type(entry["fit_errors"]) is not int or entry["fit_errors"] < 0):
                                raise ValueError("R8_INVALID_FAST_TABLE")
                    total += len(rows)
            if state["online_events"] < total:
                raise ValueError("R8_INCONSISTENT_EVENT_COUNTER")
            obj.recent = state["recent"]
            obj.mode = state["mode"]
            obj.fast = state["fast"]
            obj.revisions = state["revisions"]
            obj.online_events = state["online_events"]
            return obj
        except (ValueError, KeyError, TypeError, OverflowError, AttributeError) as ex:
            raise ValueError("R8_UNTRUSTED_CHECKPOINT") from ex
