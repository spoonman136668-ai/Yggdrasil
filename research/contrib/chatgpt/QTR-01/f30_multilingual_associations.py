#!/usr/bin/env python3
"""F30 source-only first-party multilingual association intake.

All name strings are first-party source labels tagged with the actual source
language; no English translation, Qwen coordinate alignment, recipient model
weights, learning or protected science data.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

from f26_semantic_association import (
    NotAdmitted, PackedAssociationWeights, ITEM_RE, qnum, safe_label,
    validate_rows, dryrun, stable_json, digest,
)
from f27_versioned_entitydata import LiveEntityData

SCHEMA = "yggdrasil.qtr01.f30.language-preserving-cc0-associations.v1"
FROZEN = "a9f77a34f8cef3902ee6cb03fb1ef3fdad1c8ee0"
SEEDS = ("Q42", "Q5")
PREDICATES = ("P31", "P279", "P106", "P19", "P69", "P27", "P50", "P463")
LANGUAGES = ("en", "en-gb", "en-ca", "en-us", "fr", "de", "es", "it")
MAX_ENDPOINTS = 24
MAX_STATEMENTS = 160
MAX_SOURCE_BYTES = 16777216
MAX_RECEIPT = 393216
POLICY = Path(__file__).with_name("f30_prereg.json")


def preflight():
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if (policy.get("schema") != SCHEMA
        or policy.get("stage") != "FROZEN_BEFORE_SOURCE_CAPTURE_OR_IMPLEMENTATION"
        or policy.get("source") != "https://www.wikidata.org/wiki/Special:EntityData/{id}.json"
        or policy.get("allowed_seed_qids") != list(SEEDS)
        or policy.get("allowed_properties") != list(PREDICATES)
        or policy.get("allow_label_languages_in_preference_order") != list(LANGUAGES)
        or policy.get("max_source_statements") != MAX_STATEMENTS
        or policy.get("max_endpoint_queries") != MAX_ENDPOINTS
        or policy.get("source_per_get_max_bytes") != 4194304
        or policy.get("source_aggregate_max_bytes") != MAX_SOURCE_BYTES
        or policy.get("max_output_metadata_bytes") != MAX_RECEIPT
        or policy.get("source_network_retries") != 0
        or policy.get("fences", {}).get("no_model_weight_modification") is not True):
        raise NotAdmitted("F30_SOURCE_POLICY_DRIFT")
    return policy


def exact_source_label(entity):
    labels = entity.get("labels")
    if type(labels) is not dict:
        return None
    for language in LANGUAGES:
        record = labels.get(language)
        if type(record) is not dict or record.get("language") != language:
            continue
        raw = record.get("value")
        if type(raw) is not str:
            continue
        try:
            label = safe_label(raw)
        except NotAdmitted:
            continue
        return {"source_language": language, "label": label}
    return None


def extract_seed_claims(seeds):
    if set(seeds) != set(SEEDS):
        raise NotAdmitted("F30_WRONG_SOURCE_SEED_SET")
    rows = []
    rejected = 0
    seed_labels = {}
    for sid in SEEDS:
        entity = seeds[sid]
        name = exact_source_label(entity)
        if name is None:
            raise NotAdmitted("F30_SOURCE_SEED_HAS_NO_PERMITTED_LANGUAGE")
        seed_labels[sid] = name
        rev = entity.get("lastrevid")
        if type(rev) is not int or rev <= 0 or type(entity.get("claims")) is not dict:
            raise NotAdmitted("F30_NO_FIRST_PARTY_SEED_REVISION_OR_CLAIMS")
        for pid in PREDICATES:
            claims = entity["claims"].get(pid, [])
            if type(claims) is not list:
                raise NotAdmitted("F30_CLAIM_ARRAY_MALFORMED")
            for statement in claims:
                if type(statement) is not dict:
                    rejected += 1
                    continue
                claim_id = statement.get("id")
                if (type(claim_id) is not str
                    or not claim_id.startswith(sid + "$")
                    or len(claim_id) > 180
                    or statement.get("rank") not in ("normal", "preferred")
                    or "qualifiers" in statement):
                    rejected += 1
                    continue
                mainsnak = statement.get("mainsnak")
                if type(mainsnak) is not dict or mainsnak.get("snaktype") != "value":
                    rejected += 1
                    continue
                dv = mainsnak.get("datavalue")
                value = dv.get("value") if type(dv) is dict else None
                if (type(value) is not dict
                    or value.get("entity-type") != "item"
                    or type(value.get("id")) is not str
                    or not ITEM_RE.fullmatch(value["id"])):
                    rejected += 1
                    continue
                rows.append({
                    "s": sid, "p": pid, "o": value["id"],
                    "s_label": name["label"], "s_language": name["source_language"],
                    "source_claim": claim_id, "source_revision": rev,
                })
    rows.sort(key=lambda x: (
        qnum(x["s"], "Q"), qnum(x["p"], "P"), qnum(x["o"], "Q"), x["source_claim"]
    ))
    seen = set()
    unique = []
    for row in rows:
        triple = row["s"], row["p"], row["o"]
        if triple not in seen:
            seen.add(triple)
            unique.append(row)
    return unique[:MAX_STATEMENTS], {
        "eligible_unique_before_cap": len(unique),
        "rejected_witness_or_unqualified": rejected,
        "truncated": len(unique) > MAX_STATEMENTS,
        "seed_source_label_languages": {sid: seed_labels[sid]["source_language"] for sid in SEEDS},
    }


def endpoint_order(rows):
    connected = any(
        r["s"] == "Q42" and r["p"] == "P31" and r["o"] == "Q5"
        for r in rows
    )
    objects = {r["o"] for r in rows if r["o"] not in SEEDS}
    bridge = ({r["o"] for r in rows
               if r["s"] == "Q5" and r["p"] == "P279"}
              if connected else set())
    bridge &= objects
    order = lambda values: sorted(values, key=lambda q: qnum(q, "Q"))
    return (order(bridge) + order(objects - bridge))[:MAX_ENDPOINTS]


def complete_source_labels(rows, seeds, endpoints, properties):
    all_items = {**seeds, **endpoints}
    admitted = []
    excluded = Counter()
    for row in rows:
        s = exact_source_label(all_items[row["s"]])
        obj = all_items.get(row["o"])
        p = properties.get(row["p"])
        o = exact_source_label(obj) if obj is not None else None
        rel = exact_source_label(p) if p is not None else None
        if not s or not o or not rel:
            excluded["unlabeled_or_unfetched_edge"] += 1
            continue
        # No QID/English label guessed: preserve source locale for every field.
        admitted.append({
            "s": row["s"], "p": row["p"], "o": row["o"],
            "s_label": s["label"], "s_language": s["source_language"],
            "p_label": rel["label"], "p_language": rel["source_language"],
            "o_label": o["label"], "o_language": o["source_language"],
            "source_claim": row["source_claim"],
            "source_revision": row["source_revision"],
        })
    if not admitted:
        raise NotAdmitted("F30_NO_SOURCE_LABELED_RELATIONS")
    return admitted, dict(excluded)


def source_free_numeric_control(admitted):
    # F26's invariant is over integer Q-P-Q relations; language metadata is
    # deliberately kept out of the numeric payload, never silently dropped
    # from the independently stored source-provenance envelope.
    bare = [{key: r[key] for key in (
        "s", "p", "o", "s_label", "p_label", "o_label",
        "source_claim", "source_revision"
    )} for r in admitted]
    validate_rows(bare)
    summary = dryrun(bare)
    packed = PackedAssociationWeights.from_rows(bare)
    restored = PackedAssociationWeights.restore(packed.blob)
    if packed.blob != restored.blob or summary["numeric_carrier_bytes"] != len(packed.blob):
        raise NotAdmitted("F30_SOURCE_NUMERIC_COLD_DRIFT")
    return {
        "source_labeled_rows": len(admitted),
        "typed_integer_carrier_bytes": len(packed.blob),
        "numeric_carrier_sha256": sha256(packed.blob).hexdigest(),
        "source_label_languages": dict(sorted(Counter(
            lang for row in admitted for lang in (
                row["s_language"], row["p_language"], row["o_language"]
            )
        ).items())),
        "numeric_vs_equal_info_symbolic_2hop_parity": summary["equal_info_symbolic_control_parity"],
        "actual_observed_twohop_queries": summary["twohop_compositions_checked"],
        "canonical_cold_restore": summary["cold_restore_exact"],
        "neural_weights_modified": False,
        "generalization_or_causal_learning_proven": False,
    }


def capture(reader=None):
    preflight()
    reader = LiveEntityData() if reader is None else reader
    seeds, original_sha = {}, {}
    for sid in SEEDS:
        seeds[sid], original_sha[sid] = reader.fetch(sid)
    rows, inventory = extract_seed_claims(seeds)
    # Both source-bearing subjects must match their original exact
    # first-party revision-addressed current-source payload.
    for sid in SEEDS:
        pinned, digest_ = reader.fetch(sid, seeds[sid]["lastrevid"])
        if pinned != seeds[sid] or digest_ != original_sha[sid]:
            raise NotAdmitted("F30_PINNED_SOURCE_CLAIM_REVISION_DRIFT")
    endpoints = {}
    for qid in endpoint_order(rows):
        endpoints[qid] = reader.fetch(qid)[0]
    props = {}
    for pid in PREDICATES:
        props[pid] = reader.fetch(pid)[0]
    admitted, excluded = complete_source_labels(rows, seeds, endpoints, props)
    control = source_free_numeric_control(admitted)
    if reader.total_bytes > MAX_SOURCE_BYTES:
        raise NotAdmitted("F30_SOURCE_CAP_EXCEEDED")
    witness = {
        "schema": SCHEMA,
        "preregistration_commit": FROZEN,
        "source": "Wikidata Special:EntityData first-party JSON",
        "structured_data_license": "CC0",
        "source_license_url": "https://www.wikidata.org/wiki/Wikidata:Licensing",
        "source_only_development": True,
        "source_seed_ids": list(SEEDS),
        "source_predicate_ids": list(PREDICATES),
        "inventory": inventory, "excluded": excluded,
        "raw_first_party_source_receipts": reader.receipts,
        "total_source_bytes": reader.total_bytes,
        "source_rows": admitted,
        "source_rows_canonical_sha256": digest(admitted),
        "numeric_equal_info_control": control,
        "not_qwen_semantic_coordinate_alignment": True,
        "accepted_model_weights_modified": False,
        "scientific_pass": False,
        "disposition": "DEV_ADMITTED_SOURCE_ASSOCIATIONS_NOT_NATIVE_LEARNING",
    }
    if len(stable_json(witness)) > MAX_RECEIPT:
        raise NotAdmitted("F30_ARCHIVE_RECEIPT_TOO_LARGE")
    return witness


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--frozen-source-only", action="store_true", required=True)
    cli.add_argument("--output", required=True, type=Path)
    args = cli.parse_args()
    try:
        result = capture()
    except (NotAdmitted, ValueError, OSError, TimeoutError, UnicodeError, OverflowError) as exc:
        print("F30_FIRST_PARTY_SOURCE_BLOCKED=" + type(exc).__name__ + ":" + str(exc),
              file=sys.stderr)
        return 2
    raw = stable_json(result) + b"\n"
    args.output.write_bytes(raw)
    ctrl = result["numeric_equal_info_control"]
    print("F30_CC0_SOURCE_ASSOCIATIONS=PASS")
    print("F30_SOURCE_LABELED_TRIPLES=" + str(ctrl["source_labeled_rows"]))
    print("F30_SOURCE_LABEL_LANGUAGES=" + json.dumps(ctrl["source_label_languages"], sort_keys=True))
    print("F30_ACTUAL_TWOHOP_QUERIES=" + str(ctrl["actual_observed_twohop_queries"]))
    print("F30_CANONICAL_INTEGER_CARRIER_BYTES=" + str(ctrl["typed_integer_carrier_bytes"]))
    print("F30_SOURCE_RECEIPT_SHA256=" + sha256(raw).hexdigest())
    print("F30_NO_NATIVE_WEIGHT_EDIT_OR_SCIENTIFIC_PASS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
