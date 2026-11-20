// DWSA-06 source-only CLI qualification. No teacher model, actor, or training.
// Supply three exact pinned third-party source files as positional arguments.
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const INPUT_BLOBS = [
  '16ea8cf939bfa0f5f21e227d159b11d4ff578eca',
  '6f95eea88422ceb01b3118e65cd45b9a4c065bd9',
  '1776478a312781e0866f16e1ef237fcbc1092d1a',
];
const CHILDREN = [
  ['run.mjs', 'eee673dd0e8af3089bc5d1b686e4e00627940ead'],
  ['untrained_ablation.mjs', '2da6cecf437a67fc24b72c70de1874f147191840'],
  ['layer_intervention.mjs', '2c5db1d84206122abe53f6fed94caaa2ba1b3b0b'],
];
function need(ok, code) {
  if (!ok) throw Error('DWSA06_QUALIFY_REJECT_' + code);
}
function blobSha(buf) {
  return createHash('sha1')
    .update(Buffer.from('blob ' + buf.length + '\0', 'utf8'))
    .update(buf).digest('hex');
}
function record(condition, error) { need(condition, error); return true; }
function qualify(paths) {
  const started = process.hrtime.bigint();
  record(paths.length === 3, 'EXPECT_MODEL_SOURCE_TRAIN_PATHS');
  const originalBytes = paths.map(path => readFileSync(path));
  originalBytes.forEach((bytes, i) => record(blobSha(bytes) === INPUT_BLOBS[i], 'SOURCE_BLOB_' + i));
  const reports = [];
  for (const [script, pinnedSha] of CHILDREN) {
    const fullPath = join(HERE, script);
    record(blobSha(readFileSync(fullPath)) === pinnedSha, 'CODE_DRIFT_' + script);
    const result = spawnSync(process.execPath, [fullPath, ...paths], {
      cwd: HERE, encoding: 'utf8', shell: false, timeout: 60000, maxBuffer: 2 * 1024 * 1024,
      env: Object.fromEntries(['PATH','HOME','SystemRoot','TEMP','TMP','USERPROFILE']
        .filter(key => typeof process.env[key] === 'string')
        .map(key => [key, process.env[key]])),
    });
    record(result.error === undefined && result.status === 0 && result.signal === null,
      'CHILD_FAILURE_' + script + '_EXIT_' + result.status);
    let parsed;
    try { parsed = JSON.parse(result.stdout); }
    catch { throw Error('DWSA06_QUALIFY_REJECT_NON_JSON_' + script); }
    reports.push(parsed);
  }
  const [original, untrained, layer] = reports;
  record(original.schema === 'dwsa06.static-path-prototype-dev.v1', 'ORIGINAL_SCHEMA');
  record(original.checkpoint_sha256 === 'a32ff3ae95dbe040b87b9763a1586fdb4a2e459b5375de99fe9c7a8a8e444135', 'CHECKPOINT_SHA');
  record(original.candidate_bytes === 84 && original.tests.cold_restores === 3 && original.tests.tamper_rejections === 5, 'CHECKPOINT_CONTROLS');
  record(original.metrics.learned_path.correct === 1615 && original.metrics.supervised_same_bytes.correct === 1985, 'ORIGINAL_SCORES');
  record(untrained.schema === 'dwsa06.learning-specific-weight-path-dev.v1', 'UNTRAINED_SCHEMA');
  record(untrained.trained.correct === 1615 && untrained.untrained.length === 16, 'UNTRAINED_COUNT');
  record(untrained.untrained[0].seed === 20261022 && untrained.untrained[0].correct === 230, 'ORIGINAL_INIT_PARITY');
  record(untrained.untrained_accuracy.maximum === 0.2135 && untrained.frozen_dev_decision === 'LEARNING_SPECIFIC_DEV_SIGNAL', 'UNTRAINED_RESULT');
  record(layer.schema === 'dwsa06.frozen-layer-intervention-dev.v1', 'LAYER_SCHEMA');
  record(layer.measurements.length === 16 && layer.measurements[0].correct === 230 && layer.measurements[15].correct === 1615, 'LAYER_PARITY');
  record(layer.best_mixed_mask === 11 && layer.best_mixed_accuracy === 0.6665 && layer.criterion === 'INTERLAYER_DEPENDENCE_DEV_SIGNAL', 'LAYER_RESULT');
  record(layer.checkpoint_bytes === 84 && layer.cold_restores_per_mask === 3 && layer.tamper_rejections === 4, 'LAYER_CODEC');
  record(layer.checkpoint_sha256[15] === original.checkpoint_sha256, 'CROSS_SCRIPT_CHECKPOINT_PARITY');
  record(original.donor_forward_calls === 0 && untrained.donor_forward_calls === 0 && layer.donors_executed === 0, 'ZERO_DONOR_INFERENCE');
  record(original.original_source_actions === 0 && untrained.new_source_actions === 0 && layer.source_world_actions === 0, 'ZERO_SOURCE_ACTIONS');
  const time_ms = Number(process.hrtime.bigint() - started) / 1e6;
  return {
    schema: 'dwsa06.node-source-cli-qualification.v1',
    result: 'FULL_PINNED_NODE_SOURCE_CLI_DEV_PASS',
    original_input_blobs: INPUT_BLOBS,
    original_script_blobs: CHILDREN.map(([name, sha]) => ({name, sha})),
    original_checkpoint_sha256: original.checkpoint_sha256,
    learned_correct: original.metrics.learned_path.correct,
    matched_control_correct: original.metrics.supervised_same_bytes.correct,
    original_untrained_correct: untrained.untrained[0].correct,
    best_untrained_accuracy: untrained.untrained_accuracy.maximum,
    best_mixed_accuracy: layer.best_mixed_accuracy,
    masks: layer.measurements.length,
    donor_forward_calls: 0,
    original_world_actions: 0,
    scientific: 'UNVERIFIED', deployment: 'NONE',
    duration_ms_diagnostic: time_ms,
  };
}
try { console.log(JSON.stringify(qualify(process.argv.slice(2)), null, 2)); }
catch (e) { console.error(String(e)); process.exitCode = 1; }
