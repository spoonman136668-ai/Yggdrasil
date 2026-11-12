"""WSP52 SELFTEST diagnostic: order-invariant readout of IDENTICAL numeric weights.

This explicitly supplies a commutative-simulator prior. Natural language is not
commutative; never treat this as evidence of learned grammar order or syntax.
Not registered as a PRIMARY or WSP52 scientific arm.
"""
from collections import Counter, defaultdict
from direct_writer import DirectWeightWriter, _canonical, _parts, _validate_state


class OrderInvariantReadout(DirectWeightWriter):
    def predict(self, before, acoustic_bits):
        _validate_state(before)
        segmentations = _parts(acoustic_bits)
        if (_canonical(before), acoustic_bits) in self.conflicts:
            return None
        # Reuse *exactly* the original direct writer weights and experience costs.
        # Ablate the sentence-slot and ordering prior at readout only.
        word_weights = defaultdict(Counter)
        effect_weights = defaultdict(Counter)
        for (_slot, bits, entity), weight in self.entity_weights.items():
            word_weights[bits][entity] += weight
        for (_slot, left, right, effect), weight in self.effect_weights.items():
            effect_weights[tuple(sorted((left, right)))][effect] += weight
        candidates = {}
        for parts in segmentations:
            for entity_slot in range(3):
                entity_key = parts[entity_slot]
                effect_key = tuple(sorted(parts[i] for i in range(3) if i != entity_slot))
                ent = self._best(word_weights[entity_key], 2)
                eff = self._best(effect_weights[effect_key], 2)
                if ent is None or eff is None:
                    continue
                result = list(before)
                result[ent[0]] = eff[0]
                result = tuple(result)
                candidates[result] = max(candidates.get(result, 0), min(ent[1], eff[1]))
        if not candidates:
            return None
        ranked = sorted(candidates.items(), key=lambda x: (-x[1], x[0]))
        if len(ranked) > 1 and ranked[0][1] <= 2*ranked[1][1]:
            return None
        return ranked[0][0]
