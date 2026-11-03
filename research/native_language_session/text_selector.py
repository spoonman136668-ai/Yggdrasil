"""Native closed-response text selector; no novel-string generation claim."""
import hashlib
import re
from research.native_language_session.runtime import NativeSession, SOURCE_BLOB, canonical, decode, digest

SCHEMA = "yggdrasil.native-whole-response-selector.v1"
ENCODING = "utf8-high-low-nibbles-original-ab-contexts.v1"


def text_bytes(value, maximum):
    if type(value) is not str:
        raise ValueError("TEXT_REQUIRED")
    raw = value.encode("utf-8")
    if not 1 <= len(raw) <= maximum:
        raise ValueError("TEXT_SIZE_INVALID")
    return raw


def frames(text):
    for byte in text_bytes(text, 256):
        for context, shift in (("A", 4), ("B", 0)):
            yield context, tuple(bool(byte & (1 << (shift + bit))) for bit in range(4))


def validate_examples(examples):
    if type(examples) is not list or not 2 <= len(examples) <= 16:
        raise ValueError("EXAMPLE_COUNT_INVALID")
    total = 0
    for example in examples:
        if type(example) is not dict or set(example) != {"input", "response"}:
            raise ValueError("EXAMPLE_FIELDS_INVALID")
        total += len(text_bytes(example["input"], 256))
        text_bytes(example["response"], 128)
    responses = sorted({x["response"] for x in examples})
    if total > 1024 or not 2 <= len(responses) <= 8:
        raise ValueError("TRAINING_CAPACITY_INVALID")
    return responses


class NativeTextSelector:
    @classmethod
    def train(cls, examples):
        responses = validate_examples(examples)  # All input before native updates.
        obj = cls()
        obj.responses = responses
        obj.banks = [NativeSession() for _ in responses]
        obj.training_sha256 = hashlib.sha256(canonical(examples)).hexdigest()
        for example in examples:
            for context, sensors in frames(example["input"]):
                for response, bank in zip(obj.responses, obj.banks):
                    selected = bank.predict(context, sensors)
                    bank.feedback(selected["query_id"], example["response"] == response, 2)
        return obj

    def predict(self, text):
        events = list(frames(text))
        # All decisions come from original bounded-neighbor local-cell reads.
        scores = [sum(bank.native.predict(ctx, sensors) for ctx, sensors in events) / len(events)
                  for bank in self.banks]
        best = max(range(len(scores)), key=lambda i: scores[i])
        return {"response": self.responses[best], "responses": list(self.responses),
                "native_scores": scores, "output_mode": "closed-response-selection",
                "language_proof": False, "novel_string_generation": False}

    def checkpoint(self):
        payload = {"schema": SCHEMA, "encoding": ENCODING, "source_blob": SOURCE_BLOB,
                   "responses": self.responses, "training_sha256": self.training_sha256,
                   "banks": [decode(bank.checkpoint()) for bank in self.banks]}
        raw = canonical({"payload": payload, "sha256": digest(payload)})
        if len(raw) > 131072:
            raise ValueError("TEXT_CHECKPOINT_CAP_EXCEEDED")
        return raw

    @classmethod
    def restore(cls, raw):
        doc = decode(raw)
        if type(doc) is not dict or set(doc) != {"payload", "sha256"}:
            raise ValueError("TEXT_ENVELOPE_INVALID")
        p = doc["payload"]
        if (type(p) is not dict or set(p) != {"schema", "encoding", "source_blob", "responses", "training_sha256", "banks"}
                or p["schema"] != SCHEMA or p["encoding"] != ENCODING
                or p["source_blob"] != SOURCE_BLOB or doc["sha256"] != digest(p)
                or type(p["responses"]) is not list or not 2 <= len(p["responses"]) <= 8
                or type(p["banks"]) is not list or len(p["banks"]) != len(p["responses"])
                or type(p["training_sha256"]) is not str
                or not re.fullmatch(r"[0-9a-f]{64}", p["training_sha256"])):
            raise ValueError("TEXT_IDENTITY_OR_INTEGRITY_INVALID")
        for response in p["responses"]:
            text_bytes(response, 128)
        if sorted(set(p["responses"])) != p["responses"]:
            raise ValueError("RESPONSE_BANK_INVALID")
        obj = cls()
        obj.responses = p["responses"]
        obj.training_sha256 = p["training_sha256"]
        obj.banks = [NativeSession.restore(canonical(x)) for x in p["banks"]]
        sequences = {x.sequence for x in obj.banks}
        if len(sequences) != 1 or not 4 <= next(iter(sequences)) <= 2048:
            raise ValueError("NATIVE_TRAINING_COUNTER_INVALID")
        return obj


def main():
    import sys
    state = None
    while True:
        raw = sys.stdin.buffer.readline(131073)
        if not raw:
            return 0
        if len(raw) > 131072:
            return 1
        try:
            req = decode(raw)
            fields = {"train": {"op", "examples"}, "predict": {"op", "input"},
                      "checkpoint": {"op"}, "restore": {"op", "checkpoint"}}
            if type(req) is not dict or type(req.get("op")) is not str or req["op"] not in fields or set(req) != fields[req["op"]]:
                raise ValueError("TEXT_REQUEST_FIELDS_INVALID")
            op = req["op"]
            if op in ("train", "restore"):
                if state is not None:
                    raise ValueError("SILENT_STATE_REPLACEMENT_DENIED")
                state = NativeTextSelector.train(req["examples"]) if op == "train" else NativeTextSelector.restore(canonical(req["checkpoint"]))
                result = {"ready": True, "response_count": len(state.responses)}
            else:
                if state is None:
                    raise ValueError("TRAIN_OR_RESTORE_REQUIRED")
                result = state.predict(req["input"]) if op == "predict" else {"checkpoint": decode(state.checkpoint())}
            print(canonical({"ok": True, "result": result, "language_proof": False}).decode(), flush=True)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            print(canonical({"ok": False, "error": str(exc), "language_proof": False}).decode(), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
