"""CVH-03: bridge FKP25's exact original causal MDP to FKP24's factory shape.

Import and object CONSTRUCTION ONLY. No source world is reset or stepped by
this module. No original upstream code is copied, stubbed, rewritten, or
replaced. The resulting factory could be passed to FKP24's *trusted* adapter
ONLY in a separate owner-authorized first-use action. This file provides no
CLI that performs such an action, and no security claim about an in-process
source/learner Python boundary.

The two in-memory package namespace containers bypass only the already
identified unrelated upstream eager optional imports. Actual CausalGym
core/mdp classes and all underlying world code come from an exact SHA-pinned
read-only checkout and the FKP25 source-admission checks.
"""
from __future__ import annotations

from contextlib import contextmanager
import importlib
import importlib.util
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
FKP25 = HERE.parent / "FKP-25" / "runtime_probe.py"


class FactoryLifetime:
    """Use a constructed-source factory only within its verified import span."""
    def __init__(self, construct):
        if not callable(construct):
            raise ValueError("CVH03_ORIGINAL_CONSTRUCTOR_REQUIRED")
        self._construct = construct
        self._live = True
        self.constructed = 0

    def __call__(self):
        if not self._live:
            raise PermissionError("CVH03_ORIGINAL_FACTORY_CLOSED")
        value = self._construct()
        self.constructed += 1
        return value

    def close(self):
        self._live = False


def _original_qualification():
    """Load qualified FKP25 code from its inherited unmodified project path.

    The import invokes no original source modules or physical source actions.
    """
    if not FKP25.is_file():
        raise ValueError("CVH03_REQUIRED_FKP25_SOURCE_MISSING")
    spec = importlib.util.spec_from_file_location(
        "cvh03_exact_inherited_fkp25_runtime_probe", FKP25)
    if spec is None or spec.loader is None:
        raise ValueError("CVH03_FKP25_IMPORT_UNAVAILABLE")
    existing = sys.modules.get(spec.name)
    if existing is not None:
        return existing
    item = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = item
    try:
        spec.loader.exec_module(item)
    except BaseException:
        sys.modules.pop(spec.name, None)
        raise
    return item


@contextmanager
def verified_original_factory(checkout):
    """Yield callable producing only ORIGINAL source constructors, no actions.

    Verify original Git commit, 16 source blobs, clean worktree and pinned
    dependency versions before importing any original CausalGym module.
    Fail closed if any prior causal_gym import is present. After context exit
    the callable is permanently invalid, even if the caller retained it.
    """
    original = _original_qualification()
    root = Path(checkout).expanduser().resolve(strict=True)
    custody = original.verify_extended_original_git(root)
    deps = original._require_dependency_versions()
    if custody["original_source_sha"] != original.PIN or custody["real_actions"] != 0:
        raise ValueError("CVH03_SOURCE_CUSTODY_NOT_ACTION_FREE")
    if any(k == "causal_gym" or k.startswith("causal_gym.") for k in sys.modules):
        raise ValueError("CVH03_EXISTING_UPSTREAM_IMPORT_NOT_ISOLATED")

    factory = None
    original_module_keys = set(sys.modules)
    try:
        coreinit = original._ensure_checkout_file("causal_gym/core/__init__.py", root)
        mdpfile = original._ensure_checkout_file("causal_gym/envs/mdp.py", root)
        rootpkg = root / "causal_gym"
        sys.modules["causal_gym"] = original._memory_package(
            "causal_gym", rootpkg)
        core = importlib.import_module("causal_gym.core")
        if core.__file__ is None or Path(core.__file__).resolve() != coreinit:
            raise ValueError("CVH03_ORIGINAL_CORE_IMPORT_DRIFT")
        for key in ("SCM", "PCH", "Task", "Graph"):
            if not hasattr(core, key):
                raise ValueError("CVH03_CORE_PUBLIC_INTERFACE_MISSING")
            setattr(sys.modules["causal_gym"], key, getattr(core, key))
        sys.modules["causal_gym.envs"] = original._memory_package(
            "causal_gym.envs", rootpkg / "envs")
        native = importlib.import_module("causal_gym.envs.mdp")
        if native.__file__ is None or Path(native.__file__).resolve() != mdpfile:
            raise ValueError("CVH03_ORIGINAL_MDP_IMPORT_DRIFT")
        if not issubclass(native.MDPSCM, core.SCM) or not issubclass(
                native.MDPPCH, core.PCH):
            raise ValueError("CVH03_NATIVE_INHERITANCE_INVALID")
        tasklib = importlib.import_module("causal_gym.core.task")
        if not hasattr(tasklib, "Task") or not hasattr(
                tasklib.LearningRegime, "do"):
            raise ValueError("CVH03_NATIVE_DO_TASK_UNAVAILABLE")

        def constructor():
            # Inherited FKP25 constructor contract; the class is the original
            # unchanged native MDPPCH, NOT a model-learner wrapper.
            obj = native.MDPPCH(
                max_step=30,
                task=tasklib.Task(
                    learning_regime=tasklib.LearningRegime.do))
            if (not isinstance(obj, native.MDPPCH)
                    or not callable(getattr(obj, "do", None))
                    or not callable(getattr(obj, "reset", None))
                    or obj.task.learning_regime != tasklib.LearningRegime.do
                    or getattr(obj.env, "num_step", None) != 0):
                raise ValueError("CVH03_SOURCE_CONSTRUCTOR_MUTATED_OR_STEPPED")
            return obj

        factory = FactoryLifetime(constructor)
        yield factory, {
            "source_sha": original.PIN,
            "source_blobs_verified": len(custody["checked_original_blobs"]),
            "dependencies": deps,
            "targeted_original_class": "causal_gym.envs.mdp.MDPPCH",
            "source_action_calls": 0,
            "source_reset_calls": 0,
            "source_first_use": False,
            "scientific_pass": False,
            "native_accepted": False,
            "import_mode": "PINNED_TARGETED_NAMESPACES_ORIGINAL_CLASSES",
        }
    finally:
        if factory is not None:
            factory.close()
        # Remove only modules installed in this context, not preexisting
        # unrelated names. The caller must not keep/reuse source objects.
        for key in list(sys.modules):
            if (key not in original_module_keys and
                    (key == "causal_gym" or key.startswith("causal_gym."))):
                sys.modules.pop(key, None)
