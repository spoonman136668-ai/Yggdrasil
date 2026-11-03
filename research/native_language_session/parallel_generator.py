"""Bounded parallel native output fields. No scientific language proof."""
import base64
import hashlib
import json
from pathlib import Path
import re
from research.native_language_session.runtime import SOURCE_BLOB, canonical, digest
from research.native_language_session.text_selector import NativeTextSelector, text_bytes

SCHEMA = "yggdrasil.native-parallel-byte-generator.v1"
SELECTOR_BLOB = "fd53e676118b48baa16ef31cd2e306ecd29f4015"
ENCODING = "independent-lsb0-byte-fields-complete-input.v1"
CAP = 1048576


def selector_identity():
    raw = Path(__file__).with_name("text_selector.py").read_bytes()
    if hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() != SELECTOR_BLOB:
        raise ValueError("GENERATOR_SELECTOR_SOURCE_DRIFT")


def decode(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= CAP:
        raise ValueError("GENERATOR_JSON_SIZE_INVALID")
    def unique(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError("GENERATOR_DUPLICATE_FIELD")
            result[k] = v
        return result
    try:
        value = json.loads(raw, object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("GENERATOR_NONFINITE_JSON")))
        def bounded(x, depth=0):
            if depth > 32:
                raise ValueError("GENERATOR_JSON_DEPTH_INVALID")
            if isinstance(x, dict):
                for v in x.values():
                    bounded(v, depth + 1)
            elif isinstance(x, list):
                for v in x:
                    bounded(v, depth + 1)
        bounded(value)
        return value
    except RecursionError as exc:
        raise ValueError("GENERATOR_JSON_DEPTH_INVALID") from exc


def train_field(examples, labels):
    if len(set(labels)) == 1:
        return {"kind": "constant", "value": int(labels[0])}
    model = NativeTextSelector.train([{"input": x["input"], "response": y} for x, y in zip(examples, labels)])
    return {"kind": "native", "value": 0, "model": base64.b64encode(model.checkpoint()).decode("ascii")}


def read_field(field, text):
    if field["kind"] == "constant":
        return field["value"], []
    model = NativeTextSelector.restore(base64.b64decode(field["model"], validate=True))
    result = model.predict(text)
    return int(result["response"]), result["native_scores"]


class NativeParallelGenerator:
    @classmethod
    def train(cls, examples):
        selector_identity()
        if type(examples) is not list or not 2 <= len(examples) <= 8:
            raise ValueError("GENERATOR_EXAMPLE_COUNT_INVALID")
        inputs, outputs = [], []
        for x in examples:
            if type(x) is not dict or set(x) != {"input", "response"}:
                raise ValueError("GENERATOR_EXAMPLE_FIELDS_INVALID")
            inputs.append(text_bytes(x["input"], 128))
            outputs.append(text_bytes(x["response"], 16))
        if sum(map(len, inputs)) > 512:
            raise ValueError("GENERATOR_INPUT_BUDGET_EXCEEDED")
        width = max(map(len, outputs))
        labels = [[str(((raw[pos] if pos < len(raw) else 0) >> bit) & 1) for raw in outputs]
                  for pos in range(width) for bit in range(8)]
        if all(len(set(x)) == 1 for x in labels):
            raise ValueError("GENERATOR_NO_NATIVE_VARIABLE_BIT_FIELD")
        # All examples and resource bounds have been checked before updates.
        obj = cls()
        obj.width, obj.example_count = width, len(examples)
        obj.input_bytes = sum(map(len, inputs))
        obj.training_sha256 = digest(examples)
        obj.response_hashes = sorted({hashlib.sha256(x).hexdigest() for x in outputs})
        obj.length = train_field(examples, [str(len(x)) for x in outputs])
        obj.fields = [train_field(examples, x) for x in labels]
        return obj

    def generate(self, text):
        text_bytes(text, 128)
        length, length_scores = read_field(self.length, text)
        values, scores = [], []
        for field in self.fields:
            value, score = read_field(field, text)  # Same input, no generated prefix.
            values.append(value)
            scores.append(score)
        full = bytes(sum(values[pos * 8 + bit] << bit for bit in range(8)) for pos in range(self.width))
        length_valid = 1 <= length <= self.width
        candidate = full[:length] if length_valid else full
        try:
            response = candidate.decode("utf-8", errors="strict")
            utf8_valid = True
        except UnicodeDecodeError:
            response, utf8_valid = None, False
        valid = length_valid and utf8_valid
        return {"response": response if valid else None, "raw_hex": candidate.hex(),
                "predicted_length": length, "length_valid": length_valid,
                "utf8_valid": utf8_valid, "valid_output": valid,
                "candidate_status": "VALID_UTF8" if valid else "INVALID_GENERATED_CANDIDATE",
                "seen_training_response": hashlib.sha256(candidate).hexdigest() in self.response_hashes,
                "output_mode": "parallel-native-byte-field", "whole_response_bank": False,
                "language_proof": False, "length_scores": length_scores, "bit_scores": scores}

    def checkpoint(self):
        p = {"schema": SCHEMA, "source_blob": SOURCE_BLOB, "selector_blob": SELECTOR_BLOB,
             "encoding": ENCODING, "width": self.width, "example_count": self.example_count,
             "input_bytes": self.input_bytes, "training_sha256": self.training_sha256,
             "response_hashes": self.response_hashes, "length": self.length, "fields": self.fields}
        raw = canonical({"payload": p, "sha256": digest(p)})
        if len(raw) > CAP:
            raise ValueError("GENERATOR_CHECKPOINT_CAP_EXCEEDED")
        return raw

    @classmethod
    def restore(cls, raw):
        selector_identity()
        doc = decode(raw)
        if type(doc) is not dict or set(doc) != {"payload", "sha256"}:
            raise ValueError("GENERATOR_ENVELOPE_INVALID")
        p = doc["payload"]
        keys = {"schema", "source_blob", "selector_blob", "encoding", "width", "example_count", "input_bytes", "training_sha256", "response_hashes", "length", "fields"}
        if (type(p) is not dict or set(p) != keys or p["schema"] != SCHEMA
                or p["source_blob"] != SOURCE_BLOB or p["selector_blob"] != SELECTOR_BLOB
                or p["encoding"] != ENCODING or doc["sha256"] != digest(p)
                or type(p["width"]) is not int or not 1 <= p["width"] <= 16
                or type(p["example_count"]) is not int or not 2 <= p["example_count"] <= 8
                or type(p["input_bytes"]) is not int or not p["example_count"] <= p["input_bytes"] <= min(512, 128 * p["example_count"])
                or type(p["training_sha256"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", p["training_sha256"])
                or type(p["fields"]) is not list or len(p["fields"]) != p["width"] * 8
                or type(p["response_hashes"]) is not list or not 2 <= len(p["response_hashes"]) <= p["example_count"]):
            raise ValueError("GENERATOR_IDENTITY_OR_SHAPE_INVALID")
        hashes = p["response_hashes"]
        if any(type(h) is not str or not re.fullmatch(r"[0-9a-f]{64}", h) for h in hashes) or hashes != sorted(set(hashes)):
            raise ValueError("GENERATOR_RESPONSE_DIGESTS_INVALID")
        def field_valid(field, is_length):
            if type(field) is not dict or type(field.get("value")) is not int:
                raise ValueError("GENERATOR_FIELD_INVALID")
            if field.get("kind") == "constant":
                if set(field) != {"kind", "value"} or (field["value"] != p["width"] if is_length else field["value"] not in (0, 1)):
                    raise ValueError("GENERATOR_CONSTANT_INVALID")
                return
            if field.get("kind") != "native" or set(field) != {"kind", "value", "model"} or field["value"] != 0 or type(field["model"]) is not str:
                raise ValueError("GENERATOR_NATIVE_FIELD_INVALID")
            model = NativeTextSelector.restore(base64.b64decode(field["model"], validate=True))
            expected = [str(n) for n in range(1, p["width"] + 1)] if is_length else ["0", "1"]
            if any(v not in expected for v in model.responses) or (is_length and str(p["width"]) not in model.responses) or (not is_length and model.responses != ["0", "1"]):
                raise ValueError("GENERATOR_FIELD_DOMAIN_INVALID")
            if any(b.sequence != 2 * p["input_bytes"] for b in model.banks):
                raise ValueError("GENERATOR_NATIVE_COUNTER_INVALID")
        field_valid(p["length"], True)
        for field in p["fields"]:
            field_valid(field, False)
        if not any(x["kind"] == "native" for x in p["fields"]):
            raise ValueError("GENERATOR_NO_NATIVE_VARIABLE_BIT_FIELD")
        obj = cls()
        for name in ("width", "example_count", "input_bytes", "training_sha256", "response_hashes", "length", "fields"):
            setattr(obj, name, p[name])
        return obj


def main():
    import sys
    state = None
    while True:
        raw = sys.stdin.buffer.readline(CAP + 1)
        if not raw:
            return 0
        if len(raw) > CAP:
            return 1
        try:
            req = decode(raw)
            allowed = {"train": {"op", "examples"}, "generate": {"op", "input"}, "checkpoint": {"op"}, "restore": {"op", "checkpoint"}}
            if type(req) is not dict or type(req.get("op")) is not str or req["op"] not in allowed or set(req) != allowed[req["op"]]:
                raise ValueError("GENERATOR_REQUEST_FIELDS_INVALID")
            op = req["op"]
            if op in ("train", "restore"):
                if state is not None:
                    raise ValueError("SILENT_STATE_REPLACEMENT_DENIED")
                state = NativeParallelGenerator.train(req["examples"]) if op == "train" else NativeParallelGenerator.restore(canonical(req["checkpoint"]))
                result = {"ready": True, "maximum_output_bytes": state.width}
            else:
                if state is None:
                    raise ValueError("TRAIN_OR_RESTORE_REQUIRED")
                result = state.generate(req["input"]) if op == "generate" else {"checkpoint": decode(state.checkpoint())}
            print(canonical({"ok": result.get("valid_output", True), "result": result, "language_proof": False}).decode(), flush=True)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            print(canonical({"ok": False, "error": str(exc), "language_proof": False}).decode(), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
