"""Frozen WSP17 retention assay; imperfect learned operations are NOT filtered."""
import hashlib
import importlib.util
import json
import platform
import sys
import time
from pathlib import Path
from synaptic_bank import SynapticBank, PlasticNand, context, SLOTS, WIDTH
sys.path.append(str(Path(__file__).resolve().parents[1]/"WSP-16"))
from neutral import NeutralNand, SEEDS, PUBLIC

GROUPS = ((0,3,5,9), (14,19,23,31))


def trainer():
    path = Path(__file__).resolve().parents[1]/"WSP-16"/"run_dev.py"
    spec = importlib.util.spec_from_file_location("wsp17_frozen_wsp16_evaluator", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def run():
    start = time.perf_counter()
    ref = trainer()
    sequential = symbolic_agreement = cold = collateral = rejection = erased = unknown = 0
    sequential_total = collateral_total = old_correct = repair_correct = 0
    public_fit = public_total = trained_fit = trained_repair_fit = converged = 0
    single_slot_wrong = trained_steps = 0
    checkpoints = []
    times = {k: 0. for k in ("acquisition", "bank_writes", "bank_inference", "checkpoint", "repair", "trained")}
    construction_proposals = repair_proposals = 0
    construction_gates = repair_gates = 0
    for seed in SEEDS:
        for group in GROUPS:
            bank = SynapticBank()
            symbolic = {}  # independent CONTROL ONLY, never passed to bank
            observation_buffers = []
            for key, signature in enumerate(group):
                original = tuple((context(i), (signature >> j) & 1) for j, i in enumerate(PUBLIC))
                tick = time.perf_counter()
                initial = PlasticNand().learn(original, seed)
                obs = original+((context(3), 1-initial.predict(context(3))),)
                acquired = NeutralNand(initial.snapshot()).adapt(obs, seed)
                times["acquisition"] += time.perf_counter()-tick
                construction_proposals += initial.proposals+acquired.proposals
                construction_gates += initial.gate_evaluations+acquired.gate_evaluations
                observation_buffers.append(obs)
                outputs = tuple(acquired.predict(context(i)) for i in range(8))
                symbolic[key] = outputs
                public_fit += sum(acquired.predict(x) == y for x, y in obs)
                public_total += 6
                tick = time.perf_counter()
                if bank.write(context(key), acquired.rows) != 1:
                    raise AssertionError("WSP17_WRITE_REJECTED")
                times["bank_writes"] += time.perf_counter()-tick
                tick = time.perf_counter()
                for prior in range(key+1):
                    for i in range(8):
                        got = bank.predict(context(prior), context(i))
                        sequential += got == symbolic[prior][i]
                        sequential_total += 1
                        symbolic_agreement += got == symbolic[prior][i]
                times["bank_inference"] += time.perf_counter()-tick
                tick = time.perf_counter()
                pred, n, bce = ref.trained_six(obs)
                times["trained"] += time.perf_counter()-tick
                if bce > .02:
                    raise AssertionError("WSP17_TRAINED_NOT_CONVERGED")
                converged += 1; trained_steps += n
                trained_fit += sum(pred[i] == y for i, (_x, y) in zip(PUBLIC+(3,), obs))
            before = bank.snapshot()
            for key in range(4):
                for i in range(8):
                    single_slot_wrong += symbolic[3][i] != symbolic[key][i]
            tick = time.perf_counter()
            cold_bank = SynapticBank.restore(before)
            for key in range(4):
                cold += all(cold_bank.predict(context(key), context(i)) == symbolic[key][i] for i in range(8))
            if cold_bank.snapshot() != before:
                raise AssertionError("WSP17_COLD_BYTES")
            times["checkpoint"] += time.perf_counter()-tick
            for key in range(4,8):
                unknown += bank.predict(context(key), context(0)) is None
            accepted = bank.write(context(4), acquired.rows)
            rejection += accepted == 0 and bank.snapshot() == before
            for key in range(4,8):
                unknown += bank.predict(context(key), context(0)) is None
            # Selective numerical retrieval and replacement; no collateral
            # task's graph is supplied to the repair learner.
            present, rows = bank.read(context(1))
            initial_repair = PlasticNand(); initial_repair.rows = rows
            target = 1-initial_repair.predict(context(3))
            repair_obs = observation_buffers[1][:5]+((context(3), target),)
            tick = time.perf_counter()
            repaired = NeutralNand(initial_repair.snapshot()).adapt(repair_obs, seed)
            times["repair"] += time.perf_counter()-tick
            repair_proposals += repaired.proposals
            repair_gates += repaired.gate_evaluations
            if present != 1 or bank.write(context(1), repaired.rows) != 1:
                raise AssertionError("WSP17_REPAIR_ROUTE")
            repair_correct += repaired.predict(context(3)) == target
            for key in (0,2,3):
                for i in range(8):
                    collateral += bank.predict(context(key), context(i)) == symbolic[key][i]
                    collateral_total += 1
                # Real synaptic identity, beyond behavioral agreement.
                if bank.read(context(key))[1] != cold_bank.read(context(key))[1]:
                    raise AssertionError("WSP17_COLLATERAL_SYNAPTIC_CHANGE")
            symbolic[1] = tuple(repaired.predict(context(i)) for i in range(8))
            for key in range(4):
                for i in range(8):
                    symbolic_agreement += bank.predict(context(key), context(i)) == symbolic[key][i]
            tick = time.perf_counter()
            pred, n, bce = ref.trained_six(repair_obs)
            times["trained"] += time.perf_counter()-tick
            if bce > .02:
                raise AssertionError("WSP17_REPAIR_BASELINE_NOT_CONVERGED")
            converged += 1; trained_steps += n
            trained_repair_fit += sum(pred[i] == y for i, (_x,y) in zip(PUBLIC+(3,), repair_obs))
            checkpoints.append(bank.snapshot())
            blank = SynapticBank()
            erased += all(blank.predict(context(key), context(i)) is None for key in range(4) for i in range(8))
    supported = (sequential == sequential_total == 640 and collateral == collateral_total == 192
                 and cold == 32 and rejection == erased == 8 and unknown == 64)
    required = (supported and symbolic_agreement == 896 and converged == 40
                and trained_fit == public_total == 192 and trained_repair_fit == 48
                and SLOTS*(WIDTH+4) == 316)
    report = {"schema": "wsp17.public-dev.v1", "engineering": "PASS" if required else "FAIL",
              "frozen_retention_hypothesis": "DEV_SUPPORTED" if supported else "SCIENTIFIC_NEGATIVE",
              "scientific_classification": "TIE with exact symbolic storage; no independent scientific superiority",
              "banks": 8, "stored_operations": 32, "sequential_retained": sequential,
              "sequential_total": sequential_total, "cold_restored_operations": cold,
              "collateral_retained_after_repair": collateral, "collateral_total": collateral_total,
              "symbolic_storage_agreement": symbolic_agreement, "symbolic_storage_queries": 896,
              "full_bank_rejection_preserved": rejection, "unknown_key_abstentions": unknown,
              "erasure_effective_banks": erased, "single_slot_output_mismatches_of256": single_slot_wrong,
              "acquired_public_correct": public_fit, "acquired_public_total": public_total,
              "repair_witness_correct_of8": repair_correct, "trained_public_correct": trained_fit,
              "trained_repair_public_correct_of48": trained_repair_fit, "trained_converged_of40": converged,
              "trained_steps": trained_steps, "resident_binary_scalars": SLOTS*(WIDTH+4),
              "checkpoint_bytes": len(checkpoints[0]), "external_replay_buffer_examples_per_bank": 24,
              "construction_proposals": construction_proposals, "construction_nand_evaluations": construction_gates,
              "repair_proposals": repair_proposals, "repair_nand_evaluations": repair_gates,
              "gradient_steps_candidate": 0,
              "checkpoint_digest_sha256": hashlib.sha256(b"".join(checkpoints)).hexdigest(),
              "seconds": {k:round(v,6) for k,v in times.items()}, "total_seconds":round(time.perf_counter()-start,6),
              "environment": {"python":sys.version, "platform":platform.platform()},
              "limits":"Routing key supplied, not learned; four times single-slot graph capacity. Python supplies generic simulation/serialization/noise and externally retained experiences. Every task-specific resident graph/key/occupancy is numeric synaptic state. Stored imperfect outputs and errors are preserved, not solved by memory. Symbolic storage ties; no unknown-family transfer or matched total-cost superiority."}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    run()
