"""Independent compact exact-rational replayer for ENERGY-22; no native imports."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product

def draw(*x):
    return sha256('|'.join(map(str,('energy22',)+x)).encode('ascii')).digest()[0]
def prob(*x):
    return F(1 + draw(*x)%8, 10)
def choose(pt,py):
    vals=[]
    for a in (0,1):
        best=[max(py(a,s,b) for b in (0,1)) for s in (0,1)]
        vals.append((1-pt(a))*best[0]+pt(a)*best[1])
    return int(vals[1]>vals[0])

checks=wrong_terminal=wrong_candidate=wrong_action=0
for old in (1,2,3,5):
 for case in range(96):
    trans={(h,a):prob(old,case,h,'t',a) for h in range(old+1) for a in (0,1)}
    reward={(h,a,s,b):prob(old,case,h,'q',a,s,b) for h in range(old+1)
            for a,s,b in product((0,1),repeat=3)}
    w=[F(7,old*8)]*old+[F(1,8)]
    def joint(a,s,b,y):
        return sum((w[h]*(trans[h,a] if s else 1-trans[h,a])*
          (reward[h,a,s,b] if y else 1-reward[h,a,s,b])
          for h in range(old+1)), F(0))
    def pt(a):
        return sum((w[h]*trans[h,a] for h in range(old+1)),F(0))
    def py(a,s,b):
        z=sum((w[h]*(trans[h,a] if s else 1-trans[h,a]) for h in range(old+1)),F(0))
        return sum((w[h]*(trans[h,a] if s else 1-trans[h,a])*
                 reward[h,a,s,b] for h in range(old+1)),F(0))/z
    for step in range(5):
        assert sum(w)==1; checks+=2
        for a in (0,1):
            assert pt(a)==joint(a,1,0,0)+joint(a,1,0,1);checks+=1
            for s,b in product((0,1),repeat=2):
                actual=py(a,s,b)
                assert actual==joint(a,s,b,1)/(joint(a,s,b,0)+joint(a,s,b,1));checks+=1
                wrong_terminal+=sum((w[h]*reward[h,a,s,b] for h in range(old+1)),F(0))!=actual
                h=max(range(old+1),key=lambda j:(w[j]*(trans[j,a] if s else 1-trans[j,a]),j))
                wrong_candidate+=reward[h,a,s,b]!=actual
        expected=choose(pt,py)
        ep=lambda a: joint(a,1,0,0)+joint(a,1,0,1)
        eq=lambda a,s,b:joint(a,s,b,1)/(joint(a,s,b,0)+joint(a,s,b,1))
        assert expected==choose(ep,eq);checks+=1
        prior=max(range(old+1),key=lambda h:(w[h],h))
        hp=lambda a:trans[prior,a]
        hq=lambda a,s,b:reward[max(range(old+1),key=lambda h:(w[h]*(trans[h,a] if s else 1-trans[h,a]),h)),a,s,b]
        wrong_action+=expected!=choose(hp,hq)
        if step==4:continue
        a=draw(old,case,step,'first')%2
        s=draw(old,case,step,'state')%2
        b=draw(old,case,step,'second')%2
        y=draw(old,case,step,'reward')%2
        mass=[w[h]*(trans[h,a] if s else 1-trans[h,a])*
              (reward[h,a,s,b] if y else 1-reward[h,a,s,b]) for h in range(old+1)]
        z=sum(mass)
        w=[v/z for v in mass]
        checks+=1
        if step%2==0:trans[old,a]=F(step+2+s,step+5)
        else:reward[old,a,s,b]=F(step+2+y,step+5)
assert (checks,wrong_terminal,wrong_candidate,wrong_action)==(26496,14519,14987,326)
print('ENERGY-22 REPLAY PASS: 384 cases, 1920 points,',checks,'exact equalities;',
      wrong_terminal,wrong_candidate,wrong_action,'negative-control differences')
