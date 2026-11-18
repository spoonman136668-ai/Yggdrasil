"""WSP158: opt-in two-weight native probability calibration, no native edits.

Source independent. Program learned public evidence from existing YPC1 memory
and exactly two stage calibration weight indices. Development only: no first-use
authority, controller, original environment, counterfactual or new memory bank.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib

from yggdrasil.public_causal_cells import PublicCausalCells

MAGIC=b"YSC1"
GRID_NUMERATOR=(0,1,2,4,8)
GRID_DENOMINATOR=4
ORIGINAL_NATIVE_BYTES=PublicCausalCells.CHECKPOINT_BYTES
COMPOSITE_BYTES=len(MAGIC)+ORIGINAL_NATIVE_BYTES+2+32

class ProgrammedNativeStageCalibration:
    """Tiny source-blind readout program bound to a 164-byte native checkpoint.

    The learned native checkpoint stays exactly the original 164-byte model,
    and never changes merely because two calibration weights are selected.
    The two original public stage identities are 0=transition, 1=terminal.
    """
    __slots__=("_raw",)

    def __init__(self,native_checkpoint:bytes,transition_index:int,reward_index:int):
        if type(transition_index) is not int or not 0<=transition_index<len(GRID_NUMERATOR):
            raise ValueError("WSP158_TRANSITION_WEIGHT_INDEX")
        if type(reward_index) is not int or not 0<=reward_index<len(GRID_NUMERATOR):
            raise ValueError("WSP158_REWARD_WEIGHT_INDEX")
        if type(native_checkpoint) is not bytes:
            raise ValueError("WSP158_ORIGINAL_NATIVE_CHECKPOINT_TYPE")
        model=PublicCausalCells.restore(native_checkpoint)
        if model.snapshot()!=native_checkpoint:
            raise ValueError("WSP158_ORIGINAL_NATIVE_COLD_DIFFERENCE")
        payload=MAGIC+native_checkpoint+bytes((transition_index,reward_index))
        self._raw=payload+hashlib.sha256(payload).digest()

    def checkpoint(self)->bytes:
        return self._raw

    @classmethod
    def restore(cls,raw:bytes):
        if (type(raw) is not bytes or len(raw)!=COMPOSITE_BYTES
                or raw[:len(MAGIC)]!=MAGIC
                or hashlib.sha256(raw[:-32]).digest()!=raw[-32:]):
            raise ValueError("WSP158_PROGRAMMED_CHECKPOINT_INVALID")
        native=raw[len(MAGIC):len(MAGIC)+ORIGINAL_NATIVE_BYTES]
        obj=cls(native,raw[-34],raw[-33])
        if obj.checkpoint()!=raw:
            raise ValueError("WSP158_PROGRAMMED_COLD_MISMATCH")
        return obj

    @property
    def weights(self)->tuple[int,int]:
        return self._raw[-34],self._raw[-33]

    def native_checkpoint(self)->bytes:
        return self._raw[len(MAGIC):len(MAGIC)+ORIGINAL_NATIVE_BYTES]

    def probability(self,address:int,action:int,stage:int,*,retained:bool=False)->Fraction:
        if type(stage) is not int or stage not in (0,1):
            raise ValueError("WSP158_STAGE_INVALID")
        if type(retained) is not bool:
            raise ValueError("WSP158_RETAINED_FLAG_INVALID")
        model=PublicCausalCells.restore(self.native_checkpoint())
        # Public native implementation validates action, slot and retained
        # and gives Beta(1,1) numerator, denominator for observed public data.
        num,den=model.outcome_probability(address,action,retained=retained)
        successes=num-1
        trials=den-2
        if trials==0:
            return Fraction(1,2)
        pseudocount=GRID_NUMERATOR[self.weights[stage]]
        return Fraction(4*successes+pseudocount,4*trials+2*pseudocount)

def alpha_fraction(index:int)->Fraction:
    if type(index) is not int or not 0<=index<len(GRID_NUMERATOR):
        raise ValueError("WSP158_WEIGHT_INDEX_INVALID")
    return Fraction(GRID_NUMERATOR[index],GRID_DENOMINATOR)
