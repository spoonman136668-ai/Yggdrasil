import hashlib
import json
import unittest
from resource_inventory import common_checkpoint, vector
from residual_belief import ResidualBelief
from mr32_controls import MemorylessMean, ConventionalPrototypeControl
from recurrent_control import RecurrentStateSpaceControl
from diagonal_bayes_control import DiagonalBayesControl
from interaction_bayes_control import InteractionBayesControl
from learned_memory_allocator import LearnedMemoryAllocator

class CommonCheckpointTests(unittest.TestCase):
    def _learn_once(self, model):
        if isinstance(model, LearnedMemoryAllocator):
            model.insert("memory-a",vector(1,16))
            model.mark_use("memory-a")
            model.observe_task_outcome("memory-a",1.0)
        else:
            model.predict(vector(1,16),1)
            model.observe_selected_outcome(vector(2,8))

    def test_every_model_uses_common_versioned_integrity_envelope(self):
        models=[
            ResidualBelief(),MemorylessMean(),ConventionalPrototypeControl(),
            RecurrentStateSpaceControl(),DiagonalBayesControl(),
            InteractionBayesControl(),LearnedMemoryAllocator()
        ]
        for model in models:
            with self.subTest(model=type(model).__name__):
                self._learn_once(model)
                native_size,common_size=common_checkpoint(model)
                self.assertGreater(native_size,0)
                self.assertGreater(common_size,native_size)
                raw=(model.snapshot() if hasattr(model,"snapshot") else model.state_bytes())
                decoded=json.loads(raw.decode("utf-8"))
                payload=decoded.get("payload",decoded)
                common_payload={"model_type":type(model).__name__,"state":payload}
                digest=hashlib.sha256(json.dumps(common_payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
                self.assertEqual(len(json.dumps({"schema":"yggdrasil.mr32.common-checkpoint.v1","payload_sha256":digest,"payload":common_payload},sort_keys=True,separators=(",",":"),allow_nan=False).encode()),common_size)

if __name__=="__main__":unittest.main()
