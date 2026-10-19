"""T15 Yggdrasil comparator-compatibility R1 source REISSUE ONLY.
Original failed six-hop -52015..-52000 / -52107..-52100 are consumed.
This wrapper binds the SAME frozen T15 source grammar to NEW source IDs.
Import is inert; the frozen first source grammar is not edited.
"""
import importlib.util,types
from pathlib import Path
D=Path(__file__).parent
TRAIN=tuple(range(-55015,-54999))
OPEN=tuple(range(-55107,-55099))
p=importlib.util.spec_from_file_location("ygg_t15_original_source",D/"20261019-yggdrasil-t15-source.py")
o=importlib.util.module_from_spec(p);p.loader.exec_module(o)
def birth(seed):
    assert seed in TRAIN or seed in OPEN,"ORIGINAL_COHORT_REUSE_FORBIDDEN"
    bounded=types.FunctionType(o.birth.__code__,dict(o.birth.__globals__,TRAIN=TRAIN,OPEN=OPEN),
       o.birth.__name__,o.birth.__defaults__)
    return bounded(seed)
