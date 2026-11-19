"""Opt-in Yggdrasil native capacity continuation, preserving original 7-component weights.

The original fully trained native+six JEPA checkpoint is an immutable archive.
New genuine public action/consequence episodes append to bounded native shards;
cloned six JEPA heads continue *their original learned parameters*, with epoch
step counters for legacy specialists whose fixed 1024-episode validation cap
otherwise prevents any further training. This is DEVELOPMENT engineering only.

This adapter does not make a scientific causal transfer claim and does not
silently promote or blend archive/new predictions into an owner policy.
"""
from __future__ import annotations
import json

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist
from yggdrasil.native_jepa_future import (
    NativeFutureStateLearner, FutureStateHead, HORIZON,
    observed_features, primary_probabilities, targets, public_observed,
)

SCHEMA = "yggdrasil.cap01.segmented-cumulative-jepa.v1"
MAX_SHARD = 64
MAX_SHARDS = 4
MAX_CHECKPOINT_BYTES = 2 * 1024 * 1024
EVENT_FIELDS = ("identifier","views","first","state","second","reward","post")


def _bit(value):
    require(type(value) is int and value in (0, 1), "CAP01_PUBLIC_BIT")
    return value


def _views(views):
    require(type(views) is tuple and len(views) == 2 and
            all(type(view) is tuple and len(view) == 2 for view in views),
            "CAP01_PAIRED_VIEWS")
    for view in views:
        for item in view:
            _bit(item)
    return views


def _event(identifier, views, row, post):
    require(pin(identifier), "CAP01_SOURCE_ID")
    views = _views(views)
    require(type(row) is dict and set(row) == {"s1", "x1", "s2", "x2", "y"},
            "CAP01_PUBLIC_ROW_KEYS")
    for value in row.values():
        _bit(value)
    post = tuple(post) if type(post) is tuple else post
    require(type(post) is tuple and len(post) == 3 and
            all(type(x) is int and x in (0, 1) for x in post),
            "CAP01_OBSERVED_POST")
    require(row["s1"] == views[0][0] and row["s2"] == post[1],
            "CAP01_PUBLIC_SOURCE_CONSISTENCY")
    return identifier, views, row["x1"], row["s2"], row["x2"], row["y"], post


def _row(event):
    _, views, first, state, second, reward, _ = event
    return {"s1":views[0][0], "x1":first, "s2":state,
            "x2":second, "y":reward}


def _as_native(event):
    identifier, views, first, state, second, reward, _ = event
    return (identifier, views, first, state, second, reward)


def _window(event):
    return {"post":event[6], "row":_row(event)}


