"""Raw WSP111 source facts only; no new hidden effect labels in this module.

Exactly the same 1m facts as the qualified WSP110 source-only generator.
Its original private X/Y mechanisms are deliberately NOT imported.
"""
from __future__ import annotations
from pathlib import Path
import importlib.util
import sys

HERE=Path(__file__).resolve().parent
_PARENT_PATH=HERE.parent/"WSP-110"/"world.py"
_spec=importlib.util.spec_from_file_location("wsp110_original_facts_only",_PARENT_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError("qualified parent raw-fact source not available")
_parent=importlib.util.module_from_spec(_spec)
sys.modules[_spec.name]=_parent
_spec.loader.exec_module(_parent)

N_GROUPS=25000
N_SUPPORT=3000
N_TEST=22000
N_INPUT_FACTS=1000000
original_facts=_parent.original_facts
source_types_for_group=_parent.types_for_group
