"""Manual fixtures only. Independent exhaustive tiny-path reference."""
import json
import math
import unittest
from num05 import digest, public_row, target, region
from bayesian_filter import HYPER_GRID
from bocpd import ExactArchiveBOCPD, fit_runlength


def packet(i,z=(0.,0.,0.),action=4,state=(.7,.8)):
    return public_row(digest(("num06-bocpd-fixture-"+str(i)).encode()),state,action,
                      (state[0]+z[0],state[1]+z[1]),z[2])


def brute(rows, query, h=.08, sigma=.15, prior=.5):
    """Enumerate complete histories, including distinct return times.
    Independent probability-space calculation; no prefix sharing or coalescing.
    """
    paths=[(0,0,0,1.)]
    def distribution(start,stop,key,observed):
        matching=[target(r) for r in observed[start:stop]
                  if (region(r["observation"]),r["action"])==key]
        v=1/(1/prior**2+len(matching)/sigma**2)
        return [sum(z[j] for z in matching)*v/sigma**2 for j in range(3)],sigma**2+v
    def expand(paths,t):
        if t==0:
            return paths
        out=[]
        for phase,s,e,w in paths:
            if phase==0:
                out.extend(((0,0,0,w*(1-h)),(1,t,0,w*h)))
            elif phase==1:
                out.extend(((1,s,0,w*(1-h)),(2,s,t,w*h)))
            else:
                out.append((2,s,e,w))
        return out
    def emission(phase,s,t,key,observed):
        return distribution(0,t,key,observed) if phase==0 else (
               distribution(s,t,key,observed) if phase==1 else distribution(0,s,key,observed))
    for t,row in enumerate(rows):
        nextpaths=[]
        key=(region(row["observation"]),row["action"])
        z=target(row)
        for phase,s,e,w in expand(paths,t):
            mu,v=emission(phase,s,t,key,rows[:t])
            like=math.prod(math.exp(-.5*(z[j]-mu[j])**2/v)/math.sqrt(2*math.pi*v) for j in range(3))
            nextpaths.append((phase,s,e,w*like))
        normal=sum(p[3] for p in nextpaths)
        paths=[(phase,s,e,w/normal) for phase,s,e,w in nextpaths]
    masses=[sum(w for phase,s,e,w in paths if phase==j) for j in range(3)]
    qkey=(region(query["observation"]),query["action"])
    forecast=[0.,0.,0.]
    for phase,s,e,w in expand(paths,len(rows)):
        mu,_=emission(phase,s,len(rows),qkey,rows)
        for i in range(3):
            forecast[i]+=w*mu[i]
    return masses,forecast


class ExactBOCPDTests(unittest.TestCase):
    def test_exhaustive_reference(self):
        m=ExactArchiveBOCPD(hazard=.08,noise_sigma=.15,prior_std=.5)
        rows=[packet(i,z,action=4 if i!=3 else 0)
              for i,z in enumerate([(.1,.02,.03),(.1,.02,.03),(.6,-.4,.5),
                                    (.7,-.5,.2),(.6,-.4,.5),(.1,.02,.03),(.1,.02,.03)])]
        for t,row in enumerate(rows):
            mass,p=brute(rows[:t],row)
            for x,y in zip(p,m.predict(row["observation"],row["action"])):
                self.assertAlmostEqual(x,y,places=12)
            for x,y in zip(mass,m.info()["phase_posterior"]):
                self.assertAlmostEqual(x,y,places=12)
            self.assertEqual(m.predict(row["observation"],row["action"]),m.observe(row))
        self.assertEqual(m.info()["retained_start_hypotheses"],len(rows)-1)

    def test_return_and_null(self):
        m=ExactArchiveBOCPD()
        stationary=ExactArchiveBOCPD()
        a=(.13,-.12,.17); b=(.9,-.7,.8)
        peak=0.
        for t in range(150):
            m.observe(packet(t,a if t<55 or t>=105 else b))
            stationary.observe(packet(t,a))
            peak=max(peak,stationary.info()["novel_posterior"])
            if t==95:
                self.assertGreater(m.info()["novel_posterior"],.95)
        self.assertGreater(m.info()["return_posterior"],.95)
        self.assertLess(peak,.8)
        self.assertAlmostEqual(sum(m.info()["phase_posterior"]),1.,places=10)
        self.assertEqual(len(m.b),149)

    def test_cold_and_negatives(self):
        m=ExactArchiveBOCPD()
        rows=[packet(i,(.13,-.2,.4) if i<20 else (.5,-.8,.7)) for i in range(35)]
        for r in rows:
            m.observe(r)
        raw=m.checkpoint()
        restored=ExactArchiveBOCPD.restore(raw,digest(raw))
        self.assertEqual(restored.checkpoint(),raw)
        with self.assertRaises(ValueError):
            m.observe(rows[0])
        bad=dict(packet(40));bad["true_phase"]=1
        with self.assertRaises(ValueError):
            m.observe(bad)
        self.assertEqual(m.checkpoint(),raw)
        data=json.loads(raw);data["log_b"][0]+=1.
        bad=json.dumps(data,sort_keys=True,separators=(",",":")).encode()
        with self.assertRaises(ValueError):
            ExactArchiveBOCPD.restore(bad,digest(bad))
        with self.assertRaises(ValueError):
            ExactArchiveBOCPD.restore(raw,"0"*64)

    def test_fit_small_public_fixtures(self):
        fit=[[packet(i,(.1,.2,.3)) for i in range(8)]]
        valid=[[packet(100+i,(.12,.19,.28)) for i in range(9)]]
        result=fit_runlength(fit,valid)
        self.assertEqual(result["grid_size"],12)
        self.assertIn(tuple(result["settings"]),HYPER_GRID)
        self.assertFalse(result["held_used"])
        self.assertFalse(result["scientific_gain_verified"])
        with self.assertRaises(ValueError):
            fit_runlength(fit,[[]])

    def test_reject_parameter_invalid(self):
        for params in ({"hazard":0.},{"hazard":.5},{"noise_sigma":float("nan")},
                       {"prior_std":True},{"noise_sigma":-1.}):
            with self.assertRaises(ValueError):
                ExactArchiveBOCPD(**params)

if __name__=="__main__":
    unittest.main()
