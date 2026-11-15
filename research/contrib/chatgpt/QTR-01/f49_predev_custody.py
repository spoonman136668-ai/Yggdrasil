#!/usr/bin/env python3
"""F49 pre-DEV cold retention and ablation controls; no target outcomes.

The only data accepted here are caller-supplied public trajectory/outcome bits.
Cold source model weights are bound to an exact source-training fingerprint.
"""
from hashlib import sha256
from io import BytesIO
import json
import numpy as np

import f49_worlds as world
import f49_discrete_learners as discrete
import f49_conventional_controls as conventional
import f49_source_pretrain as source_fit

SCHEMA = "yggdrasil.qtr01.f49.predev-custody.v1"
ABLATIONS = ("no_retained_memory", "shuffled_public_outcomes", "random_proposals")


def _encode(tag, payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",",":"), allow_nan=False).encode("ascii")
    return tag + raw + b"." + sha256(tag+raw).hexdigest().encode("ascii")


def _decode(tag, raw):
    if type(raw) is not bytes or not raw.startswith(tag) or b"." not in raw:
        raise discrete.ControlRejected("F49_COLD_RESTORE_REJECTED")
    body, checksum = raw.rsplit(b".", 1)
    if sha256(body).hexdigest().encode("ascii") != checksum:
        raise discrete.ControlRejected("F49_COLD_RESTORE_REJECTED")
    try:
        return json.loads(body[len(tag):])
    except (ValueError, UnicodeError, TypeError) as exc:
        raise discrete.ControlRejected("F49_COLD_RESTORE_REJECTED") from exc


def _public_events(arm):
    if type(arm) is not discrete.PublicArm or arm.awaiting is not None:
        raise discrete.ControlRejected("F49_PUBLIC_CHECKPOINT_INVALID")
    recorded = (arm.engine.events if type(arm.engine) is discrete.ExactBankBayes
                else arm.engine.history)
    if len(recorded) != len(arm.used) or len(arm.used) > discrete.MAX_BUDGET:
        raise discrete.ControlRejected("F49_PUBLIC_HISTORY_INCONSISTENT")
    entries = []
    for index, (trajectory, observed) in zip(arm.used, recorded):
        if (type(index) is not int or not 0 <= index < len(arm.queries)
            or arm.queries[index] != trajectory):
            raise discrete.ControlRejected("F49_PUBLIC_HISTORY_BAD_TRAJECTORY")
        entries.append([index, list(discrete._check_bits(observed))])
    if len(set(z[0] for z in entries)) != len(entries):
        raise discrete.ControlRejected("F49_PUBLIC_REPLAYED_QUERY")
    return entries


def _public_fingerprint(arm):
    eng = arm.engine
    if type(eng) is discrete.GrammarLearner:
        return sha256(eng.cold_checkpoint()).hexdigest()
    state = {"mismatch": eng.mismatch,
             "events": [[list(t), list(y)] for t, y in eng.events]}
    return sha256(json.dumps(state, sort_keys=True, separators=(",",":")).encode()).hexdigest()


def cold_public(arm):
    """Reproducible public history and model evidence, with no evaluator labels."""
    entries = _public_events(arm)
    return _encode(b"F49P1", {
        "schema": SCHEMA, "kind": arm.kind, "size": arm.bank_size,
        "seed": arm.seed, "events": entries,
        "engine_fingerprint": _public_fingerprint(arm)})


def restore_public(raw):
    """Rebuild selection and evidence only from authenticated public history."""
    state = _decode(b"F49P1", raw)
    try:
        if state.get("schema") != SCHEMA:
            raise ValueError("invalid schema")
        arm = discrete.PublicArm(state["kind"], state["size"], state["seed"])
        for chosen, pair in state["events"]:
            index, _ = arm.select()
            if type(chosen) is not int or chosen != index:
                raise ValueError("noncanonical intervention sequence")
            arm.observe(index, pair)
        if (_public_fingerprint(arm) != state["engine_fingerprint"]
            or cold_public(arm) != raw):
            raise ValueError("state replay changed")
        return arm
    except (ValueError, TypeError, KeyError, IndexError, discrete.ControlRejected) as exc:
        raise discrete.ControlRejected("F49_COLD_RESTORE_REJECTED") from exc


def _source_fingerprint(pretrained):
    if type(pretrained) is not conventional.Pretrained:
        raise discrete.ControlRejected("F49_SOURCE_PRETRAIN_MISSING")
    arrays = source_fit._model_arrays(pretrained.kind, pretrained.model)
    digest = sha256()
    digest.update((pretrained.kind + "|" + str(pretrained.size)).encode())
    digest.update(int(pretrained.model.steps).to_bytes(8, "little"))
    for name, value in sorted(arrays.items()):
        digest.update(name.encode())
        digest.update(source_fit._canonical_bytes(value))
    return digest.hexdigest()


