"""WSP39 bounded training-free binary dynamical model; no tokens or transformers."""
import hashlib
import json

ACTIONS = 4
MAGIC = b"WSP39V1|"


def require_bit(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("WSP39_BAD_BIT")
    return value


class NumericModel:
    """Stored GF(2) numeric transition weights. Interpreter is pre-authored."""
    def __init__(self, width, weight_rows, biases):
        if type(width) is not int or width not in (64, 128, 256, 512, 1024):
            raise ValueError("WSP39_BAD_WIDTH")
        if type(weight_rows) is not tuple or len(weight_rows) != ACTIONS or type(biases) is not tuple or len(biases) != ACTIONS:
            raise ValueError("WSP39_BAD_ACTIONS")
        for rows, bias in zip(weight_rows, biases):
            if type(rows) is not tuple or len(rows) != width or type(bias) is not int or bias < 0 or bias.bit_length() > width:
                raise ValueError("WSP39_BAD_ROWS")
            if any(type(row) is not int or row < 0 or row.bit_length() > width for row in rows):
                raise ValueError("WSP39_BAD_WEIGHT")
        self.width = width
        self.rows = weight_rows
        self.biases = biases

    def apply(self, action, state):
        if type(action) is not int or not 0 <= action < ACTIONS or type(state) is not int or state < 0 or state.bit_length() > self.width:
            raise ValueError("WSP39_BAD_STATE_ACTION")
        out = self.biases[action]
        for i, row in enumerate(self.rows[action]):
            if (row & state).bit_count() % 2:
                out ^= 1 << i
        return out

    def rollout(self, state, actions):
        if type(actions) is not tuple or not 1 <= len(actions) <= 4:
            raise ValueError("WSP39_BAD_SEQUENCE")
        for action in actions:
            state = self.apply(action, state)
        return state

    def plan(self, start, goal, depth=3):
        if type(goal) is not int or goal < 0 or goal.bit_length() > self.width or depth != 3:
            raise ValueError("WSP39_BAD_GOAL")
        # Exactly 4^3=64 candidates. No hidden oracle access during planning.
        for a in range(ACTIONS):
            mid1 = self.apply(a, start)
            for b in range(ACTIONS):
                mid2 = self.apply(b, mid1)
                for c in range(ACTIONS):
                    if self.apply(c, mid2) == goal:
                        return (a, b, c)
        return None

    def patch(self, action, output_bit, input_bit, new_bit):
        if type(action) is not int or not 0 <= action < ACTIONS or type(output_bit) is not int or not 0 <= output_bit < self.width or type(input_bit) is not int or not 0 <= input_bit < self.width:
            raise ValueError("WSP39_BAD_PATCH")
        require_bit(new_bit)
        groups = list(self.rows)
        rows = list(groups[action])
        original = rows[output_bit]
        rows[output_bit] = original | (1 << input_bit) if new_bit else original & ~(1 << input_bit)
        groups[action] = tuple(rows)
        return NumericModel(self.width, tuple(groups), self.biases)

    def snapshot(self):
        body = json.dumps({"schema": "wsp39.gf2.numeric.v1", "width": self.width, "rows": [[hex(v) for v in rr] for rr in self.rows], "biases": [hex(v) for v in self.biases]}, sort_keys=True, separators=(",", ":")).encode("ascii")
        return MAGIC + len(body).to_bytes(4, "big") + body + hashlib.sha256(body).digest()

    @classmethod
    def restore(cls, data):
        if type(data) is not bytes or not data.startswith(MAGIC) or len(data) < len(MAGIC) + 36:
            raise ValueError("WSP39_BAD_CHECKPOINT")
        length = int.from_bytes(data[len(MAGIC):len(MAGIC) + 4], "big")
        body = data[len(MAGIC) + 4:-32]
        if len(body) != length or hashlib.sha256(body).digest() != data[-32:]:
            raise ValueError("WSP39_BAD_CHECKPOINT")
        try:
            j = json.loads(body.decode("ascii"))
            if type(j) is not dict or set(j) != {"schema", "width", "rows", "biases"} or j["schema"] != "wsp39.gf2.numeric.v1":
                raise ValueError("WSP39_BAD_SCHEMA")
            model = cls(j["width"], tuple(tuple(int(v, 16) for v in rows) for rows in j["rows"]), tuple(int(v, 16) for v in j["biases"]))
            if model.snapshot() != data:
                raise ValueError("WSP39_NONCANONICAL")
            return model
        except (ValueError, TypeError, KeyError, UnicodeError, OverflowError, RecursionError):
            raise ValueError("WSP39_BAD_CHECKPOINT") from None


def direct_acquire(width, probe, basis_indices):
    """Probes only; teacher's hidden matrices and labels are not provided."""
    if type(basis_indices) is not tuple or len(set(basis_indices)) != len(basis_indices) or any(type(i) is not int or not 0 <= i < width for i in basis_indices):
        raise ValueError("WSP39_BAD_PROBES")
    weights = []
    biases = []
    receipt = []
    for action in range(ACTIONS):
        zero = probe(action, 0)
        if type(zero) is not int or zero < 0 or zero.bit_length() > width:
            raise ValueError("WSP39_BAD_ORACLE_REPLY")
        biases.append(zero)
        receipt.append((action, -1, zero))
        rows = [0] * width
        for idx in basis_indices:
            answer = probe(action, 1 << idx)
            if type(answer) is not int or answer < 0 or answer.bit_length() > width:
                raise ValueError("WSP39_BAD_ORACLE_REPLY")
            receipt.append((action, idx, answer))
            diff = answer ^ zero
            while diff:
                lowest = diff & -diff
                rows[lowest.bit_length() - 1] |= (1 << idx)
                diff ^= lowest
        weights.append(tuple(rows))
    return NumericModel(width, tuple(weights), tuple(biases)), tuple(receipt)


class StrongGF2Control:
    """Independent sparse GF(2) ID fit from observed replies, same queries."""
    def __init__(self, width, transcript):
        if type(width) is not int or width not in (64, 128, 256, 512, 1024):
            raise ValueError("WSP39_BAD_WIDTH")
        if type(transcript) is not tuple:
            raise ValueError("WSP39_BAD_TRANSCRIPT")
        self.width = width
        zero = {}
        columns = {a: {} for a in range(ACTIONS)}
        for a, j, y in transcript:
            if type(a) is not int or not 0 <= a < ACTIONS or type(y) is not int or y < 0 or y.bit_length() > width:
                raise ValueError("WSP39_BAD_TRANSCRIPT")
            if j == -1:
                if a in zero: raise ValueError("WSP39_DUPLICATE_ZERO")
                zero[a] = y
            else:
                if type(j) is not int or not 0 <= j < width or j in columns[a]:
                    raise ValueError("WSP39_DUPLICATE_BASIS")
                columns[a][j] = y
        if len(zero) != ACTIONS:
            raise ValueError("WSP39_MISSING_ZERO")
        self.biases = tuple(zero[a] for a in range(ACTIONS))
        sources = []
        for a in range(ACTIONS):
            by_output = [[] for _ in range(width)]
            for input_bit, reply in columns[a].items():
                diff = reply ^ zero[a]
                for out in range(width):
                    if (diff >> out) & 1:
                        by_output[out].append(input_bit)
            sources.append(tuple(tuple(sorted(row)) for row in by_output))
        self.sources = tuple(sources)

    def apply(self, action, state):
        if type(action) is not int or not 0 <= action < ACTIONS or type(state) is not int or state < 0 or state.bit_length() > self.width:
            raise ValueError("WSP39_BAD_STATE_ACTION")
        out = self.biases[action]
        for bit, inputs in enumerate(self.sources[action]):
            parity = 0
            for source in inputs:
                parity ^= (state >> source) & 1
            out ^= parity << bit
        return out

    def rollout(self, start, actions):
        for a in actions:
            start = self.apply(a, start)
        return start

    def plan(self, start, goal):
        for a in range(ACTIONS):
            mid1 = self.apply(a, start)
            for b in range(ACTIONS):
                mid2 = self.apply(b, mid1)
                for c in range(ACTIONS):
                    if self.apply(c, mid2) == goal:
                        return (a, b, c)
        return None


def literal_observation_only(width, transcript):
    """Exact state->answer memorizer, intended negative-control on unfamiliar states."""
    found = {}
    for action, index, reply in transcript:
        state = 0 if index == -1 else (1 << index)
        found[(action, state)] = reply
    return found
