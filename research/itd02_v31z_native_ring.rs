//! V31Z: separately compiled, original eight-cell source-only feature owner.
//! Rust 2021 std-only CDylib. All original learning/model code remains Python.
//! Eight separate Box<Cell> allocations; direct original two-neighbor reads,
//! exactly four synchronous rounds; no long-range routing, oracle, or weights.
use std::ffi::c_void;

const CELLS: usize = 8;
const CHANNELS: usize = 7;
const HOPS: usize = 4;
const FEATURES: usize = 20;
const GAIN: f64 = 0.92;
const CUE_SITES: [usize; 4] = [1, 3, 7, 4];
const ACTION_SITES: [usize; 3] = [0, 2, 5];

#[repr(C)]
#[derive(Clone, Copy, Default)]
pub struct Counts {
    pub builds: u64,
    pub hits: u64,
    pub accepted_first_resets: u64,
    pub original_neighbor_directed_frames: u64,
    pub separate_cell_count: u64,
    pub feature_row_width: u64,
}

struct Cell {
    id: usize,
    left: usize,
    right: usize,
    state: [f64; CHANNELS],
    scratch: [f64; CHANNELS],
    row: [f64; FEATURES],
}

impl Cell {
    fn new(id: usize) -> Self {
        Self {
            id,
            left: (id + CELLS - 1) % CELLS,
            right: (id + 1) % CELLS,
            state: [0.0; CHANNELS],
            scratch: [0.0; CHANNELS],
            row: [0.0; FEATURES],
        }
    }
}

pub struct NativeRing {
    cells: Vec<Box<Cell>>,
    cached_cue: i32,
    cached_first: i32,
    cache_valid: bool,
    counts: Counts,
}

impl NativeRing {
    fn new() -> Self {
        let mut cells = Vec::with_capacity(CELLS);
        for i in 0..CELLS {
            cells.push(Box::new(Cell::new(i)));
        }
        Self {
            cells,
            cached_cue: -1,
            cached_first: -1,
            cache_valid: false,
            counts: Counts {
                separate_cell_count: CELLS as u64,
                feature_row_width: FEATURES as u64,
                ..Counts::default()
            },
        }
    }

    fn valid_layout(&self) -> bool {
        if self.cells.len() != CELLS {
            return false;
        }
        for i in 0..CELLS {
            let cell = &self.cells[i];
            if cell.id != i
                || cell.left != (i + CELLS - 1) % CELLS
                || cell.right != (i + 1) % CELLS
                || cell.left == cell.right
                || cell.left == i
                || cell.right == i
            {
                return false;
            }
            for j in 0..i {
                if std::ptr::eq::<Cell>(&*self.cells[j], &**cell) {
                    return false;
                }
            }
        }
        true
    }

    fn reset(&mut self) {
        self.cache_valid = false;
        self.cached_cue = -1;
        self.cached_first = -1;
        for cell in &mut self.cells {
            cell.state = [0.0; CHANNELS];
            cell.scratch = [0.0; CHANNELS];
            cell.row = [0.0; FEATURES];
        }
        self.counts.accepted_first_resets += 1;
    }

    fn compute(&mut self, cue: usize, first: usize) {
        for cell in &mut self.cells {
            cell.state = [0.0; CHANNELS];
            cell.scratch = [0.0; CHANNELS];
        }
        self.cells[CUE_SITES[cue]].state[cue] = 1.0;
        self.cells[ACTION_SITES[first]].state[4 + first] = 1.0;

        // Observe the previous hop's exact own and two original direct
        // neighboring states; only write to the receiving owner's scratch.
        for _hop in 0..HOPS {
            for i in 0..CELLS {
                let left = self.cells[i].left;
                let right = self.cells[i].right;
                for ch in 0..CHANNELS {
                    let old = self.cells[i].state[ch];
                    let lv = self.cells[left].state[ch];
                    let rv = self.cells[right].state[ch];
                    let incoming = if lv >= rv { lv } else { rv };
                    let gained = GAIN * incoming;
                    let top = if old >= gained { old } else { gained };
                    self.cells[i].scratch[ch] = if top >= 2.0 { 2.0 } else { top };
                }
            }
            for cell in &mut self.cells {
                std::mem::swap(&mut cell.state, &mut cell.scratch);
            }
        }

        for cell in &mut self.cells {
            let x = cell.state;
            let mut row = [0.0f64; FEATURES];
            row[0] = 1.0;
            row[1..1 + CHANNELS].copy_from_slice(&x);
            for c in 0..4 {
                for a in 0..3 {
                    row[8 + c * 3 + a] = x[c] * x[4 + a];
                }
            }
            cell.row = row;
        }
        self.counts.builds += 1;
        self.counts.original_neighbor_directed_frames += (CELLS * 2 * HOPS) as u64;
        self.cache_valid = true;
        self.cached_cue = cue as i32;
        self.cached_first = first as i32;
    }
}