def cold_conventional(arm, pretrained):
    """Retain adapted parameters and Adam moments; no optimizer rerun on restore."""
    if (type(arm) is not conventional.ConventionalArm
        or type(pretrained) is not conventional.Pretrained
        or arm.kind != pretrained.kind or arm.size != pretrained.size
        or arm.awaiting is not None or len(arm.used) != len(arm.events)
        or len(arm.used) > discrete.MAX_BUDGET):
        raise discrete.ControlRejected("F49_CONVENTIONAL_CHECKPOINT_INVALID")
    entries = []
    for index, (tr, observed) in zip(arm.used, arm.events):
        if (type(index) is not int or not 0 <= index < len(arm.pool)
            or arm.pool[index] != tr):
            raise discrete.ControlRejected("F49_CONVENTIONAL_HISTORY_INVALID")
        entries.append([index, list(discrete._check_bits(observed))])
    if len(set(arm.used)) != len(arm.used):
        raise discrete.ControlRejected("F49_CONVENTIONAL_REPEATED_ACTION")
    meta = {"schema": SCHEMA, "kind": arm.kind, "size": arm.size,
            "seed": arm.seed, "source_sha256": _source_fingerprint(pretrained),
            "source_observations": pretrained.source_observations,
            "events": entries, "steps": int(arm.model.steps)}
    model_arrays = source_fit._model_arrays(arm.kind, arm.model)
    arrays = {"meta": np.frombuffer(json.dumps(meta, sort_keys=True,
                       separators=(",",":")).encode("ascii"), dtype=np.uint8)}
    for name, value in model_arrays.items():
        if value.dtype != np.float64 or not np.isfinite(value).all():
            raise discrete.ControlRejected("F49_NONFINITE_ADAPTED_WEIGHTS")
        arrays[name] = value
    buffer = BytesIO()
    np.savez_compressed(buffer, **arrays)
    content = buffer.getvalue()
    return b"F49N1" + content + sha256(b"F49N1" + content).digest()


def restore_conventional(raw, pretrained):
    """Bit-exact same-platform adapted state, without replaying target updates."""
    if (type(raw) is not bytes or len(raw) < 43 or
        not raw.startswith(b"F49N1") or
        sha256(raw[:-32]).digest() != raw[-32:]):
        raise discrete.ControlRejected("F49_COLD_RESTORE_REJECTED")
    try:
        with np.load(BytesIO(raw[5:-32]), allow_pickle=False) as saved:
            meta = json.loads(saved["meta"].tobytes().decode("ascii"))
            if (meta.get("schema") != SCHEMA or meta["kind"] != pretrained.kind
                or meta["size"] != pretrained.size
                or meta["source_sha256"] != _source_fingerprint(pretrained)
                or meta["source_observations"] != pretrained.source_observations):
                raise ValueError("source mismatch")
            arm = conventional.ConventionalArm(pretrained, meta["seed"])
            template = source_fit._model_arrays(arm.kind, arm.model)
            if set(saved.files) != {"meta", *template}:
                raise ValueError("wrong numerical array inventory")
            for name, expected in template.items():
                value = saved[name]
                if (value.dtype != np.float64 or value.shape != expected.shape
                    or not np.isfinite(value).all()):
                    raise ValueError("adapted weights invalid")
                if arm.kind == "conventional_logistic":
                    arm.model.w = value.copy()
                else:
                    {"p": arm.model.params, "m": arm.model.m,
                     "v": arm.model.v}[name[0]][int(name[1:])] = value.copy()
            steps = meta["steps"]
            if type(steps) is not int or steps < pretrained.model.steps:
                raise ValueError("optimizer step regression")
            arm.model.steps = steps
            for index, pair in meta["events"]:
                if (type(index) is not int or not 0 <= index < len(arm.pool)
                    or index in arm.used):
                    raise ValueError("bad observed action")
                pair = discrete._check_bits(pair)
                arm.used.append(index)
                arm.events.append((arm.pool[index], pair))
            if len(arm.used) > discrete.MAX_BUDGET or cold_conventional(arm, pretrained) != raw:
                raise ValueError("noncanonical cold image")
            return arm
    except (KeyError, TypeError, ValueError, OSError, OverflowError,
            UnicodeError, discrete.ControlRejected) as exc:
        raise discrete.ControlRejected("F49_COLD_RESTORE_REJECTED") from exc


class NativeAblation:
    """Control receives the same public bits, but the learning seam is removed."""

    def __init__(self, mode, bank_size, seed):
        world.freeze()
        if mode not in ABLATIONS:
            raise discrete.ControlRejected("F49_UNREGISTERED_ABLATION")
        self.mode = mode
        self.arm = discrete.PublicArm("native", bank_size, seed)
        if mode == "random_proposals":
            self.arm.engine = discrete.GrammarLearner(bank_size, random_proposals=True)
        self.actual_public_outcomes = []
        self.charged_proposals = 0

    def select(self):
        return self.arm.select()

    def observe(self, index, public_pair):
        pair = discrete._check_bits(public_pair)
        submitted = (pair[::-1] if self.mode == "shuffled_public_outcomes" else pair)
        self.arm.observe(index, submitted)
        self.charged_proposals += discrete.PROPOSALS_PER_EVENT
        self.actual_public_outcomes.append(pair)
        if self.mode == "no_retained_memory":
            self.arm.engine = discrete.GrammarLearner(self.arm.bank_size)

    @property
    def observed_bits(self):
        return 2 * len(self.actual_public_outcomes)


if __name__ == "__main__":
    print("F49_PREDEV_RETENTION_AND_NEGATIVE_ABLATIONS_READY_NO_TARGET_FIRST_USE")
