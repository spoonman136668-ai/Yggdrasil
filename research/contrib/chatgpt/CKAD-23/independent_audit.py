"""Independent CKAD23 raw-evidence audit, without importing the native learner."""
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "CKAD-22"
SOURCE = HERE.parent / "CKAD-20" / "synthetic_world.py"
sys.path.insert(0, str(HERE.parent / "CKAD-20"))
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
spec = importlib.util.spec_from_file_location("ckad23_exact_reference", PREVIOUS / "independent_audit.py")
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)
canonical, sha = ref.canonical, ref.sha

def require(condition, label):
    if not condition:
        raise RuntimeError("CKAD23_INDEPENDENT_" + label)

def event_id(source, cohort, seed, index, arm):
    return sha(canonical(["ckad23", source, cohort, seed, index, arm]))

def held_random(cohort, seed, index):
    digest = sha256(f"ckad23/actions-v1/{cohort}/held-matched/{seed}/{index}".encode("ascii")).digest()
    return digest[0] & 1, digest[1] & 1

def evaluate_exact(mixture, source_seed, count, world, held_count):
    cohort = f"ckad23-held-{count}"
    total = 0
    transition_loss, terminal_loss = Fraction(), Fraction()
    disagreements = distinct = 0
    for i in range(held_count):
        episode = ref.make_episode(cohort=cohort, seed=source_seed, index=i, **world)
        view, alternate = ref.public_views(episode)
        distinct += view != alternate
        plan = mixture.plan(view)
        played = ref.rollout(episode, lambda _: plan["first_action"],
            lambda _, first, state: plan["second_actions"][first][state])
        total += played["y"]
        x1, x2 = held_random(cohort, source_seed, i)
        observed = ref.rollout(episode, lambda _: x1, lambda *_: x2)
        s2, y = observed["s2"], observed["y"]
        p, q = mixture.forecast(view, x1), mixture.forecast(view, x1, s2, x2)
        transition_loss += (p - s2) ** 2
        terminal_loss += (q - y) ** 2
        disagreements += int(p != mixture.forecast(alternate, x1))
        disagreements += int(q != mixture.forecast(alternate, x1, s2, x2))
    def ratio(f):
        return [f.numerator, f.denominator]
    return {"episodes": held_count, "reward_sum": total,
            "transition_brier": ratio(transition_loss / held_count),
            "terminal_brier": ratio(terminal_loss / held_count),
            "pooled_brier": ratio((transition_loss + terminal_loss) / (2 * held_count)),
            "view_disagreements": disagreements,
            "view_comparisons": 2 * held_count,
            "distinct_view_episodes": distinct}

def audit(root=HERE):
    protocol = json.loads((HERE / "prereg.json").read_text(encoding="ascii"))
    result = json.loads((root / "campaign-result.json").read_text(encoding="ascii"))
    require(sha(SOURCE.read_bytes()) == protocol["source_sha256"] == result["source_sha256"],
            "SOURCE_PIN")
    require(result["scientific_pass"] is False and result["accepted_native"] is False
            and result["deployment"] == "NONE", "SCIENTIFIC_FENCE")
    require([row["seed"] for row in result["seeds"]] == protocol["seeds"], "SEEDS")
    source = protocol["source_sha256"]
    for case in result["seeds"]:
        seed = case["seed"]
        raw = (root / case["final_checkpoint_name"]).read_bytes()
        require(sha(raw) == case["final_checkpoint_sha256"], "FULL_NATIVE_STATE_PIN")
        model = json.loads(raw)
        episode = json.loads(model["experience_ascii"])
        require(episode["schema"] == "yggdrasil.ckad.native-episode-experience.v4",
                "STREAM_SCHEMA")
        original = json.loads((PREVIOUS / f"seed-{seed}-expanded-native.json").read_bytes())
        require({k: v for k, v in model.items() if k != "experience_ascii"}
                == {k: v for k, v in original.items() if k != "experience_ascii"},
                "LEGACY_STATE_PRESERVED")
        original_events = json.loads(original["experience_ascii"])["episodes"]
        events = episode["episodes"]
        require(len(original_events) == 448 and len(events) == 640, "EPISODE_COUNT")
        require(events[:448] == original_events, "ORIGINAL_PREFIX")
        require(len({event[0] for event in events}) == len(events), "EVENT_IDENTITY")
        mixture = ref.Mixture(original_events, novel=True)
        score = Fraction(1)
        detections = []
        held = protocol["budgets"]["held_episodes_per_checkpoint"]
        snapshots = {s["count"]: s for s in case["stream"]}
        require(sorted(snapshots) == protocol["budgets"]["checkpoints"], "CHECKPOINTS")
        source_seed = seed + protocol["source_seed_offset"]
        for n in range(193):
            if n in snapshots:
                row = snapshots[n]
                world = protocol["phases"][0 if n == 0 else (n - 1) // 48]
                expected = evaluate_exact(mixture, source_seed, n, world, held)
                require(row["evaluation"]["detector_active"] == expected
                        and row["evaluation"]["exact_mixture"] == expected,
                        "HELD_EXACT_REFERENCE")
                require(row["active_detections"] == detections, "DETECTION_TRACE")
                require(row["active_score"] == [score.numerator, score.denominator],
                        "SCORE_TRACE")
                require(row["context_start"] == mixture.start,
                        "CONTEXT_START_TRACE")
            if n == 192:
                break
            event = events[448 + n]
            expect_id = event_id(source, "ckad23-stream", source_seed, n, "active")
            require(event[0] == expect_id, "ACTIVE_RECEIPT_ID")
            world = protocol["phases"][n // 48]
            fixture = ref.make_episode(cohort="ckad23-stream", seed=source_seed,
                                       index=n, **world)
            view = ref.public_views(fixture)
            require(event[1] == [list(x) for x in view], "PUBLIC_VIEWS")
            _, _, x1, s2, x2, y = event
            observed = ref.rollout(fixture, lambda _: x1, lambda *_: x2)
            require([observed[k] for k in ("x1", "s2", "x2", "y")] == [x1, s2, x2, y],
                    "ACTUAL_ACTION_CONSEQUENCE")
            p = mixture.forecast(view[0], x1)
            q = mixture.forecast(view[0], x1, s2, x2)
            likelihood = (p if s2 else 1 - p) * (q if y else 1 - q)
            require(likelihood > 0, "PREQUENTIAL_LIKELIHOOD")
            mixture.add(event)
            score = max(Fraction(1), score / (4 * likelihood))
            if score >= 16 and 449 + n - mixture.start >= 8:
                detections.append({"event_id": event[0], "evidence_count": 449 + n,
                                   "score": [score.numerator, score.denominator]})
                mixture = ref.Mixture(events[:449 + n], novel=True)
                score = Fraction(1)
        require(case["active_detections"] == detections, "FINAL_DETECTION_RECEIPT")
        require(episode["context_start"] == mixture.start
                and episode["stream_start"] == 448, "FINAL_NATIVE_STREAM_BOUNDS")
        require(case["final_checkpoint_bytes"] == len(raw), "STATE_SIZE")
    print(json.dumps({"independent_audit": "PASS", "seeds": protocol["seeds"],
                      "stream_episodes_per_seed": 192}, sort_keys=True))

if __name__ == "__main__":
    audit(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE)
