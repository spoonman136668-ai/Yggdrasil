"""Opt-in cumulative CKAD integration over existing native representations.

Fixture witnesses are provenance-pinned development data, not authenticated
real-world do outcomes. No controller, source actor, or accepted-model authority.
The property image and every old constraint survive updates. Degree selection
remains provisional; inconsistent deterministic outcomes quarantine the slot.
"""
from fractions import Fraction
import json

from yggdrasil.native_context_basis import canonical, digest, pin, require, SOURCE_MODE, SOURCE_KIND
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_degree_hypothesis import NativeDegreeHypothesis
from yggdrasil.native_sparse_hypothesis import NativeSparseHypothesis, SCHEMA as SPARSE_SCHEMA
from yggdrasil.native_causal_relation_posterior import NativeCausalRelationPosterior
from yggdrasil.native_stochastic_history import NativeStochasticHistory
from yggdrasil.native_dtr_history import NativeDTRHistory
from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_prior_hypothesis import input_order
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA = 'yggdrasil.ckad.native-cumulative-learner.v1'
REPAIR_SCHEMA = 'yggdrasil.ckad.native-cumulative-learner.v2'
HISTORY_SCHEMA = 'yggdrasil.ckad.native-cumulative-learner.v3'
DTR_SCHEMA = 'yggdrasil.ckad.native-cumulative-learner.v4'
EXPERIENCE_SCHEMA = 'yggdrasil.ckad.native-cumulative-learner.v5'
RELATION_SCHEMA = 'yggdrasil.ckad.native-cumulative-learner.v6'
EXPERIENCE_SOURCE = '20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef'
MAX_BYTES = 16 * 1024 * 1024
MAX_EVENTS = 128


def coordinates(slot):
    require(type(slot) is int and 0 <= slot < 16, 'INTEGRATED_SLOT')
    return (slot, False) if slot < 7 else (slot - 7, True)


def _two_stage_plan(transition, terminal):
    first_values = []
    second_actions = []
    for first_action in (0, 1):
        next_one = transition(first_action)
        best_rewards = []
        contingent_actions = []
        for next_state in (0, 1):
            rewards = [terminal(first_action, next_state, action) for action in (0, 1)]
            best_action = int(rewards[1] > rewards[0])
            best_rewards.append(rewards[best_action])
            contingent_actions.append(best_action)
        first_values.append((1 - next_one) * best_rewards[0] + next_one * best_rewards[1])
        second_actions.append(tuple(contingent_actions))

    return {
        "first_values": tuple((value.numerator, value.denominator) for value in first_values),
        "first_action": int(first_values[1] > first_values[0]),
        "second_actions": tuple(second_actions),
    }


