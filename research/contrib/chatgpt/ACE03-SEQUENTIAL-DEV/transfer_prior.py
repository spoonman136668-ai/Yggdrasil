"""ACE03-XFER01: shared learned prior with frozen local snapshots.
Development-only successor; no native integration or scored study.
Reuse the pinned ACE03 State, feature grammar, and prequential selector.
"""
import hashlib
import math
import struct

from adaptive_contract import AdaptiveContract, State, ROW, LIMIT, sigmoid

MAGIC = b'ACE03XP1'
HEADER = struct.Struct('<8sHQ')
GATE = struct.Struct('<4d')
BLOCK = 4 * ROW.size
SLOT = 1 + 2 * BLOCK + GATE.size
LOG_ODDS_LIMIT = 16.0


def clone(rows):
    return [State.unpack(a.pack()) for a in rows]


def readout(rows, pattern):
    return tuple(a.forecasts(pattern)[a.choice()] for a in rows)


class TransferContract(AdaptiveContract):
    """One shared relation prior; no evaluator phase IDs or cross-key replay."""
    def __init__(self, public_keys=3):
        super().__init__(public_keys)
        self._shared = [State() for _ in range(4)]
        self._prior = [None] * public_keys
        self._log_odds = [(0.,)*4 for _ in range(public_keys)]

    def _components(self, key, pattern):
        local = readout(self._rows[key], pattern)
        snapshot = self._prior[key]
        prior = readout(self._shared if snapshot is None else snapshot, pattern)
        return local, prior

    def predict(self, key, pattern):
        if key is None:
            if type(pattern) is not int or not 0 <= pattern < 512:
                raise ValueError('invalid pattern')
            return None
        self._check(key, pattern)
        local, prior = self._components(key, pattern)
        return tuple((1-w)*p + w*q for p,q,w in
                     zip(local, prior, map(sigmoid, self._log_odds[key])))

    def observe(self, sequence, key, pattern, outcomes):
        self._check(key, pattern)
        if type(sequence) is not int or sequence != self.cursor or sequence >= LIMIT:
            raise ValueError('sequence mismatch or shared capacity exhausted')
        if (type(outcomes) is not tuple or len(outcomes) != 4 or
                any(type(y) is not int or y not in (0,1) for y in outcomes)):
            raise ValueError('four jointly observed binary outcomes required')
        # All forecasts precede the update. Snapshot once at first exposure.
        local, prior = self._components(key, pattern)
        snapshot = self._prior[key]
        if snapshot is None:
            snapshot = clone(self._shared)
        log_odds = tuple(max(-LOG_ODDS_LIMIT, min(LOG_ODDS_LIMIT,
                             z+(p-y)**2-(q-y)**2))
                         for z,p,q,y in zip(self._log_odds[key],local,prior,outcomes))
        # Stage both updates before committing either. No partial event.
        new_local, new_shared = clone(self._rows[key]), clone(self._shared)
        for a,b,y in zip(new_local,new_shared,outcomes):
            a.update(pattern,y)
            b.update(pattern,y)
        self._rows[key], self._shared = new_local, new_shared
        self._prior[key], self._log_odds[key] = snapshot, log_odds
        self.cursor += 1

    def checkpoint(self):
        payload = HEADER.pack(MAGIC,self.public_keys,self.cursor)
        payload += b''.join(a.pack() for a in self._shared)
        for rows,snapshot,odds in zip(self._rows,self._prior,self._log_odds):
            payload += bytes([int(snapshot is not None)])
            payload += b''.join(a.pack() for a in rows)
            payload += (bytes(BLOCK) if snapshot is None else
                        b''.join(a.pack() for a in snapshot))
            payload += GATE.pack(*odds)
        return payload + hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not HEADER.size+BLOCK+SLOT+32 <= len(raw) <= HEADER.size+BLOCK+16*SLOT+32:
            raise ValueError('checkpoint envelope')
        payload,digest = raw[:-32],raw[-32:]
        if hashlib.sha256(payload).digest() != digest:
            raise ValueError('checkpoint digest')
        magic,keys,cursor = HEADER.unpack_from(payload)
        if (magic != MAGIC or not 1 <= keys <= 16 or cursor > LIMIT
                or len(payload) != HEADER.size+BLOCK+keys*SLOT):
            raise ValueError('checkpoint schema')
        model = cls(keys)

        def rows_at(offset):
            rows = [State.unpack(payload[offset+j*ROW.size:offset+(j+1)*ROW.size])
                    for j in range(4)]
            if len({a.n for a in rows}) != 1:
                raise ValueError('joint exposure mismatch')
            return rows

        model._shared = rows_at(HEADER.size)
        if model._shared[0].n != cursor:
            raise ValueError('shared exposure mismatch')
        total = 0
        for key in range(keys):
            offset = HEADER.size+BLOCK+key*SLOT
            flag = payload[offset]
            rows = rows_at(offset+1)
            n = rows[0].n
            total += n
            odds = GATE.unpack_from(payload,offset+1+2*BLOCK)
            prior_offset = offset+1+BLOCK
            if flag != int(n > 0) or any(not math.isfinite(x) or
                                        abs(x) > min(n,LOG_ODDS_LIMIT) for x in odds):
                raise ValueError('invalid admission state')
            if flag:
                prior = rows_at(prior_offset)
                if prior[0].n > cursor-n:
                    raise ValueError('invalid snapshot exposure')
                model._prior[key] = prior
            elif any(payload[prior_offset:prior_offset+BLOCK]):
                raise ValueError('unexpected inactive snapshot')
            model._rows[key], model._log_odds[key] = rows, odds
        if total != cursor:
            raise ValueError('cursor/count inconsistency')
        model.cursor = cursor
        return model