class SegmentedNativeJEPA:
    """An isolated archive + ongoing real native segment + six continuing heads.

    Same original model, not a reset. The earlier checkpoint remains exact.
    Specialist epochs separate the fixed-size legacy step-counter contract
    from actual continuing weights; total steps are offsets+epoch steps.
    """

    def __init__(self, archive_raw, source, segments, events, one, temporal,
                 future, offsets):
        self._archive_raw = archive_raw
        self._source = source
        self._segments = segments
        self._events = events
        self._one = one
        self._temporal = temporal
        self._future = future
        self._offsets = offsets

    @classmethod
    def from_archive(cls, raw, expected_sha):
        require(type(raw) is bytes and 0 < len(raw) < MAX_CHECKPOINT_BYTES
                and pin(expected_sha) and digest(raw) == expected_sha,
                "CAP01_ORIGINAL_ARCHIVE_SHA")
        original = NativeFutureStateLearner.restore(raw, expected_sha)
        one = (original.original.base.transition.clone(),
               original.original.base.reward.clone())
        temporal = (original.original.transition.clone(),
                    original.original.reward.clone())
        offsets = (tuple(head.steps for head in one),
                   tuple(head.steps for head in temporal))
        # Only counter EPOCH rolls over; no trained parameter is reinitialized.
        for head in (*one, *temporal):
            head.steps = 0
        future = (FutureStateHead.restore(original.sensory.checkpoint()),
                  FutureStateHead.restore(original.reward.checkpoint()))
        return cls(raw, original, (NativeEpisodeExperience(repair=True),),
                   (), one, temporal, future, offsets)

    @property
    def archive_sha256(self):
        return digest(self._archive_raw)

    @property
    def original_count(self):
        return len(self._source.original.base.native._ledger)

    @property
    def new_count(self):
        return len(self._events)

    @property
    def total_count(self):
        return self.original_count + self.new_count

    @property
    def future_windows(self):
        return max(0, self.new_count - HORIZON + 1)

    def _history(self):
        return self._source.original.base.native._ledger + tuple(
            _as_native(event) for event in self._events)

    def _validate_custody(self):
        original = self._source.original.base.native._ledger
        seen = {row[0] for row in original}
        require(len(seen) == len(original), "CAP01_ORIGINAL_IDS")
        require(len(self._segments) in range(1, MAX_SHARDS + 1),
                "CAP01_SEGMENT_COUNT")
        require(len(self._events) <= MAX_SHARD*MAX_SHARDS and
                self.total_count >= self.original_count,
                "CAP01_TOTAL_CAPACITY")
        for index, shard in enumerate(self._segments):
            require(isinstance(shard, NativeEpisodeExperience) and
                    0 <= len(shard._ledger) <= MAX_SHARD,
                    "CAP01_SHARD_CAPACITY")
            if index < len(self._segments)-1:
                require(len(shard._ledger) == MAX_SHARD,
                        "CAP01_SHARD_GAP")
        reconstructed = tuple(event for shard in self._segments
                              for event in shard._ledger)
        require(len(reconstructed) == len(self._events) and
                reconstructed == tuple(_as_native(x) for x in self._events),
                "CAP01_SHARD_LEDGER_PROVENANCE")
        for i, event in enumerate(self._events):
            identifier = event[0]
            require(identifier not in seen, "CAP01_GLOBAL_ID_CONFLICT")
            seen.add(identifier)
            if i+1<len(self._events):
                next_views = self._events[i+1][1]
                require(event[6] ==
                        (next_views[0][0], next_views[0][1],
                         next_views[1][1]), "CAP01_PUBLIC_CONTINUITY")
        require(all(head.steps == 3*self.new_count
                    for head in (*self._one,*self._temporal)),
                "CAP01_LEARNED_STEP_COUNT")
        base_one = (self._source.original.base.transition,
                    self._source.original.base.reward)
        base_temp = (self._source.original.transition,
                     self._source.original.reward)
        require(self._offsets ==
                (tuple(x.steps for x in base_one),
                 tuple(x.steps for x in base_temp)),
                "CAP01_ORIGINAL_STEP_EPOCH")
        old_future = (self._source.sensory,self._source.reward)
        require(all(head.windows == original.windows + self.future_windows
                    for head,original in zip(self._future,old_future)),
                "CAP01_FUTURE_WINDOWS")
        require(self._source.checkpoint() == self._archive_raw,
                "CAP01_ARCHIVE_MUTATION")
        return True

    def archived_forecast(self, view, first, state=None, second=None):
        """The exact immutable native readout. Stage 2 requires witnessed s2."""
        require((state is None) == (second is None),
                "CAP01_TWO_STAGE_PREDICTION")
        native = self._source.original.base.native
        if state is None:
            return float(native.context_forecast(view,first))
        return float(native.context_forecast(view,first,state,second))

    def active_forecast(self, view, first, state=None, second=None):
        """New learned segment readout, separate from preserved archive."""
        require((state is None) == (second is None),
                "CAP01_TWO_STAGE_PREDICTION")
        return float(self._segments[-1].forecast(view,first,state,second))

    def specialist_forecast(self, views, first, state=None, second=None):
        """Two short-horizon JEPA learners forecast only the observed stage."""
        views = _views(views)
        prior = self._history()
        if state is None:
            require(second is None, "CAP01_TWO_STAGE_PREDICTION")
            return (self._one[0].probability(views,first),
                    self._temporal[0].probability(views,(first,),prior))
        require(second is not None,"CAP01_SECOND_ACTION")
        return (self._one[1].probability(views,first,state,second),
                self._temporal[1].probability(
                    views,(first,state,second),prior))

    def future_forecast(self, views, public_plans):
        """Three preannounced action pairs; NO future state is an input."""
        x = observed_features(_views(views),public_plans,self._history())
        return tuple(float(z) for z in primary_probabilities(
            self._future[0].predict(x),self._future[1].predict(x)))

    def observe(self, identifier, views, row, post):
        """Consume exactly one actually observed public intervention row.

        The original frozen source model is NEVER updated. Four cloned
        specialist sets learn after the witnessed s2/reward. Future heads
        learn a completed public 3-step window only once all 3 real
        post-states have been observed.
        """
        event = _event(identifier,views,row,post)
        old=self._source.original.base.native._ids.get(identifier)
        require(old is None, "CAP01_OLD_ARCHIVE_ID_PROTECTED")
        for previous in self._events:
            if previous[0]==identifier:
                require(previous==event,"CAP01_CONFLICTING_REPLAY")
                return self
        require(self.new_count < MAX_SHARD*MAX_SHARDS,
                "CAP01_ALL_SHARDS_FULL")
        candidate = SegmentedNativeJEPA(
            self._archive_raw,self._source,self._segments,self._events,
            tuple(x.clone() for x in self._one),
            tuple(x.clone() for x in self._temporal),
            tuple(FutureStateHead.restore(x.checkpoint()) for x in self._future),
            self._offsets,
        )
        prior = self._history()
        shards=list(candidate._segments)
        if len(shards[-1]._ledger)==MAX_SHARD:
            require(len(shards)<MAX_SHARDS, "CAP01_SHARD_COUNT_LIMIT")
            shards.append(NativeEpisodeExperience(repair=True))
        shards[-1]=shards[-1].observe(identifier,views,row)
        candidate._segments=tuple(shards)
        candidate._one[0].observe(views,(row["x1"],),row["s2"])
        candidate._one[1].observe(
            views,(row["x1"],row["s2"],row["x2"]),row["y"])
        candidate._temporal[0].observe(
            views,(row["x1"],),prior,row["s2"])
        candidate._temporal[1].observe(
            views,(row["x1"],row["s2"],row["x2"]),prior,row["y"])
        candidate._events=self._events+(event,)
        if candidate.new_count>=HORIZON:
            start=candidate.new_count-HORIZON
            window=candidate._events[start:start+HORIZON]
            # Reconstruct action plans and history only from witnessed
            # source. Forecasts were created earlier from announced actions.
            old_ledger = candidate._source.original.base.native._ledger
            history=old_ledger+tuple(_as_native(e)
                                      for e in candidate._events[:start])
            plans=tuple((e[2],e[4]) for e in window)
            x=observed_features(window[0][1],plans,history)
            sensor,reward=targets(tuple(_window(e) for e in window))
            candidate._future[0].learn(x,sensor)
            candidate._future[1].learn(x,reward)
        candidate._validate_custody()
        return candidate

    def checkpoint(self):
        self._validate_custody()
        parts=[]
        for segment in self._segments:
            raw=segment.checkpoint()
            parts.append({"sha256":digest(raw),"ascii":raw.decode("ascii")})
        data={
            "schema":SCHEMA,
            "archive_sha256":digest(self._archive_raw),
            "archive_ascii":self._archive_raw.decode("ascii"),
            "original_count":self.original_count,
            "total_count":self.total_count,
            "segments":parts,
            "events":[
                {key:value for key,value in zip(EVENT_FIELDS,e)}
                for e in self._events
            ],
            "offsets":self._offsets,
            "one":[head.as_data() for head in self._one],
            "temporal":[head.data() for head in self._temporal],
            "future":[head.checkpoint() for head in self._future],
        }
        raw=canonical(data)
        require(0<len(raw)<=MAX_CHECKPOINT_BYTES,
                "CAP01_ROOT_CHECKPOINT_BYTES")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha):
        require(type(raw) is bytes and 0<len(raw)<=MAX_CHECKPOINT_BYTES and
                pin(expected_sha) and digest(raw)==expected_sha,
                "CAP01_CHECKPOINT_SHA")
        try:
            data=json.loads(raw.decode("ascii"))
            require(type(data) is dict and set(data)=={
                "schema","archive_sha256","archive_ascii",
                "original_count","total_count","segments","events",
                "offsets","one","temporal","future",
            } and data["schema"]==SCHEMA and canonical(data)==raw,
                    "CAP01_CHECKPOINT_SCHEMA")
            archive=data["archive_ascii"].encode("ascii")
            current=cls.from_archive(archive,data["archive_sha256"])
            require(data["original_count"]==current.original_count and
                    len(data["events"])<=MAX_SHARD*MAX_SHARDS and
                    len(data["segments"]) in range(1,MAX_SHARDS+1),
                    "CAP01_RESTORE_COUNTS")
            # Full learned-weight and witness-custody replay from the
            # untouched original, not simply trusting a matching new hash.
            for record in data["events"]:
                require(type(record) is dict and set(record)==set(EVENT_FIELDS),
                        "CAP01_RESTORE_EVENT_FIELDS")
                views=tuple(tuple(x) for x in record["views"])
                post=tuple(record["post"])
                row={"s1":views[0][0],"x1":record["first"],
                     "s2":record["state"],"x2":record["second"],
                     "y":record["reward"]}
                current=current.observe(record["identifier"],views,row,post)
            require(current.total_count==data["total_count"] and
                    current.checkpoint()==raw,
                    "CAP01_FORGED_OR_DIVERGED_COLD_REPLAY")
            return current
        except (KeyError,TypeError,ValueError,AttributeError,IndexError,
                UnicodeError,OverflowError,RecursionError) as exc:
            raise ValueError("YGG_CAP01_COLD_REPLAY_REJECTED") from exc
