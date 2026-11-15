"""Frozen ST4 source: actual balanced delayed-intervention branch pairs.

Development-only in-house causal task. PRIVATE law/mask/pending/seed/trial
belong to this SOURCE, not a learner input. The public interface of an
eventual learner is an eight-bit observation, prior *observed* consequence,
prior announced action and current announced action. The evaluator may
compare true source branches after BOTH source steps, never as model labels.

Neither ST3 model nor source is imported or modified.
"""
import hashlib
import json

SCHEMA = "yggdrasil.nci04.st4.paired-public-interventions-source.v1"
PROBES = (0, 1, 3)
TREATMENT_ACTION = 2
CONTROL_ACTION = 3
TRIALS = 16
SOURCE_ACTIONS_PER_TRIAL = 4


def digest(label):
    if type(label) is not str:
        raise ValueError("ST4_SOURCE_DIGEST_LABEL")
    return hashlib.sha256(label.encode("utf-8")).digest()


def public_bits(byte):
    if type(byte) is not int or not 0 <= byte <= 255:
        raise ValueError("ST4_SOURCE_INVALID_BYTE")
    return tuple((byte >> bit) & 1 for bit in range(8))


def check_public(bits):
    if (type(bits) not in (tuple,list) or len(bits) != 8 or
        any(type(x) is not int or x not in (0,1) for x in bits)):
        raise ValueError("ST4_SOURCE_INVALID_PUBLIC_BITS")
    return sum(bit << index for index,bit in enumerate(bits))


def rotation(law):
    if type(law) is not int or law < 0:
        raise ValueError("ST4_SOURCE_BAD_LAW")
    return 1 + digest("ST4-rot|" + str(law))[0] % 3


def immediate_mask(law, action):
    if type(law) is not int or law < 0 or action not in (0,1):
        raise ValueError("ST4_SOURCE_BAD_IMMEDIATE")
    return digest("ST4-mask|" + str(law) + "|" + str(action))[0]


def delayed_mask(law):
    if type(law) is not int or law < 0:
        raise ValueError("ST4_SOURCE_BAD_DELAY")
    return digest("ST4-delay|" + str(law))[0]


def rotate_byte(n, r):
    if (type(n) is not int or n not in range(256) or
        type(r) is not int or r not in (1,2,3)):
        raise ValueError("ST4_SOURCE_BAD_ROTATE")
    return ((n << r) | (n >> (8-r))) & 255


def blind_design(seed, trial):
    """Actor never receives source law, cause, model forecast or target."""
    if (type(seed) is not int or seed < 0 or
        type(trial) is not int or trial not in range(TRIALS)):
        raise ValueError("ST4_ACTOR_BAD_SEED_OR_TRIAL")
    raw=digest("ST4-actor|" + str(seed) + "|" + str(trial))
    first = "treatment" if raw[1] % 2 == 0 else "control"
    return {
        "probe_action":PROBES[raw[0] % len(PROBES)],
        "arm_order":(first,
                      "control" if first=="treatment" else "treatment"),
    }


