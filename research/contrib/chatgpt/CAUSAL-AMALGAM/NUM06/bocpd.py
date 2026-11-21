"""Exact finite run-length filter for an explicitly restricted A->B->A model.

Every possible B start is retained (no beam pruning). After B->A the archived
A predictive law is frozen; return likelihoods are independent conditional on
that fixed predictive law. Return end times with the same B start therefore
coalesce exactly. This is not an unrestricted recurrent-regime posterior.
No true switch times, private source fields, source generation or native writes.
"""
from __future__ import annotations
from bisect import bisect_right
import json
import math
from num05 import MAX_ROWS, canonical, digest, error, public_action, public_row, public_state, region, target
from bayesian_filter import HYPER_GRID

SCHEMA = "yggdrasil.num06.exact-finite-archive-runlength.v1"
NEG = -math.inf


def logsum(values):
    values = list(values)
    peak = max(values, default=NEG)
    if peak == NEG:
        return NEG
    return peak + math.log(sum(math.exp(v-peak) for v in values))


class ExactArchiveBOCPD:
    """Log-space A*, B(s), returned-A(s) posterior, initially A* with mass 1.

    Before every event after the first, A* starts B with hazard h; any B(s)
    returns to frozen archived A(s) with hazard h. Returned A is absorbing.
    Prefix sufficient statistics are stored only once per public context.
    O(t) hypotheses and O(t) work per observation, excluding cell lookup.
    """

    def __init__(self, *, hazard=.02, noise_sigma=.04, prior_std=.5):
        if any(type(v) is not float or not math.isfinite(v)
               for v in (hazard, noise_sigma, prior_std)):
            raise ValueError("NUM06_BOCPD_PARAMETER_TYPE")
        if not 0 < hazard < .5 or not 0 < noise_sigma <= 1 or not 0 < prior_std <= 2:
            raise ValueError("NUM06_BOCPD_PARAMETER_RANGE")
        self.hazard, self.noise_sigma, self.prior_std = hazard, noise_sigma, prior_std
        self._logh, self._logstay = math.log(hazard), math.log1p(-hazard)
        self.rows, self.seen, self.prefix = [], set(), {}
        self.a, self.b, self.returned = 0., [], []

    @staticmethod
    def _key(observation, action):
        return (region(observation), public_action(action))

    def _stats(self, key, stop):
        times, sums = self.prefix.get(key, ([], []))
        n = bisect_right(times, stop)
        return (n, sums[n-1]) if n else (0, (0.,0.,0.))

    def _predictive(self, key, start, stop):
        n0,u = self._stats(key, start)
        n1,v = self._stats(key, stop)
        noise2 = self.noise_sigma**2
        variance = 1. / (1. / self.prior_std**2 + (n1-n0) / noise2)
        return [(v[i]-u[i])*variance/noise2 for i in range(3)], noise2+variance

    def _prior(self):
        t = len(self.rows)
        if t == 0:
            return [(0, 0, self.a)]
        # Phase 0 (no change); 1 (novel run starts at s); 2 (returned A).
        states = [(0,0,self.a+self._logstay)]
        states += [(1,s,self.b[s-1]+self._logstay) for s in range(1,t)]
        states += [(1,t,self.a+self._logh)]
        states += [(2,s,logsum((self.returned[s-1],self.b[s-1]+self._logh)))
                   for s in range(1,t)]
        states += [(2,t,NEG)]
        return states

    def _components(self, observation, action):
        key = self._key(observation, action)
        t = len(self.rows)
        for phase,s,weight in self._prior():
            if phase == 0:
                start,stop = 0,t
            elif phase == 1:
                start,stop = s,t
            else:
                start,stop = 0,s
            center,var = self._predictive(key,start,stop)
            yield phase,s,weight,center,var

    def predict(self, observation, action):
        public_state(observation)
        public_action(action)
        mixture = [0.,0.,0.]
        for _,_,weight,center,_ in self._components(observation,action):
            for i in range(3):
                mixture[i] += math.exp(weight)*center[i]
        return mixture

    def observe(self,row):
        if type(row) is not dict or set(row) != {
          "id","source_tag","observation","action","successor","reward","terminated","truncated"}:
            raise ValueError("NUM06_BOCPD_ROW_SCHEMA")
        exact = public_row(row["id"],row["observation"],row["action"],
                           row["successor"],row["reward"],row["terminated"],
                           row["truncated"],source_tag=row["source_tag"])
        if row != exact or canonical(row) != canonical(exact):
            raise ValueError("NUM06_BOCPD_NONCANONICAL")
        if row["id"] in self.seen:
            raise ValueError("NUM06_BOCPD_DUPLICATE")
        if len(self.rows) >= MAX_ROWS:
            raise ValueError("NUM06_BOCPD_CAPACITY")
        z = target(row)
        t = len(self.rows)
        mixture = [0.,0.,0.]
        posterior = []
        for phase,s,weight,center,var in self._components(row["observation"],row["action"]):
            for i in range(3):
                mixture[i] += math.exp(weight)*center[i]
            ll = -.5*sum((z[i]-center[i])**2/var + math.log(2*math.pi*var) for i in range(3))
            posterior.append((phase,s,weight+ll))
        norm = logsum(x[2] for x in posterior)
        self.b, self.returned = [NEG]*t, [NEG]*t
        for phase,s,v in posterior:
            if phase == 0:
                self.a = v-norm
            elif phase == 1:
                self.b[s-1] = v-norm
            else:
                self.returned[s-1] = v-norm
        key = self._key(row["observation"],row["action"])
        times,sums = self.prefix.setdefault(key, ([],[]))
        last = sums[-1] if sums else (0.,0.,0.)
        times.append(t+1)
        sums.append(tuple(last[i]+z[i] for i in range(3)))
        self.rows.append(exact)
        self.seen.add(row["id"])
        return mixture

    def info(self):
        pm = [math.exp(self.a),math.exp(logsum(self.b)),math.exp(logsum(self.returned))]
        return {"rows":len(self.rows),"phase_posterior":pm,
                "novel_posterior":pm[1],"return_posterior":pm[2],
                "retained_start_hypotheses":len(self.b),
                "logical_banks_per_hypothesis":2,
                "source_owner_authenticated":False,"native_admission":False,
                "scientific_gain_verified":False}

    def checkpoint(self):
        def encode(v):
            return None if v == NEG else v
        raw = canonical({"schema":SCHEMA,"params":[self.hazard,self.noise_sigma,self.prior_std],
                         "rows":self.rows,"log_a":encode(self.a),
                         "log_b":[encode(v) for v in self.b],
                         "log_return":[encode(v) for v in self.returned],
                         "source_owner_authenticated":False,
                         "native_admission":False,"scientific_gain_verified":False})
        if len(raw)>300000:
            raise ValueError("NUM06_BOCPD_CHECKPOINT_BYTES")
        return raw

    @classmethod
    def restore(cls,raw,sha256):
        if type(raw) is not bytes or type(sha256) is not str or len(raw)>300000 or digest(raw)!=sha256:
            raise ValueError("NUM06_BOCPD_CHECKPOINT_HASH")
        try:
            obj=json.loads(raw)
            if (obj["schema"]!=SCHEMA or canonical(obj)!=raw or
                any(obj[k] is not False for k in ("source_owner_authenticated","native_admission","scientific_gain_verified"))):
                raise ValueError("NUM06_BOCPD_CHECKPOINT_FORMAT")
            p=obj["params"]
            m=cls(hazard=p[0],noise_sigma=p[1],prior_std=p[2])
            for row in obj["rows"]:
                m.observe(row)
            if m.checkpoint()!=raw:
                raise ValueError("NUM06_BOCPD_CHECKPOINT_REPLAY_MISMATCH")
            return m
        except (KeyError,TypeError,IndexError,OverflowError,RecursionError) as exc:
            raise ValueError("NUM06_BOCPD_CHECKPOINT_FORMAT") from exc


def fit_runlength(fit_cohorts,validation_cohorts):
    """Each cohort must already be independently admitted FIT or VALID evidence.
    This routine does not generate data, and is not an authority/roster check.
    Freeze chosen parameters before any held input.
    """
    if not fit_cohorts or not validation_cohorts:
        raise ValueError("NUM06_BOCPD_MISSING_FIT_VALID")
    if any(not cohort for cohort in (*fit_cohorts,*validation_cohorts)):
        raise ValueError("NUM06_BOCPD_EMPTY_COHORT")

    def score(rows,settings):
        m=ExactArchiveBOCPD(hazard=settings[0],noise_sigma=settings[1],prior_std=settings[2])
        return sum(error(m.observe(row),target(row)) for row in rows)/len(rows)

    ranked=[]
    for p in HYPER_GRID:
        a=sum(score(rows,p) for rows in fit_cohorts)/len(fit_cohorts)
        b=sum(score(rows,p) for rows in validation_cohorts)/len(validation_cohorts)
        ranked.append(((a+b)/2,p))
    score,p=min(ranked)
    return {"settings":list(p),"selection_mse":score,"grid_size":len(HYPER_GRID),
            "held_used":False,"scientific_gain_verified":False}
