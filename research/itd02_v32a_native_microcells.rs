//! V32A independent native OWNERSHIP and LOCAL reward-driven plasticity.
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
const MAGIC: &[u8; 8] = b"V32AMIC1";
const SIZE: usize = 8 + 8 + N * (8 + A*C*8) + 8;

struct Cell {
    id: usize,
    left: usize,
    right: usize,
    cue: [f64; C],
    next_cue: [f64; C],
    weights: [[f64; C]; A],
    local_updates: u64,
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
            weights:[[0.; C]; A],local_updates:0,
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
            x.score=(0..C).map(|c|x.cue[c]*x.weights[action][c]).sum();
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
                let credit=RATE*reward*x.credit;
                let mut any=false;
                for c in 0..C {
                    let delta=credit*x.cue[c];
                    if delta!=0. {
                        let value=x.weights[action][c]+delta;
                        x.weights[action][c]=value.max(-8.).min(8.);
                        any=true;
                    }
                }
                if any {x.local_updates+=1;}
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
pub extern "C" fn v32a_new()->*mut Ring {
    Box::into_raw(Box::new(Ring::new()))
}
#[no_mangle]
pub unsafe extern "C" fn v32a_free(p:*mut Ring) {
    if !p.is_null() {drop(Box::from_raw(p));}
}
#[no_mangle]
pub extern "C" fn v32a_schema()->u64 {0x5633324100010001}
#[no_mangle]
pub extern "C" fn v32a_checkpoint_size()->usize {SIZE}
#[no_mangle]
pub unsafe extern "C" fn v32a_observe(p:*mut Ring,cue:i32)->i32 {
    if p.is_null(){return -1}
    if !(0..4).contains(&cue){return -2}
    let r=&mut *p;
    if !r.layout_ok(){return -3}
    r.observe(cue as usize);
    0
}
#[no_mangle]
pub unsafe extern "C" fn v32a_scores(p:*mut Ring,out:*mut f64,len:usize)->i32 {
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
pub unsafe extern "C" fn v32a_feedback(p:*mut Ring,action:i32,reward:f64,learning:i32)->i32 {
    if p.is_null(){return -1}
    if !(0..3).contains(&action) || !reward.is_finite()
        || reward.abs()>1. || !(0..2).contains(&learning) {return -2}
    let r=&mut *p;
    if !r.layout_ok() || !r.pending{return -3}
    r.feedback(action as usize,reward,learning==1);
    0
}
#[no_mangle]
pub unsafe extern "C" fn v32a_cell_address(p:*const Ring, index:i32)->usize {
    if p.is_null() || !(0..8).contains(&index){return 0}
    let r=&*p;if !r.layout_ok(){return 0}
    (&*r.cells[index as usize] as *const Cell) as usize
}
#[no_mangle]
pub unsafe extern "C" fn v32a_neighbor(p:*const Ring,i:i32,side:i32)->i32 {
    if p.is_null() || !(0..8).contains(&i) || !(0..2).contains(&side){return -1}
    let r=&*p;if !r.layout_ok(){return -1}
    if side==0{r.cells[i as usize].left as i32}
    else {r.cells[i as usize].right as i32}
}
#[no_mangle]
pub unsafe extern "C" fn v32a_cell_updates(p:*const Ring,i:i32)->i64 {
    if p.is_null() || !(0..8).contains(&i){return -1}
    let r=&*p;if !r.layout_ok(){return -1}
    r.cells[i as usize].local_updates as i64
}
#[no_mangle]
pub unsafe extern "C" fn v32a_save(p:*const Ring,out:*mut u8,len:usize)->i32{
    if p.is_null() || out.is_null(){return -1}
    if len!=SIZE{return -2}
    let r=&*p;
    if !r.layout_ok() {return -3}
    let mut data=Vec::with_capacity(SIZE);
    data.extend_from_slice(MAGIC);
    data.extend_from_slice(&r.update_calls.to_le_bytes());
    for x in &r.cells{
        data.extend_from_slice(&x.local_updates.to_le_bytes());
        for a in 0..A {for c in 0..C {
            data.extend_from_slice(&x.weights[a][c].to_le_bytes());
        }}
    }
    let hash=checksum(&data);
    data.extend_from_slice(&hash.to_le_bytes());
    if data.len()!=SIZE{return -4}
    std::slice::from_raw_parts_mut(out,SIZE).copy_from_slice(&data);
    0
}
#[no_mangle]
pub unsafe extern "C" fn v32a_load(p:*mut Ring,buffer:*const u8,len:usize)->i32{
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
    let mut values=[[[0.0f64;C];A];N];
    let mut counts=[0u64;N];
    let mut at=16;
    for i in 0..N {
        counts[i]=u64::from_le_bytes(bytes[at..at+8].try_into().unwrap());
        at+=8;
        if counts[i]>updates{return -7}
        for a in 0..A {for c in 0..C {
            let v=f64::from_le_bytes(bytes[at..at+8].try_into().unwrap());
            at+=8;
            if !v.is_finite() || v.abs()>8. {return -8}
            values[i][a][c]=v;
        }}
    }
    if at!=SIZE-8 {return -9}
    for i in 0..N {
        r.cells[i].weights=values[i];
        r.cells[i].local_updates=counts[i];
    }
    r.update_calls=updates;
    r.observed=-1;
    r.pending=false;
    0
}
