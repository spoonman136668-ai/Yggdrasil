//! V32E new quarantined per-cue/action consecutive-contradiction consensus gate; original V32A unchanged.
 //! Quarantined source-only 8-cell prototype. Not original native learner.
use std::convert::TryInto;

const N: usize = 8;
const C: usize = 4;
const A: usize = 3;
const HOPS: usize = 4;
const GAIN: f64 = 0.92;
const RATE: f64 = 0.20;
const INPUT: [usize; C] = [1, 3, 7, 4];
const OUTPUT: [usize; A] = [0, 2, 5];
const MAGIC: &[u8; 8] = b"V32EMIC1";
const WINDOW: usize = 24; // 12 streak bytes + 12 distinct-pair certification bytes
const PAIRS: usize = 12;
const CONSENSUS: u64 = 6;
const EVIDENCE_WINDOW_EVENTS: usize = 36;
const MATURITY: u64 = 180;
const SIGN_EPS: f64 = 1e-6;
const SIZE: usize = 8 + 8 + N * (8 + 8 + 16 + 8 + 8 + 8 + 8 + WINDOW + 2*A*C*8) + 8;

struct Cell {
    id: usize,
    left: usize,
    right: usize,
    cue: [f64; C],
    next_cue: [f64; C],
    weights: [[[f64; C]; A]; 2],
    local_updates: u64,
    active: usize,
    age: [u64; 2],
    switches: u64,
    pair_streaks: [u8; PAIRS],
    pair_certified: [u8; PAIRS],
    evidence_events: usize,
    confirmed_pairs: u64,
    evidence_resets: u64,
    credit: f64,
    next_credit: f64,
    score: f64,
    next_score: f64,
}

