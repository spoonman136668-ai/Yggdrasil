// DWSA-06 engineering-only deterministic native codec qualification.
import assert from 'node:assert/strict';
import test from 'node:test';
import {createHash} from 'node:crypto';
import {encodePrototypes, decodePrototypes, classifyPrototypes} from './codec.mjs';

const bank = Array.from({length: 10}, (_, c) =>
  Array.from({length: 35}, (_, i) => Number((c * 17 + i * 11) % 7 < 3)));

function resign(bytes) {
  const raw = Buffer.from(bytes);
  createHash('sha256').update(raw.subarray(0, 52)).digest().copy(raw, 52);
  return raw;
}

test('84-byte deterministic output, 350 exact bits and zero padding', () => {
  const raw = encodePrototypes(bank);
  assert.equal(raw.length, 84);
  assert.equal(raw[51] & 3, 0);
  assert.deepEqual(decodePrototypes(raw), bank);
  assert.deepEqual(encodePrototypes(bank), raw);
});

test('three immutable cold restores', () => {
  const raw = encodePrototypes(bank);
  for (let i = 0; i < 3; i++)
    assert.deepEqual(decodePrototypes(Buffer.from(raw)), bank);
});

test('damaged payload, header, digest and length reject', () => {
  const raw = encodePrototypes(bank);
  for (const i of [0, 4, 8, 36, 51, 52, 83]) {
    const bad = Buffer.from(raw); bad[i] ^= 1;
    assert.throws(() => decodePrototypes(bad), /DWSA06_CODEC_REJECT_/);
  }
  assert.throws(() => decodePrototypes(raw.subarray(0, 83)), /_SIZE/);
});

test('nonzero reserved padding rejects even with valid checksum', () => {
  const altered = Buffer.from(encodePrototypes(bank)); altered[51] |= 1;
  assert.throws(() => decodePrototypes(resign(altered)), /_PADDING/);
});

test('invalid inputs reject rather than silently normalize', () => {
  assert.throws(() => encodePrototypes(bank.slice(0, 9)), /_BANK_COUNT/);
  assert.throws(() => encodePrototypes([...bank.slice(0, 9), []]), /_ROW_LENGTH/);
  const modified = bank.map(row => [...row]); modified[0][3] = 2;
  assert.throws(() => encodePrototypes(modified), /_NON_BINARY_BIT/);
  assert.throws(() => decodePrototypes(Uint8Array.from(encodePrototypes(bank))), /_SIZE/);
});

test('Hamming classification and lowest-index tie rule', () => {
  const restored = decodePrototypes(encodePrototypes(bank));
  for (let c = 0; c < 10; c++) {
    const winner = classifyPrototypes(restored, bank[c]);
    assert.ok(winner <= c); // duplicate prototypes may tie to a lower label
  }
  const tie = Array.from({length: 10}, () => Array(35).fill(0));
  assert.equal(classifyPrototypes(tie, Array(35).fill(1)), 0);
  assert.throws(() => classifyPrototypes(bank, Array(34).fill(0)), /_INPUT/);
});

