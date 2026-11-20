// DWSA-06 engineering-only 84-byte native Hamming prototype checkpoint.
// Independent of any trained donor runtime, learner or environment actions.
import {createHash, timingSafeEqual} from 'node:crypto';

const HEADER = Buffer.from([68, 87, 80, 54, 1, 0, 10, 35]);
const BANKS = 10, BITS_PER_BANK = 35, PAYLOAD_BYTES = 44;
const BODY_BYTES = HEADER.length + PAYLOAD_BYTES;
const TOTAL_BYTES = BODY_BYTES + 32;

function insist(ok, reason) {
  if (!ok) throw new Error('DWSA06_CODEC_REJECT_' + reason);
}

export function encodePrototypes(prototypes) {
  insist(Array.isArray(prototypes) && prototypes.length === BANKS, 'BANK_COUNT');
  const payload = Buffer.alloc(PAYLOAD_BYTES);
  for (let classId = 0; classId < BANKS; classId++) {
    const row = prototypes[classId];
    insist(Array.isArray(row) && row.length === BITS_PER_BANK, 'ROW_LENGTH');
    for (let i = 0; i < BITS_PER_BANK; i++) {
      insist(row[i] === 0 || row[i] === 1, 'NON_BINARY_BIT');
      if (row[i]) {
        const bit = classId * BITS_PER_BANK + i;
        payload[bit >>> 3] |= 1 << (7 - (bit & 7));
      }
    }
  }
  insist((payload[PAYLOAD_BYTES - 1] & 0b11) === 0, 'PADDING');
  const body = Buffer.concat([HEADER, payload]);
  const result = Buffer.concat([body, createHash('sha256').update(body).digest()]);
  insist(result.length === TOTAL_BYTES, 'TOTAL_LENGTH');
  return result;
}

export function decodePrototypes(raw) {
  insist(Buffer.isBuffer(raw) && raw.length === TOTAL_BYTES, 'SIZE');
  insist(raw.subarray(0, HEADER.length).equals(HEADER), 'HEADER');
  insist((raw[BODY_BYTES - 1] & 0b11) === 0, 'PADDING');
  const actual = createHash('sha256').update(raw.subarray(0, BODY_BYTES)).digest();
  insist(timingSafeEqual(actual, raw.subarray(BODY_BYTES)), 'CHECKSUM');
  return Array.from({length: BANKS}, (_, classId) =>
    Array.from({length: BITS_PER_BANK}, (_, bitId) => {
      const bit = classId * BITS_PER_BANK + bitId;
      return (raw[HEADER.length + (bit >>> 3)] >>> (7 - (bit & 7))) & 1;
    }));
}

export function classifyPrototypes(prototypes, input) {
  insist(Array.isArray(prototypes) && prototypes.length === BANKS &&
    Array.isArray(input) && input.length === BITS_PER_BANK &&
    input.every(v => v === 0 || v === 1), 'INPUT');
  let winner = 0, lowest = BITS_PER_BANK + 1;
  for (let classId = 0; classId < BANKS; classId++) {
    const row = prototypes[classId];
    insist(Array.isArray(row) && row.length === BITS_PER_BANK &&
      row.every(v => v === 0 || v === 1), 'MODEL_ROW');
    let errors = 0;
    for (let i = 0; i < BITS_PER_BANK; i++) errors += row[i] !== input[i];
    if (errors < lowest) { winner = classId; lowest = errors; }
  }
  return winner;
}