#[no_mangle]
pub extern "C" fn v31z_new() -> *mut NativeRing {
    Box::into_raw(Box::new(NativeRing::new()))
}

#[no_mangle]
pub unsafe extern "C" fn v31z_free(ring: *mut NativeRing) {
    if !ring.is_null() {
        drop(Box::from_raw(ring));
    }
}

#[no_mangle]
pub unsafe extern "C" fn v31z_reset(ring: *mut NativeRing) -> i32 {
    if ring.is_null() { return -1; }
    let r = &mut *ring;
    if !r.valid_layout() { return -2; }
    r.reset();
    0
}

/// Fill exactly eight independent 20-float original source-local feature rows.
/// Returns -1 invalid context, -2 invalid ABI length/indices, -3 layout error.
#[no_mangle]
pub unsafe extern "C" fn v31z_rows(
    ring: *mut NativeRing, cue: i32, first: i32,
    result: *mut f64, result_len: usize
) -> i32 {
    if ring.is_null() || result.is_null() { return -1; }
    if !(0..4).contains(&cue) || !(0..3).contains(&first)
        || result_len != CELLS * FEATURES { return -2; }
    let r = &mut *ring;
    if !r.valid_layout() { return -3; }
    if r.cache_valid && r.cached_cue == cue && r.cached_first == first {
        r.counts.hits += 1;
    } else {
        r.compute(cue as usize, first as usize);
    }
    let out = std::slice::from_raw_parts_mut(result, CELLS * FEATURES);
    for cell in 0..CELLS {
        out[cell * FEATURES..(cell + 1) * FEATURES]
            .copy_from_slice(&r.cells[cell].row);
    }
    0
}

#[no_mangle]
pub unsafe extern "C" fn v31z_stats(
    ring: *const NativeRing, out: *mut Counts
) -> i32 {
    if ring.is_null() || out.is_null() { return -1; }
    let r = &*ring;
    if !r.valid_layout() { return -2; }
    *out = r.counts;
    0
}

#[no_mangle]
pub unsafe extern "C" fn v31z_cell_address(
    ring: *const NativeRing, index: i32
) -> usize {
    if ring.is_null() || !(0..8).contains(&index) { return 0; }
    let r = &*ring;
    if !r.valid_layout() { return 0; }
    (&*r.cells[index as usize] as *const Cell) as usize
}

#[no_mangle]
pub unsafe extern "C" fn v31z_neighbor(
    ring: *const NativeRing, index: i32, side: i32
) -> i32 {
    if ring.is_null() || !(0..8).contains(&index) || !(0..2).contains(&side) {
        return -1;
    }
    let r = &*ring;
    if !r.valid_layout() { return -1; }
    let cell = &r.cells[index as usize];
    if side == 0 { cell.left as i32 } else { cell.right as i32 }
}

// Read-only negative probe: only one of the two original directly linked
// neighbors may be admitted, rejects user-forged nonneighbor identity.
#[no_mangle]
pub unsafe extern "C" fn v31z_is_direct_neighbor(
    ring: *const NativeRing, index: i32, other: i32
) -> i32 {
    if ring.is_null() || !(0..8).contains(&index) || !(0..8).contains(&other) {
        return -1;
    }
    let r = &*ring;
    if !r.valid_layout() { return -1; }
    let cell = &r.cells[index as usize];
    if cell.left == other as usize || cell.right == other as usize {
        1
    } else {
        0
    }
}

// Prevent accidental claim of a native learning cell: export only original
// immutable source feature transport, never learned weights, rewards or credit.
#[no_mangle]
pub extern "C" fn v31z_ffi_schema() -> u64 { 0x5633315a_00010001 }
