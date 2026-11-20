// DWSA-06 negative source-custody tests; does not require donor files or network.
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtempSync, writeFileSync, rmSync} from 'node:fs';
import {join, dirname} from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';

const script=join(dirname(fileURLToPath(import.meta.url)), 'qualify_source_cli.mjs');
function child(args) {
  return spawnSync(process.execPath, [script, ...args], {
    encoding:'utf8', shell:false, timeout:10000,
    env:Object.fromEntries(['PATH','HOME','SystemRoot','TEMP','TMP','USERPROFILE']
      .filter(key=>typeof process.env[key]==='string')
      .map(key=>[key,process.env[key]])),
  });
}
test('refuses missing upstream input paths before executing a source', () => {
  const r=child([]);
  assert.equal(r.status,1);
  assert.match(r.stderr,/DWSA06_QUALIFY_REJECT_EXPECT_MODEL_SOURCE_TRAIN_PATHS/);
  assert.equal(r.stdout,'');
});
test('refuses a tampered upstream model before executing any source script', () => {
  const dir=mkdtempSync(join(tmpdir(),'dwsa06-negative-'));
  try {
    const paths=['donor.json','models.js','train.mjs'].map(name=>join(dir,name));
    for(const p of paths)writeFileSync(p,'tampered pinned source\n');
    const r=child(paths);
    assert.equal(r.status,1);
    assert.match(r.stderr,/DWSA06_QUALIFY_REJECT_SOURCE_BLOB_0/);
    assert.equal(r.stdout,'');
  } finally { rmSync(dir,{recursive:true,force:true}); }
});
