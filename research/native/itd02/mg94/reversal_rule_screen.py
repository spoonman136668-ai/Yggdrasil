"""MG94-H deterministic source-rule screen, not original-world experiment."""
from collections import defaultdict

def run():
    key=(0,0,1)
    stream=[1]*8+[0]*8
    native=defaultdict(lambda:[0,0])
    matched_count_control=defaultdict(lambda:[0,0])
    predictions=[]
    for outcome in stream:
        a=native[key]
        b=matched_count_control[key]
        assert a==b
        a[outcome]+=1
        b[outcome]+=1
        predictions.append(None if a[0]==a[1] else int(a[1]>a[0]))
    assert native[key]==matched_count_control[key]==[8,8]
    assert predictions[7]==1
    assert predictions[-1] is None
    print("PASS: 16 deterministic source-rule outcomes; final 8/8 tie; no advantage")

if __name__=="__main__":
    run()