impl Cell {
    fn new(id: usize) -> Self {
        Self {
            id, left:(id+N-1)%N, right:(id+1)%N,
            cue:[0.; C], next_cue:[0.; C],
            weights:[[[0.; C]; A]; 2],local_updates:0,
            active:0, age:[0,0], switches:0,
            pair_streaks:[0;PAIRS],pair_certified:[0;PAIRS],
            evidence_events:0,confirmed_pairs:0,evidence_resets:0,
            credit:0., next_credit:0.,score:0.,next_score:0.,
        }
    }
}
pub struct Ring {
    cells: Vec<Box<Cell>>,
    pending: bool,
    observed: i32,
    update_calls: u64,
}
impl Ring {
    fn new() -> Self {
        let mut cells=Vec::with_capacity(N);
        for i in 0..N { cells.push(Box::new(Cell::new(i))); }
        Self {cells,pending:false,observed:-1,update_calls:0}
    }
    fn layout_ok(&self) -> bool {
        if self.cells.len()!=N {return false}
        for i in 0..N {
            let x=&self.cells[i];
            if x.id!=i || x.left!=(i+N-1)%N || x.right!=(i+1)%N {return false}
            for j in 0..i {
                if std::ptr::eq::<Cell>(&*self.cells[j],&**x){return false}
            }
        }
        true
    }
    fn observe(&mut self,cue:usize) {
        for x in &mut self.cells {x.cue=[0.;C]; x.next_cue=[0.;C];}
        self.cells[INPUT[cue]].cue[cue]=1.;
        for _ in 0..HOPS {
            for i in 0..N {
                let left=self.cells[i].left;
                let right=self.cells[i].right;
                for c in 0..C {
                    let own=self.cells[i].cue[c];
                    let l=self.cells[left].cue[c];
                    let r=self.cells[right].cue[c];
                    let peer=if l>=r{l}else{r};
                    let incoming=GAIN*peer;
                    self.cells[i].next_cue[c]=if own>=incoming{own}else{incoming};
                }
            }
            for x in &mut self.cells {
                std::mem::swap(&mut x.cue,&mut x.next_cue);
            }
        }
        self.pending=true;
        self.observed=cue as i32;
    }
    fn score(&mut self, action:usize) -> f64 {
        for x in &mut self.cells {
            x.score=(0..C).map(|c|x.cue[c]*x.weights[x.active][action][c]).sum();
        }
        for _ in 0..HOPS {
            for i in 0..N {
                let left=self.cells[i].left;
                let right=self.cells[i].right;
                self.cells[i].next_score=
                    (self.cells[i].score * 0.5) +
                    (self.cells[left].score * 0.25) +
                    (self.cells[right].score * 0.25);
            }
            for x in &mut self.cells {
                std::mem::swap(&mut x.score,&mut x.next_score);
            }
        }
        self.cells[OUTPUT[action]].score
    }
    fn feedback(&mut self,action:usize,reward:f64,learning:bool){
        if learning {
            for x in &mut self.cells {x.credit=0.;x.next_credit=0.;}
            self.cells[OUTPUT[action]].credit=1.;
            for _ in 0..HOPS {
                for i in 0..N {
                    let left=self.cells[i].left;
                    let right=self.cells[i].right;
                    let own=self.cells[i].credit;
                    let l=self.cells[left].credit;
                    let r=self.cells[right].credit;
                    let near=if l>=r{l}else{r};
                    let input=GAIN*near;
                    self.cells[i].next_credit=if own>=input{own}else{input};
                }
                for x in &mut self.cells {
                    std::mem::swap(&mut x.credit,&mut x.next_credit);
                }
            }
            for x in &mut self.cells {
                // A different local cue-action pair is distinct evidence,
                // not another global-surprise event. No phase flag/oracle.
                let cue=self.observed as usize;
                if x.age[x.active] >= MATURITY {
                    if x.evidence_events == EVIDENCE_WINDOW_EVENTS {
                        x.pair_streaks=[0;PAIRS];
                        x.pair_certified=[0;PAIRS];
                        x.evidence_events=0;
                        x.confirmed_pairs=0;
                        x.evidence_resets+=1;
                    }
                    x.evidence_events+=1;
                    let pair=cue*A+action;
                    let weight=x.weights[x.active][action][cue];
                    let wrong=weight.abs()>SIGN_EPS && ((weight>0.0)!=(reward>0.0));
                    if wrong {
                        x.pair_streaks[pair]=(x.pair_streaks[pair]+1).min(3);
                        if x.pair_streaks[pair]==3 && x.pair_certified[pair]==0 {
                            x.pair_certified[pair]=1;
                            x.confirmed_pairs+=1;
                        }
                    } else {
                        x.pair_streaks[pair]=0;
                    }
                    if x.confirmed_pairs>=CONSENSUS {
                        x.active=1-x.active;
                        x.switches+=1;
                        x.pair_streaks=[0;PAIRS];
                        x.pair_certified=[0;PAIRS];
                        x.evidence_events=0;
                        x.confirmed_pairs=0;
                        x.evidence_resets=0;
                    }
                }
                let credit=RATE*reward*x.credit;
                let mut any=false;
                for c in 0..C {
                    let delta=credit*x.cue[c];
                    if delta!=0. {
                        let value=x.weights[x.active][action][c]+delta;
                        x.weights[x.active][action][c]=value.max(-8.).min(8.);
                        any=true;
                    }
                }
                if any {
                    x.local_updates+=1;
                    x.age[x.active]+=1;
                }
            }
            self.update_calls+=1;
        }
        self.pending=false;
    }
}
fn checksum(data:&[u8])->u64 {
    let mut h:u64=0xcbf29ce484222325;
    for b in data {h^=*b as u64; h=h.wrapping_mul(0x100000001b3);}
    h
}
#[no_mangle]
pub extern "C" fn v32e_new()->*mut Ring {
    Box::into_raw(Box::new(Ring::new()))
}
#[no_mangle]
pub unsafe extern "C" fn v32e_free(p:*mut Ring) {
    if !p.is_null() {drop(Box::from_raw(p));}
}
#[no_mangle]
pub extern "C" fn v32e_schema()->u64 {0x5633324500010001}
#[no_mangle]
pub extern "C" fn v32e_checkpoint_size()->usize {SIZE}
#[no_mangle]
pub unsafe extern "C" fn v32e_observe(p:*mut Ring,cue:i32)->i32 {
    if p.is_null(){return -1}
    if !(0..4).contains(&cue){return -2}
    let r=&mut *p;
    if !r.layout_ok(){return -3}
    r.observe(cue as usize);
    0
}
#[no_mangle]
pub unsafe extern "C" fn v32e_scores(p:*mut Ring,out:*mut f64,len:usize)->i32 {
    if p.is_null() || out.is_null(){return -1}
    if len!=A{return -2}
    let r=&mut *p;
    if !r.layout_ok() || !r.pending{return -3}
    let s=std::slice::from_raw_parts_mut(out,A);
    for a in 0..A {s[a]=r.score(a);}
    if s.iter().any(|v|!v.is_finite()){return -4}
    0
}
#[no_mangle]
pub unsafe extern "C" fn v32e_feedback(p:*mut Ring,action:i32,reward:f64,learning:i32)->i32 {
    if p.is_null(){return -1}
    if !(0..3).contains(&action) || !reward.is_finite()
        || reward.abs()>1. || !(0..2).contains(&learning) {return -2}
    let r=&mut *p;
    if !r.layout_ok() || !r.pending{return -3}
    r.feedback(action as usize,reward,learning==1);
    0
}
#[no_mangle]
pub unsafe extern "C" fn v32e_cell_address(p:*const Ring, index:i32)->usize {
    if p.is_null() || !(0..8).contains(&index){return 0}
    let r=&*p;if !r.layout_ok(){return 0}
    (&*r.cells[index as usize] as *const Cell) as usize
}
#[no_mangle]
pub unsafe extern "C" fn v32e_neighbor(p:*const Ring,i:i32,side:i32)->i32 {
    if p.is_null() || !(0..8).contains(&i) || !(0..2).contains(&side){return -1}
    let r=&*p;if !r.layout_ok(){return -1}
    if side==0{r.cells[i as usize].left as i32}
    else {r.cells[i as usize].right as i32}
}
#[no_mangle]
pub unsafe extern "C" fn v32e_cell_updates(p:*const Ring,i:i32)->i64 {
    if p.is_null() || !(0..8).contains(&i){return -1}
    let r=&*p;if !r.layout_ok(){return -1}
    r.cells[i as usize].local_updates as i64
}
#[no_mangle]
pub unsafe extern "C" fn v32e_cell_active(p:*const Ring,i:i32)->i32 {
    if p.is_null() || !(0..8).contains(&i){return -1}
    let r=&*p; if !r.layout_ok(){return -1}
    r.cells[i as usize].active as i32
}
#[no_mangle]
pub unsafe extern "C" fn v32e_cell_switches(p:*const Ring,i:i32)->i64 {
    if p.is_null() || !(0..8).contains(&i){return -1}
    let r=&*p; if !r.layout_ok(){return -1}
    r.cells[i as usize].switches as i64
}
#[no_mangle]
pub unsafe extern "C" fn v32e_cell_bank_age(p:*const Ring,i:i32,bank:i32)->i64 {
    if p.is_null() || !(0..8).contains(&i) || !(0..2).contains(&bank){return -1}
    let r=&*p; if !r.layout_ok(){return -1}
    r.cells[i as usize].age[bank as usize] as i64
}
#[no_mangle]
pub unsafe extern "C" fn v32e_save(p:*const Ring,out:*mut u8,len:usize)->i32{
    if p.is_null() || out.is_null(){return -1}
    if len!=SIZE{return -2}
    let r=&*p;
    if !r.layout_ok() {return -3}
    let mut data=Vec::with_capacity(SIZE);
    data.extend_from_slice(MAGIC);
    data.extend_from_slice(&r.update_calls.to_le_bytes());
    for x in &r.cells{
        data.extend_from_slice(&x.local_updates.to_le_bytes());
        data.extend_from_slice(&(x.active as u64).to_le_bytes());
        for b in 0..2 {data.extend_from_slice(&x.age[b].to_le_bytes());}
        data.extend_from_slice(&x.switches.to_le_bytes());
        data.extend_from_slice(&(x.evidence_events as u64).to_le_bytes());
        data.extend_from_slice(&x.confirmed_pairs.to_le_bytes());
        data.extend_from_slice(&x.evidence_resets.to_le_bytes());
        data.extend_from_slice(&x.pair_streaks);
        data.extend_from_slice(&x.pair_certified);
        for b in 0..2 {for a in 0..A {for c in 0..C {
            data.extend_from_slice(&x.weights[b][a][c].to_le_bytes());
        }}}
    }
    let hash=checksum(&data);
    data.extend_from_slice(&hash.to_le_bytes());
    if data.len()!=SIZE{return -4}
    std::slice::from_raw_parts_mut(out,SIZE).copy_from_slice(&data);
    0
}
#[no_mangle]
pub unsafe extern "C" fn v32e_load(p:*mut Ring,buffer:*const u8,len:usize)->i32{
    if p.is_null() || buffer.is_null(){return -1}
    if len!=SIZE{return -2}
    let bytes=std::slice::from_raw_parts(buffer,SIZE);
    if &bytes[..8]!=MAGIC{return -3}
    let recorded=u64::from_le_bytes(bytes[SIZE-8..SIZE].try_into().unwrap());
    if recorded!=checksum(&bytes[..SIZE-8]){return -4}
    let r=&mut *p;
    if !r.layout_ok() || r.pending{return -5}
    let updates=u64::from_le_bytes(bytes[8..16].try_into().unwrap());
    if updates>100_000_000{return -6}
    // Parse and validate EVERYTHING before mutating any live cell heap.
    let mut values=[[[[0.0f64;C];A];2];N];
    let mut counts=[0u64;N];
    let mut active=[0usize;N];
    let mut ages=[[0u64;2];N];
    let mut switches=[0u64;N];
    let mut pos=[0usize;N];
    let mut fill=[0usize;N];
    let mut bad=[0u64;N];
    let mut windows=[[0u8;WINDOW];N];
    let mut at=16;
    let mut read_u64=|at:&mut usize|->u64 {
        let val=u64::from_le_bytes(bytes[*at..*at+8].try_into().unwrap());
        *at+=8;
        val
    };
    for i in 0..N {
        counts[i]=read_u64(&mut at);
        let bank=read_u64(&mut at);
        ages[i][0]=read_u64(&mut at);
        ages[i][1]=read_u64(&mut at);
        switches[i]=read_u64(&mut at);
        let next_pos=read_u64(&mut at);
        let next_fill=read_u64(&mut at);
        bad[i]=read_u64(&mut at);
        if bank>1 || next_pos>EVIDENCE_WINDOW_EVENTS as u64 || next_fill>PAIRS as u64
            || switches[i]>updates
            || ages[i][0].saturating_add(ages[i][1]) != counts[i]
            || counts[i]>updates {return -7}
        active[i]=bank as usize;
        pos[i]=next_pos as usize;
        fill[i]=next_fill as usize;
        windows[i].copy_from_slice(&bytes[at..at+WINDOW]);
        at+=WINDOW;
        if windows[i][0..PAIRS].iter().any(|x|*x>3)
            || windows[i][PAIRS..WINDOW].iter().any(|x|*x>1)
            || windows[i][PAIRS..WINDOW].iter().map(|x|*x as u64).sum::<u64>() != next_fill
            {return -8}
        for b in 0..2 {for a in 0..A {for c in 0..C {
            let val=f64::from_le_bytes(bytes[at..at+8].try_into().unwrap());
            at+=8;
            if !val.is_finite() || val.abs()>8. {return -9}
            values[i][b][a][c]=val;
        }}}
    }
    if at!=SIZE-8 {return -10}
    for i in 0..N {
        let x=&mut r.cells[i];
        x.weights=values[i];
        x.local_updates=counts[i];
        x.active=active[i];
        x.age=ages[i];
        x.switches=switches[i];
        x.pair_streaks.copy_from_slice(&windows[i][0..PAIRS]);
        x.pair_certified.copy_from_slice(&windows[i][PAIRS..WINDOW]);
        x.evidence_events=pos[i];
        x.confirmed_pairs=fill[i] as u64;
        x.evidence_resets=bad[i];
    }
    r.update_calls=updates;
    r.observed=-1;
    r.pending=false;
    0
}