class PrivatePairedWorld:
    """At most two genuine public-source actions on one fork.

    The same source law is applied independently to each arm but is never
    exposed to a learner or blind actor. There is no off-policy invention:
    the second consequence comes from an actual step on that arm.
    """
    __slots__=("_law","_seed","_trial","_public","_pending","_step")

    def __init__(self,law,seed,trial):
        if (type(law) is not int or law < 0 or
            type(seed) is not int or seed < 0 or
            type(trial) is not int or trial not in range(TRIALS)):
            raise ValueError("ST4_SOURCE_BAD_WORLD_ARGUMENT")
        self._law=law
        self._seed=seed
        self._trial=trial
        self._public=digest("ST4-state|" + str(seed) + "|" + str(trial))[0]
        self._pending=0
        self._step=0

    def public(self):
        return public_bits(self._public)

    def step(self,action):
        if type(action) is not int or action not in range(4):
            raise ValueError("ST4_SOURCE_BAD_ACTION")
        if self._step >= 2:
            raise ValueError("ST4_SOURCE_ARM_EXHAUSTED")
        before=self._public
        extra=immediate_mask(self._law,action) if action in (0,1) else 0
        nxt=rotate_byte(before,rotation(self._law)) ^ extra ^ self._pending
        self._pending=delayed_mask(self._law) if action==2 else 0
        self._public=nxt
        self._step+=1
        return public_bits(nxt),public_bits(before ^ nxt)

    def snapshot(self):
        return json.dumps({
            "schema":SCHEMA,"law":self._law,"seed":self._seed,
            "trial":self._trial,"public":self._public,
            "pending":self._pending,"step":self._step,
        },sort_keys=True,separators=(",",":"),allow_nan=False)

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>1200:
            raise ValueError("ST4_SOURCE_BAD_CHECKPOINT")
        try:
            d=json.loads(payload)
            if (type(d) is not dict or
                set(d)!={"schema","law","seed","trial","public","pending","step"} or
                d["schema"]!=SCHEMA or
                any(type(d[key]) is not int for key in
                    ("law","seed","trial","public","pending","step")) or
                min(d["law"],d["seed"])<0 or
                d["trial"] not in range(TRIALS) or
                d["public"] not in range(256) or
                d["pending"] not in range(256) or
                d["step"] not in range(3)):
                raise ValueError("ST4_SOURCE_CHECKPOINT_SHAPE")
            obj=cls(d["law"],d["seed"],d["trial"])
            obj._public=d["public"]
            obj._pending=d["pending"]
            obj._step=d["step"]
            if obj.snapshot()!=payload:
                raise ValueError("ST4_SOURCE_NONCANONICAL_CHECKPOINT")
            return obj
        except (KeyError,TypeError,OverflowError) as exc:
            raise ValueError("ST4_SOURCE_RESTORE_FAILED") from exc


def source_paired_trial(law,seed,trial):
    """SOURCE-only diagnostic. Never offer this pair to a learner."""
    design=blind_design(seed,trial)
    arm_results={}
    h=hashlib.sha256()
    for arm in design["arm_order"]:
        world=PrivatePairedWorld(law,seed,trial)
        initial=world.public()
        intervention=2 if arm=="treatment" else 3
        after_probe,outcome_probe=world.step(intervention)
        # This cold restore happens before the common second action.
        cold=world.snapshot()
        world=PrivatePairedWorld.restore(cold)
        after_test,outcome_test=world.step(design["probe_action"])
        trace=bytes((*initial,intervention,*after_probe,*outcome_probe,
                     design["probe_action"],*after_test,*outcome_test))
        h.update(trace)
        arm_results[arm]={
            "initial_public":list(initial),
            "intervention_action":intervention,
            "pre_probe_public":list(after_probe),
            "probe_action":design["probe_action"],
            "after_probe_public":list(after_test),
            "probe_public_change":list(outcome_test),
            "cold_source_restore_exact":world._step==2,
            "real_action_steps":2,
        }
    t=arm_results["treatment"]
    c=arm_results["control"]
    return {
        "seed_evaluator_only":seed,
        "law_evaluator_only":law,
        "trial_evaluator_only":trial,
        "actor_arm_order":list(design["arm_order"]),
        "actor_probe_action":design["probe_action"],
        "same_initial_public":t["initial_public"]==c["initial_public"],
        "same_pre_probe_public":t["pre_probe_public"]==c["pre_probe_public"],
        "same_current_probe_action":t["probe_action"]==c["probe_action"],
        "different_real_probe_outcomes":
            t["probe_public_change"]!=c["probe_public_change"],
        "treatment_first_action":t["intervention_action"],
        "control_first_action":c["intervention_action"],
        "paired_original_action_consequence_sha256":h.hexdigest(),
        "original_action_steps":SOURCE_ACTIONS_PER_TRIAL,
        "cold_source_restore_exact":(
            t["cold_source_restore_exact"] and c["cold_source_restore_exact"]
        ),
        "learner_seen_private_law_or_paired_labels":False,
    }