class NativeCumulativeLearner:
    """One immutable train/save/restore interface; no rival memory substrate."""
    __slots__ = ('_properties', '_source', '_hypotheses', '_quarantined', '_events',
                 '_schema', '_repairs', '_history', '_dtr', '_experience', '_compiled')

    def __init__(self, property_raw, expected_sha256):
        self._properties = NativePropertyKnowledge.restore(property_raw, expected_sha256)
        self._source = NativeContextAccumulator(self._properties._bits)
        self._hypotheses = (None,) * 16
        self._quarantined = (False,) * 16
        self._events = ()
        self._schema = SCHEMA
        self._repairs = ()
        self._history = None
        self._dtr = None
        self._experience = None
        self._compiled = (None,) * 16

    def _copy(self):
        obj = object.__new__(NativeCumulativeLearner)
        for name in self.__slots__:
            setattr(obj, name, getattr(self, name))
        return obj

    def _rows(self, slot):
        a, r = coordinates(slot)
        bits = self._source._model.context_bits
        seen = self._source._seen[slot]
        return [[x & ((1 << bits) - 1), x >> bits,
                 self._source.predict(a, x & ((1 << bits) - 1), x >> bits, retained=r)]
                for x in sorted(range(1 << (bits + 1)), key=input_order) if seen & (1 << x)]

    def _view(self, slot):
        rows = self._rows(slot)
        bits = self._source._model.context_bits
        return NativeContextAccumulator(bits).stage_update(
            0, rows, digest(canonical(rows)), max_degree=bits + 1).checkpoint()

    def observe(self, slot, records, expected_sha256, *, source_ref,
                source_mode=SOURCE_MODE, source_kind=SOURCE_KIND):
        """Train only on revealed engineering witnesses; keep negative evidence.

        No family label, truth function, hidden source state, or evaluator is an
        input. Repeated witnessed inputs do not become extra training examples.
        A deterministic contradiction returns a quarantined copy, never erases
        the old weights or invents a corrected outcome.
        """
        a, r = coordinates(slot)
        require(source_mode == SOURCE_MODE and source_kind == SOURCE_KIND,
                'INTEGRATED_ORIGINAL_CAUSAL_SOURCE_UNQUALIFIED')
        require(pin(source_ref) and pin(expected_sha256)
                and type(records) is list and 0 < len(records) <= 2048
                and digest(canonical(records)) == expected_sha256, 'INTEGRATED_SOURCE_PIN')
        seen = {}
        for row in records:
            require(type(row) is list and len(row) == 3, 'INTEGRATED_PUBLIC_ROW')
            c = self._source._model._context(row[0])
            action = PublicCausalCells._bit(row[1], 'ACTION')
            y = PublicCausalCells._bit(row[2], 'PUBLIC_OUTCOME')
            key = c | (action << self._source._model.context_bits)
            require(key not in seen or seen[key] == y, 'INTEGRATED_INTERNAL_CONFLICT')
            seen[key] = y
        event_key = digest(canonical([slot, expected_sha256, source_ref]))
        if any(e['event_key'] == event_key for e in self._events):
            return self
        require(not self._quarantined[slot], 'INTEGRATED_QUARANTINED')
        require(len(self._events) < MAX_EVENTS, 'INTEGRATED_EVENT_CAPACITY')
        conflicts = [row for row in records if self._source._seen[slot] &
                     (1 << (row[0] | (row[1] << self._source._model.context_bits))) and
                     self._source.predict(a, row[0], row[1], retained=r) != row[2]]
        event = {'event_key': event_key, 'slot': slot, 'source_ref': source_ref,
                 'source_sha256': expected_sha256, 'records': len(records),
                 'status': 'QUARANTINED' if conflicts else 'ACQUIRED',
                 'conflicting_packet': records if conflicts else None}
        obj = self._copy()
        if conflicts:
            obj._quarantined = self._quarantined[:slot] + (True,) + self._quarantined[slot+1:]
        else:
            bits = self._source._model.context_bits
            fresh = [[x & ((1 << bits)-1), x >> bits, y] for x, y in seen.items()
                     if not self._source._seen[slot] & (1 << x)]
            if fresh:
                obj._source = self._source.stage_update(a, fresh, digest(canonical(fresh)),
                                                       max_degree=bits+1, retained=r)
            n = obj._source._seen[slot].bit_count()
            if type(self._hypotheses[slot]) is NativeSparseHypothesis:
                require(n>=8 and n%4==0, 'INTEGRATED_SPARSE_CONTINUATION_COUNT')
            hyp = None
            if n >= 8 and n % 4 == 0:
                raw = obj._view(slot)
                if type(self._hypotheses[slot]) is NativeSparseHypothesis:
                    hyp, _ = NativeSparseHypothesis.fit_checkpoint(raw, digest(raw))
                    require(hyp.eligible, 'INTEGRATED_SPARSE_CONTINUATION_UNQUALIFIED')
                else:
                    hyp = NativeDegreeHypothesis.fit_checkpoint(raw, digest(raw))
            obj._hypotheses = self._hypotheses[:slot] + (hyp,) + self._hypotheses[slot+1:]
        obj._events = self._events + (event,)
        if self._schema == RELATION_SCHEMA and self._compiled[slot] is not None:
            # Fresh witnessed evidence invalidates only its own compiled version space.
            obj._compiled = (self._compiled[:slot] + (None,) + self._compiled[slot+1:])
            if not any(obj._compiled):
                obj._schema = SCHEMA
        return obj

    def repair_sparse(self, slot):
        """Explicit opt-in repair; rejected hypotheses never replace state."""
        coordinates(slot)
        require(self._schema != RELATION_SCHEMA, 'INTEGRATED_SPARSE_WITH_COMPILED_SCOPE')
        old = self._hypotheses[slot]
        require(not self._quarantined[slot] and old is not None and not old.eligible
                and type(old) is NativeDegreeHypothesis, 'INTEGRATED_SPARSE_REPAIR_SCOPE')
        raw = self._view(slot)
        hyp, cost = NativeSparseHypothesis.fit_checkpoint(raw, digest(raw))
        if not hyp.eligible:
            return self, hyp, cost
        require(len(self._repairs)<16, 'INTEGRATED_REPAIR_CAPACITY')
        obj=self._copy();obj._schema=(DTR_SCHEMA if self._dtr is not None else
                                    HISTORY_SCHEMA if self._history is not None else REPAIR_SCHEMA)
        obj._hypotheses=self._hypotheses[:slot]+(hyp,)+self._hypotheses[slot+1:]
        obj._repairs=self._repairs+({'slot':slot,'old_hypothesis_sha256':digest(old.checkpoint()),
            'source_view_sha256':digest(raw),'rule':hyp.info()['rule']},)
        return obj,hyp,cost

    def compile_causal_relations(self, slot):
        """Opt-in numeric multi-hypothesis compilation in THIS native state.

        Existing witnessed source only. A conventional fixed ANF grammar is
        supplied, so this is not autonomous operator discovery or acceptance.
        """
        coordinates(slot)
        require(self._schema in (SCHEMA, RELATION_SCHEMA)
                and not self._repairs and self._history is None and self._dtr is None
                and self._experience is None, 'INTEGRATED_RELATION_COMPILE_SCOPE')
        require(not self._quarantined[slot] and self._hypotheses[slot] is not None
                and type(self._hypotheses[slot]) is NativeDegreeHypothesis
                and self._source._seen[slot].bit_count() in (8, 12, 16),
                'INTEGRATED_RELATION_SOURCE_COUNT')
        raw = self._view(slot)
        committee = NativeCausalRelationPosterior.fit_checkpoint(raw, digest(raw))
        if (self._compiled[slot] is not None and
                self._compiled[slot].checkpoint() == committee.checkpoint()):
            return self
        child = self._copy()
        child._compiled = self._compiled[:slot] + (committee,) + self._compiled[slot+1:]
        child._schema = RELATION_SCHEMA
        return child

    def causal_relation_probability(self, slot, context, action):
        """Return source-known or posterior (ones,total), or None if absent."""
        a, r = coordinates(slot)
        c = self._source._model._context(context)
        PublicCausalCells._bit(action, 'ACTION')
        if self._quarantined[slot]:
            return None
        seen = self._source.predict(a, c, action, retained=r)
        if seen is not None:
            return (seen, 1)
        committee = self._compiled[slot]
        return None if committee is None else committee.predict_fraction(c, action)

    def recall_causal_regime(self, slots, diagnostics, context, action):
        """Unlabeled source-only relation recall from THIS learner's native memory.

        Retained numeric committees are conditioned on real witnessed source,
        but the equal priors, unfamiliar-world alternative and 0.90 selection
        threshold are conventional supplied assumptions, NOT new primitive
        discovery, a source trust certificate, or accepted-model authority.
        No model state or source/held outcome is changed or accessed here.
        Returns (native_probability_numerator, denominator, slot_or_none).
        """
        from fractions import Fraction

        require(type(slots) in (list, tuple) and len(slots) == 2
                and all(type(s) is int and 0 <= s < 16 for s in slots)
                and slots[0] != slots[1], 'INTEGRATED_RECALL_SLOTS')
        require(type(diagnostics) is list and len(diagnostics) == 4,
                'INTEGRATED_RECALL_PUBLIC_DIAGNOSTICS')
        self._source._model._context(context)
        PublicCausalCells._bit(action, 'ACTION')
        require(all(self._compiled[s] is not None and not self._quarantined[s]
                    for s in slots), 'INTEGRATED_RECALL_NO_NATIVE_MEMORY')
        unique = set()
        for record in diagnostics:
            require(type(record) is list and len(record) == 3,
                    'INTEGRATED_RECALL_RECORD_SHAPE')
            c, a, y = record
            self._source._model._context(c)
            PublicCausalCells._bit(a, 'ACTION')
            PublicCausalCells._bit(y, 'PUBLIC_OUTCOME')
            require((c, a) not in unique, 'INTEGRATED_RECALL_DUPLICATE_INPUT')
            unique.add((c, a))
        # The unknown-world alternative is a fully specified four-Bernoulli
        # source-only likelihood 1/16. There are no hidden class labels.
        evidence = {}
        for slot in slots:
            likelihood = Fraction(1, 1)
            for c, a, y in diagnostics:
                probability = self.causal_relation_probability(slot, c, a)
                require(probability is not None, 'INTEGRATED_RECALL_MISSING_MEMORY')
                ones, total = probability
                require(type(ones) is int and type(total) is int
                        and total > 0 and 0 <= ones <= total,
                        'INTEGRATED_RECALL_PROBABILITY')
                likelihood *= Fraction(ones if y else total - ones, total)
            evidence[slot] = likelihood
        denominator = sum(evidence.values(), Fraction(1, 16))
        selected = max(slots, key=lambda slot: (evidence[slot], -slot))
        if evidence[selected] / denominator < Fraction(9, 10):
            return (1, 2, None)
        probability = self.causal_relation_probability(selected, context, action)
        require(probability is not None, 'INTEGRATED_RECALL_EMPTY_PREDICTION')
        return (probability[0], probability[1], selected)

    def propose_causal_discriminator(self, slots, diagnostics, public_candidates):
        """Choose one public do-action by disagreement of retained native causality.

        This is an opt-in source-only, exact-rational Gini-information proxy.
        No model/owner state is changed, no target outcomes are generated, and
        the unknown-class p=0.5 prior is a supplied conventional assumption.
        """
        from fractions import Fraction

        require(type(slots) in (tuple, list) and len(slots) == 2
                and all(type(i) is int and 0 <= i < 16 for i in slots)
                and slots[0] != slots[1], 'INTEGRATED_DISCRIMINATOR_SLOTS')
        require(type(diagnostics) is list and 0 <= len(diagnostics) < 4,
                'INTEGRATED_DISCRIMINATOR_DIAGNOSTICS')
        require(type(public_candidates) is list and 1 <= len(public_candidates) <= 16,
                'INTEGRATED_DISCRIMINATOR_PUBLIC_CANDIDATES')
        require(all(self._compiled[s] is not None and not self._quarantined[s]
                    for s in slots), 'INTEGRATED_DISCRIMINATOR_MISSING_NATIVE_MEMORY')

        observed = set()
        for item in diagnostics:
            require(type(item) is list and len(item) == 3,
                    'INTEGRATED_DISCRIMINATOR_DIAGNOSTIC_RECORD')
            c, a, y = item
            self._source._model._context(c)
            PublicCausalCells._bit(a, 'ACTION')
            PublicCausalCells._bit(y, 'PUBLIC_OUTCOME')
            require((c, a) not in observed,
                    'INTEGRATED_DISCRIMINATOR_DUPLICATE_DIAGNOSTIC')
            observed.add((c, a))
        candidates = []
        for item in public_candidates:
            require(type(item) is list and len(item) == 2,
                    'INTEGRATED_DISCRIMINATOR_CANDIDATE_SHAPE')
            c, a = item
            self._source._model._context(c)
            PublicCausalCells._bit(a, 'ACTION')
            require((c, a) not in observed and (c, a) not in candidates,
                    'INTEGRATED_DISCRIMINATOR_CANDIDATE_OVERLAP')
            candidates.append((c, a))

        likelihood = {}
        for slot in slots:
            weight = Fraction(1, 1)
            for c, a, y in diagnostics:
                got = self.causal_relation_probability(slot, c, a)
                require(got is not None, 'INTEGRATED_DISCRIMINATOR_MISSING_POSTERIOR')
                ones, total = got
                require(type(ones) is int and type(total) is int
                        and 0 <= ones <= total and total > 0,
                        'INTEGRATED_DISCRIMINATOR_BAD_POSTERIOR')
                weight *= Fraction(ones if y else total - ones, total)
            likelihood[slot] = weight
        likelihood_unknown = Fraction(1, 2) ** len(diagnostics)
        evidence = sum(likelihood.values(), likelihood_unknown)
        require(evidence > 0, 'INTEGRATED_DISCRIMINATOR_ZERO_MASS')
        prior = {slot: likelihood[slot] / evidence for slot in slots}
        prior_unknown = likelihood_unknown / evidence

        best = None
        best_score = None
        for c, a in sorted(candidates):
            predictions = {}
            for slot in slots:
                ones, total = self.causal_relation_probability(slot, c, a)
                predictions[slot] = Fraction(ones, total)
            mean = (sum(prior[slot] * predictions[slot] for slot in slots)
                    + prior_unknown * Fraction(1, 2))
            score = (sum(prior[slot] * (predictions[slot] - mean) ** 2
                         for slot in slots)
                     + prior_unknown * (Fraction(1, 2) - mean) ** 2)
            if best_score is None or score > best_score:
                best_score = score
                best = [c, a]
        return best

    def incorporate_causal_world(self, records, expected_sha256, *, source_ref,
                                 available_slots=(1, 2, 3, 4, 5, 6, 7, 8, 9)):
        """Learn an unlabelled causal relation in this SAME native checkpoint.

        A known source must explain all witnessed consequences strongly enough
        under the supplied Bayesian admission prior. Otherwise twelve actual
        do/outcomes can create a new source-backed native committee; four
        insufficient do/outcomes only permit recall/abstention. Does not accept
        semantic regime labels, model coefficients or future held outcomes.
        A supplied 697-model ANF grammar is NOT intrinsic primitive discovery.
        """
        require(self._schema in (SCHEMA, RELATION_SCHEMA)
                and self._history is None and self._dtr is None
                and self._experience is None and not self._repairs,
                'INTEGRATED_CAUSAL_STATE_SCOPE')
        require(type(records) is list and len(records) in (4, 12)
                and pin(expected_sha256) and digest(canonical(records)) == expected_sha256
                and pin(source_ref), 'INTEGRATED_CAUSAL_STATE_SOURCE_PIN')
        require(type(available_slots) in (tuple, list)
                and 1 <= len(available_slots) <= 9
                and list(available_slots) == sorted(set(available_slots))
                and all(type(s) is int and 1 <= s <= 9 for s in available_slots),
                'INTEGRATED_CAUSAL_STATE_ALLOWED_SLOTS')
        observed = set()
        for row in records:
            require(type(row) is list and len(row) == 3,
                    'INTEGRATED_CAUSAL_STATE_PUBLIC_ROW')
            c, a, y = row
            self._source._model._context(c)
            PublicCausalCells._bit(a, 'ACTION')
            PublicCausalCells._bit(y, 'PUBLIC_OUTCOME')
            require((c, a) not in observed, 'INTEGRATED_CAUSAL_STATE_DUPLICATE_DO')
            observed.add((c, a))
        from fractions import Fraction

        known = [slot for slot in available_slots
                 if self._compiled[slot] is not None
                 and self._compiled[slot].model_count > 0
                 and not self._quarantined[slot]]
        likelihood = {}
        for slot in known:
            score = Fraction(1, 1)
            for c, a, y in records:
                nums = self.causal_relation_probability(slot, c, a)
                require(nums is not None and type(nums[0]) is int
                        and type(nums[1]) is int and nums[1] > 0
                        and 0 <= nums[0] <= nums[1],
                        'INTEGRATED_CAUSAL_STATE_POSTERIOR')
                p = Fraction(nums[0], nums[1])
                score *= p if y else 1 - p
            likelihood[slot] = score
        unknown = Fraction(1, 2) ** len(records)
        denominator = sum(likelihood.values(), unknown)
        if known:
            selected = max(known, key=lambda slot: (likelihood[slot], -slot))
            if likelihood[selected] / denominator >= Fraction(9, 10):
                # The source packet is used as observed recall evidence only;
                # it never overwrites or double-counts native source weights.
                return self, selected, 'RECALLED'
        if len(records) == 4:
            return self, None, 'ABSTAIN'
        empty = next((slot for slot in available_slots
                      if self._source._seen[slot] == 0
                      and self._hypotheses[slot] is None
                      and self._compiled[slot] is None
                      and not self._quarantined[slot]), None)
        require(empty is not None, 'INTEGRATED_CAUSAL_STATE_CAPACITY_EXHAUSTED')
        state = self
        for packet in (records[:8], records[8:]):
            state = state.observe(empty, packet, digest(canonical(packet)),
                                  source_ref=source_ref)
        state = state.compile_causal_relations(empty)
        require(state._source._seen[empty].bit_count() == 12
                and state._compiled[empty] is not None
                and all(state._compiled[slot].checkpoint()
                        == self._compiled[slot].checkpoint() for slot in known),
                'INTEGRATED_CAUSAL_STATE_LEARNED_CUSTODY')
        return (state, empty, 'ACQUIRED' if state._compiled[empty].model_count
                else 'INCOMPATIBLE')

    def validate_causal_source_with_witnesses(
            self, slot, records, expected_sha256, *,
            source_ref, evidence_slot, query_context, query_action):
        """Source-trained numeric model falsification with actual new interventions.

        Two previously unwitnessed do/outcome results are stored in another
        native source slot on this SAME immutable learner. Original source
        coefficients and compiled relation memories are never overwritten.
        A still-compatible conventional <=3-term source class is not proof
        against alternative unseen mechanisms. No hidden labels or simulator.
        """
        from yggdrasil.native_context_basis import feature_row
        require(self._schema == RELATION_SCHEMA and
                type(slot) is int and 1 <= slot <= 9 and
                type(evidence_slot) is int and 12 <= evidence_slot <= 14
                and self._compiled[slot] is not None and
                self._compiled[slot].model_count > 0 and
                not self._quarantined[slot] and
                not self._repairs and self._history is None
                and self._dtr is None and self._experience is None,
                'INTEGRATED_CAUSAL_WITNESS_SCOPE')
        require(type(records) is list and len(records) == 2
                and pin(expected_sha256)
                and digest(canonical(records)) == expected_sha256
                and pin(source_ref), 'INTEGRATED_CAUSAL_WITNESS_SOURCE_PIN')
        addresses = set()
        known = self._source._seen[slot]
        for row in records:
            require(type(row) is list and len(row) == 3,
                    'INTEGRATED_CAUSAL_WITNESS_SHAPE')
            c, a, observed_y = row
            self._source._model._context(c)
            PublicCausalCells._bit(a, 'ACTION')
            PublicCausalCells._bit(observed_y, 'PUBLIC_OUTCOME')
            k = c | (a << self._source._model.context_bits)
            require(k not in addresses and not (known & (1 << k)),
                    'INTEGRATED_CAUSAL_WITNESS_OVERLAP')
            addresses.add(k)
        self._source._model._context(query_context)
        PublicCausalCells._bit(query_action, 'ACTION')
        query = query_context | (query_action << self._source._model.context_bits)
        require(query not in addresses and not (known & (1 << query)),
                'INTEGRATED_CAUSAL_WITNESS_HELD_QUERY_LEAK')
        prior_events = [e for e in self._events if e['slot'] == evidence_slot]
        if prior_events:
            require(len(prior_events) == 1
                    and prior_events[0]['source_sha256'] == expected_sha256
                    and prior_events[0]['source_ref'] == source_ref
                    and self._source._seen[evidence_slot].bit_count() == 2
                    and {tuple(x) for x in self._rows(evidence_slot)}
                         == {tuple(x) for x in records},
                    'INTEGRATED_CAUSAL_WITNESS_LEDGER_REUSE')
        else:
            require(self._source._seen[evidence_slot] == 0
                    and self._compiled[evidence_slot] is None
                    and self._hypotheses[evidence_slot] is None
                    and not self._quarantined[evidence_slot],
                    'INTEGRATED_CAUSAL_WITNESS_EVIDENCE_SLOT_OCCUPIED')
        retained = []
        for weight in self._compiled[slot]._models:
            if all(((weight & feature_row(c | (a << 3), 4)).bit_count() & 1)
                   == outcome for c, a, outcome in records):
                retained.append(weight)
        version = (sum(((w & feature_row(query, 4)).bit_count() & 1)
                       for w in retained), len(retained)) if retained else (1, 2)
        status = 'CONSISTENT' if retained else 'FALSIFIED'
        updated = self.observe(evidence_slot, records, expected_sha256,
                               source_ref=source_ref)
        require(updated._compiled[slot] is not None
                and updated._compiled[slot].checkpoint()
                    == self._compiled[slot].checkpoint()
                and updated._source._seen[evidence_slot].bit_count() == 2
                and updated._source._seen[slot] == known,
                'INTEGRATED_CAUSAL_WITNESS_MEMORY_CUSTODY')
        return updated, version, status

    def observe_cached_history(self,raw,expected_sha256,stop):
        """Accumulate authenticated past public rows, never hypothetical do data."""
        require(self._schema != RELATION_SCHEMA, 'INTEGRATED_RELATION_HISTORY_SCOPE')
        old=self._history if self._history is not None else NativeStochasticHistory()
        history=old.stage_prefix(raw,expected_sha256,stop)
        if history is old:return self
        obj=self._copy();obj._schema=DTR_SCHEMA if self._dtr is not None else HISTORY_SCHEMA;obj._history=history
        return obj

    def history_forecast(self,world,before,action,previous_reward):
        NativeStochasticHistory.address(world,before,action,previous_reward)
        return (((1,2),(1,2)) if self._history is None else
                self._history.predict(world,before,action,previous_reward))

    def history_forecast_backoff(self,world,before,action,previous_reward):
        NativeStochasticHistory.address(world,before,action,previous_reward)
        return (((1,2),(1,2)) if self._history is None else
                self._history.predict_backoff(world,before,action,previous_reward))

    def observe_cached_dtr(self,raw,expected_sha256,stop):
        require(self._schema != RELATION_SCHEMA, 'INTEGRATED_RELATION_DTR_SCOPE')
        require(self._history is not None,'INTEGRATED_DTR_REQUIRES_HISTORY_PARENT')
        old=self._dtr if self._dtr is not None else NativeDTRHistory()
        dtr=old.stage_prefix(raw,expected_sha256,stop)
        if dtr is old:return self
        obj=self._copy();obj._schema=DTR_SCHEMA;obj._dtr=dtr;return obj

    def dtr_transition_forecast(self,s1,x1):
        NativeDTRHistory.validate(s1,x1)
        return (1,2) if self._dtr is None else self._dtr.transition(s1,x1)

    def dtr_terminal_forecast(self,s1,x1,s2,x2):
        NativeDTRHistory.validate(s1,x1,s2,x2)
        return (1,2) if self._dtr is None else self._dtr.terminal(s1,x1,s2,x2)

    def dtr_plan(self, initial_state):
        """Compare first actions using the fitted public two-stage DTR model.

        Values are model forecasts. The plan carries a second action for each
        possible pair of first action and observed next state.
        """
        NativeDTRHistory.validate(initial_state)
        if self._dtr is None:
            return None
        return _two_stage_plan(
            lambda first: Fraction(*self.dtr_transition_forecast(initial_state, first)),
            lambda first, state, second: Fraction(
                *self.dtr_terminal_forecast(initial_state, first, state, second)),
        )

    def _episode_reader(self):
        return self._experience if self._experience is not None else NativeEpisodeExperience()

    def observe_experience(self, identifier, views, row, *, source_sha256, packet_sha256, repair=None):
        """Admit one revealed development episode through the pilot source contract."""
        require(self._dtr is not None, 'EPISODE_REQUIRES_INTEGRATED_PARENT')
        require(source_sha256 == EXPERIENCE_SOURCE and
                digest(canonical([identifier, views, row])) == packet_sha256,
                'EPISODE_SOURCE_PACKET')
        require(repair is None or (type(repair) is bool and self._experience is None),
                'EPISODE_REPAIR_CONFIGURATION')
        previous = (self._episode_reader() if repair is None
                    else NativeEpisodeExperience(repair=repair))
        experience = previous.observe(identifier, views, row)
        if previous is experience:
            return self
        candidate = self._copy()
        candidate._experience = experience
        return candidate

    def consolidate_experience(self):
        """Replay the retained public episodes and verify the resulting state."""
        if self._experience is None:
            return self
        candidate = self._copy()
        candidate._experience = self._experience.consolidate()
        require(candidate.checkpoint() == self.checkpoint(), 'EPISODE_CONSOLIDATION_DRIFT')
        return candidate

    def experience_forecast(self, view, first, next_state=None, second=None, *, full=False):
        return self._episode_reader().forecast(view, first, next_state, second, full=full)

    def experience_explore(self, view, first=None, next_state=None):
        return self._episode_reader().propose(view, first, next_state)

    def experience_plan(self, view, *, full=False):
        experience = self._episode_reader()
        return _two_stage_plan(
            lambda first: experience.forecast(view, first, full=full),
            lambda first, state, second: experience.forecast(view, first, state, second, full=full),
        )

    def begin_experience_context(self, *, novel=False):
        """Start a public context session over retained experience hypotheses."""
        require(self._experience is not None, 'CONTEXT_REQUIRES_EXPERIENCE')
        candidate = self._copy()
        candidate._experience = self._experience.begin_context(novel=novel)
        return candidate

    def begin_experience_stream(self):
        """Start a single cumulative, consequence-monitored stream."""
        require(self._experience is not None, 'STREAM_REQUIRES_EXPERIENCE')
        candidate = self._copy()
        candidate._experience = self._experience.begin_stream()
        return candidate

    def experience_context_forecast(self, view, first, next_state=None, second=None):
        require(self._experience is not None, 'CONTEXT_REQUIRES_EXPERIENCE')
        return self._experience.context_forecast(view, first, next_state, second)

    def experience_context_explore(self, view, first=None, next_state=None):
        require(self._experience is not None, 'CONTEXT_REQUIRES_EXPERIENCE')
        return self._experience.context_explore(view, first, next_state)

    def experience_context_plan(self, view):
        require(self._experience is not None, 'CONTEXT_REQUIRES_EXPERIENCE')
        return _two_stage_plan(
            lambda first: self._experience.context_forecast(view, first),
            lambda first, state, second: self._experience.context_forecast(view, first, state, second),
        )

    def predict(self, slot, context, action, *, provisional=True):
        a, r = coordinates(slot)
        require(type(provisional) is bool, 'INTEGRATED_PROVISIONAL_FLAG')
        answer = self._source.predict(a, context, action, retained=r)
        if self._quarantined[slot]:
            return None
        if answer is not None or not provisional:
            return answer
        hyp = self._hypotheses[slot]
        return hyp.predict_provisional(context, action) if hyp is not None else None

    def predict_entity(self, slot, entity, action):
        p = self._properties
        p._entity(entity)
        require(p._known[entity] == (1 << p._bits)-1, 'INTEGRATED_INCOMPLETE_CONTEXT')
        return self.predict(slot, p._values[entity], action)

    def propose(self, slot, public_inputs, count):
        """Select cached/public action inputs without inspecting their outcomes.

        Priority is unknown provisional readout, then an unobserved alternative
        at an observed context, then the existing deterministic SHA ordering.
        This heuristic is not a claim of optimal intervention value.
        """
        coordinates(slot)
        require(not self._quarantined[slot] and type(count) is int and count > 0,
                'INTEGRATED_PROPOSAL')
        require(type(public_inputs) is list and len(public_inputs) <= 2048,
                'INTEGRATED_PUBLIC_INPUTS')
        bits = self._source._model.context_bits
        masks = set()
        for row in public_inputs:
            require(type(row) is list and len(row) == 2, 'INTEGRATED_PROPOSAL_LABEL_LEAK')
            c = self._source._model._context(row[0])
            action = PublicCausalCells._bit(row[1], 'ACTION')
            masks.add(c | (action << bits))
        old = self._source._seen[slot]
        fresh = [x for x in masks if not old & (1 << x)]
        def priority(x):
            c, a = x & ((1 << bits)-1), x >> bits
            return (self.predict(slot, c, a) is not None,
                    not bool(old & (1 << (x ^ (1 << bits)))), input_order(x))
        return [[x & ((1 << bits)-1), x >> bits] for x in sorted(fresh, key=priority)[:count]]

    def info(self):
        info = {'stored_properties': self._properties.property_count,
                'observed_inputs': [s.bit_count() for s in self._source._seen],
                'quarantined': list(self._quarantined),
                'representations': [h.info() if h is not None else None for h in self._hypotheses],
                'events': len(self._events), 'accepted_native': False, 'scientific_pass': False}
        if self._history is not None:info['stochastic_history']=self._history.info()
        if self._dtr is not None:info['dtr_history']=self._dtr.info()
        if self._experience is not None:info['episode_experience']=self._experience.info()
        return info

    def checkpoint(self):
        d = {'schema': self._schema, 'source_mode': SOURCE_MODE,
            'properties_ascii': self._properties.checkpoint().decode('ascii'),
            'source_ascii': self._source.checkpoint().decode('ascii'),
            'hypotheses_ascii': [h.checkpoint().decode('ascii') if h is not None else None
                                 for h in self._hypotheses],
            'quarantined': self._quarantined, 'events': self._events,
            'accepted_native': False, 'scientific_pass': False}
        if self._schema in (REPAIR_SCHEMA,HISTORY_SCHEMA,DTR_SCHEMA):d['repairs']=self._repairs
        if self._schema in (HISTORY_SCHEMA,DTR_SCHEMA):d['history_ascii']=self._history.checkpoint().decode('ascii')
        if self._schema==DTR_SCHEMA:d['dtr_ascii']=self._dtr.checkpoint().decode('ascii')
        if self._schema == RELATION_SCHEMA:
            require(any(self._compiled) and not self._repairs and self._history is None
                    and self._dtr is None and self._experience is None,
                    'INTEGRATED_RELATION_CHECKPOINT_SCOPE')
            d['compiled_ascii'] = [c.checkpoint().decode('ascii') if c is not None else None
                                   for c in self._compiled]
        else:
            require(not any(self._compiled), 'INTEGRATED_RELATION_SCHEMA_LOSS')
        if self._experience is not None:
            d['schema'] = EXPERIENCE_SCHEMA
            d['experience_ascii'] = self._experience.checkpoint().decode('ascii')
            d['experience_source'] = EXPERIENCE_SOURCE
        raw = canonical(d)
        require(len(raw) <= MAX_BYTES, 'INTEGRATED_CHECKPOINT_CAPACITY')
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES and pin(expected_sha256)
                and digest(raw) == expected_sha256, 'INTEGRATED_CHECKPOINT_PIN')
        def unique(pairs):
            d = {}
            for k, v in pairs:
                require(k not in d, 'INTEGRATED_DUPLICATE_KEY'); d[k] = v
            return d
        try:
            d = json.loads(raw.decode('ascii'), object_pairs_hook=unique)
            keys={'schema','source_mode','properties_ascii','source_ascii','hypotheses_ascii',
                  'quarantined','events','accepted_native','scientific_pass'}
            require(type(d) is dict and d.get('schema') in (SCHEMA,REPAIR_SCHEMA,HISTORY_SCHEMA,DTR_SCHEMA,EXPERIENCE_SCHEMA,RELATION_SCHEMA)
                and set(d)==(keys|{'compiled_ascii'} if d['schema']==RELATION_SCHEMA else
                             keys|{'repairs','history_ascii','dtr_ascii','experience_ascii','experience_source'} if d['schema']==EXPERIENCE_SCHEMA else
                             keys|{'repairs','history_ascii','dtr_ascii'} if d['schema']==DTR_SCHEMA else
                             keys|{'repairs','history_ascii'} if d['schema']==HISTORY_SCHEMA else
                             keys|{'repairs'} if d['schema']==REPAIR_SCHEMA else keys)
                and d['source_mode'] == SOURCE_MODE
                and d['accepted_native'] is False and d['scientific_pass'] is False
                and canonical(d) == raw, 'INTEGRATED_CHECKPOINT_CONTRACT')
            p = d['properties_ascii'].encode('ascii'); obj = cls(p, digest(p))
            s = d['source_ascii'].encode('ascii')
            obj._source = NativeContextAccumulator.restore(s, digest(s))
            require(obj._source._model.context_bits == obj._properties._bits, 'INTEGRATED_CONTEXT_JOIN')
            hs, qs, es = d['hypotheses_ascii'], d['quarantined'], d['events']
            require(type(hs) is list and len(hs) == 16 and type(qs) is list and len(qs) == 16
                and all(type(q) is bool for q in qs) and type(es) is list and len(es) <= MAX_EVENTS,
                'INTEGRATED_STATE_SHAPE')
            hypotheses = []
            for slot, h in enumerate(hs):
                n = obj._source._seen[slot].bit_count()
                require((h is not None) == (n >= 8 and n % 4 == 0), 'INTEGRATED_HYPOTHESIS_REQUIRED')
                if h is None:
                    hypotheses.append(None); continue
                h = h.encode('ascii')
                if json.loads(h)['schema']==SPARSE_SCHEMA:
                    require(d['schema'] in (REPAIR_SCHEMA,HISTORY_SCHEMA,DTR_SCHEMA,EXPERIENCE_SCHEMA),'INTEGRATED_SPARSE_VERSION')
                    hyp=NativeSparseHypothesis.restore(h,digest(h))
                else:hyp = NativeDegreeHypothesis.restore(h, digest(h))
                require(hyp.info()['source_checkpoint_sha256'] == digest(obj._view(slot)),
                        'INTEGRATED_HYPOTHESIS_SOURCE_JOIN')
                hypotheses.append(hyp)
            keys = set(); flags = [False]*16
            for e in es:
                require(type(e) is dict and set(e) == {'event_key','slot','source_ref','source_sha256',
                    'records','status','conflicting_packet'}, 'INTEGRATED_EVENT_SCHEMA')
                coordinates(e['slot'])
                require(pin(e['source_ref']) and pin(e['source_sha256'])
                    and e['event_key'] == digest(canonical([e['slot'],e['source_sha256'],e['source_ref']]))
                    and e['event_key'] not in keys and type(e['records']) is int
                    and 0 < e['records'] <= 2048, 'INTEGRATED_EVENT_PIN')
                require(not flags[e['slot']], 'INTEGRATED_POST_QUARANTINE_EVENT')
                keys.add(e['event_key'])
                if e['status'] == 'QUARANTINED':
                    packet = e['conflicting_packet']
                    require(type(packet) is list and len(packet) == e['records']
                            and digest(canonical(packet)) == e['source_sha256'], 'INTEGRATED_CONFLICT_PIN')
                    a, r = coordinates(e['slot']); bits = obj._source._model.context_bits
                    contradictions = 0
                    for row in packet:
                        require(type(row) is list and len(row) == 3, 'INTEGRATED_CONFLICT_ROW')
                        c = obj._source._model._context(row[0]); PublicCausalCells._bit(row[1], 'ACTION')
                        PublicCausalCells._bit(row[2], 'PUBLIC_OUTCOME')
                        old = obj._source.predict(a, c, row[1], retained=r)
                        contradictions += old is not None and old != row[2]
                    require(contradictions > 0, 'INTEGRATED_FAKE_QUARANTINE')
                    flags[e['slot']] = True
                else:
                    require(e['status'] == 'ACQUIRED' and e['conflicting_packet'] is None,
                            'INTEGRATED_EVENT_STATUS')
            require(flags == qs, 'INTEGRATED_QUARANTINE_LEDGER')
            obj._hypotheses = tuple(hypotheses); obj._quarantined = tuple(qs); obj._events = tuple(es)
            obj._schema=DTR_SCHEMA if d['schema']==EXPERIENCE_SCHEMA else d['schema'];repairs=d.get('repairs',[])
            require(type(repairs) is list and len(repairs)<=16,'INTEGRATED_REPAIR_LEDGER')
            slots=set()
            for e in repairs:
                require(type(e) is dict and set(e)=={'slot','old_hypothesis_sha256','source_view_sha256','rule'},
                        'INTEGRATED_REPAIR_SCHEMA')
                coordinates(e['slot']);h=hypotheses[e['slot']]
                require(e['slot'] not in slots and pin(e['old_hypothesis_sha256']) and pin(e['source_view_sha256'])
                    and type(h) is NativeSparseHypothesis and e['rule']==h.info()['rule'], 'INTEGRATED_REPAIR_JOIN')
                slots.add(e['slot'])
            require(slots=={s for s,h in enumerate(hypotheses) if type(h) is NativeSparseHypothesis},
                    'INTEGRATED_REPAIR_COMPLETENESS')
            obj._repairs=tuple(repairs)
            if d['schema'] == RELATION_SCHEMA:
                entries = d['compiled_ascii']
                require(type(entries) is list and len(entries) == 16 and any(v is not None for v in entries)
                        and not repairs, 'INTEGRATED_RELATION_ENTRIES')
                compiled = []
                for slot, value in enumerate(entries):
                    if value is None:
                        compiled.append(None)
                        continue
                    require(type(value) is str and type(hypotheses[slot]) is NativeDegreeHypothesis
                            and not qs[slot], 'INTEGRATED_RELATION_SLOT_SCOPE')
                    source_view = obj._view(slot)
                    raw_compiled = value.encode('ascii')
                    old = NativeCausalRelationPosterior.restore(raw_compiled, digest(raw_compiled))
                    fresh = NativeCausalRelationPosterior.fit_checkpoint(source_view, digest(source_view))
                    require(old.info()['source_checkpoint_sha256'] == digest(source_view)
                            and old.checkpoint() == fresh.checkpoint(),
                            'INTEGRATED_RELATION_RECALCULATED_SOURCE_JOIN')
                    compiled.append(old)
                obj._compiled = tuple(compiled)
            if obj._schema in (HISTORY_SCHEMA,DTR_SCHEMA):
                h=d['history_ascii'].encode('ascii')
                obj._history=NativeStochasticHistory.restore(h,digest(h))
            if obj._schema==DTR_SCHEMA:
                h=d['dtr_ascii'].encode('ascii');obj._dtr=NativeDTRHistory.restore(h,digest(h))
            if d['schema']==EXPERIENCE_SCHEMA:
                require(d['experience_source']==EXPERIENCE_SOURCE,'EPISODE_SOURCE_CHECKPOINT')
                experience=d['experience_ascii'].encode('ascii')
                obj._experience=NativeEpisodeExperience.restore(experience,digest(experience))
            require(obj.checkpoint() == raw, 'INTEGRATED_COLD_BYTES')
            return obj
        except (ValueError, TypeError, KeyError, UnicodeError, AttributeError, IndexError) as exc:
            raise ValueError('CKAD_INTEGRATED_CHECKPOINT_REJECTED') from exc
