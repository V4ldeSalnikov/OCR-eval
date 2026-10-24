import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { paretoPoints } from '../src/lib/ocr-pareto.ts';
import { modelParameters } from '../src/data/ocr-parameters.ts';
import { rankModels } from '../src/lib/ocr-results.ts';
import { benchmarks } from '../src/data/ocr-benchmarks.ts';

const samples = ['one', 'two'].map(id => ({ id, task: 'line-recognition', dataset_id: id, selected_samples: 10 }));
const model = id => ({ id, name: id, family: '', reference: '', supported_tasks: ['line-recognition'] });
const result = (id, sample, error) => ({ model_id: id, sample_set_id: sample, status: 'completed', corpus_metrics: { cer: error, wer: error } });
const counts = sizes => Object.fromEntries(Object.entries(sizes).map(([id, active]) => [id, { active, total: active * 2, revision: 'test' }]));

test('frontier keeps trade-offs and exact ties but removes equal-size or equal-error dominated points', () => {
  const errors = { A: .3, B: .2, C: .3, D: .4, E: .2, F: .1 };
  const data = { models: Object.keys(errors).map(model), results: Object.entries(errors).map(([id, e]) => result(id, 'one', e)) };
  const points = paretoPoints(data, [samples[0]], 'cer', counts({ A: 1, B: 2, C: 3, D: 2, E: 2, F: 4 }));
  assert.deepEqual(points.filter(p => p.frontier).map(p => p.model.id), ['A', 'B', 'E', 'F']);
});

test('unknown sizes and incomplete runs never become zero-sized or partially averaged points', () => {
  const data = { models: ['complete', 'partial', 'unknown', 'zero', 'nan'].map(model), results: [
    result('complete', 'one', 0), result('complete', 'two', .2), result('partial', 'one', 0),
    ...['unknown', 'zero', 'nan'].flatMap(id => samples.map(s => result(id, s.id, 0))),
  ] };
  const sizes = counts({ complete: 10, partial: 1, zero: 0, nan: NaN });
  const overall = paretoPoints(data, samples, 'wer', sizes);
  assert.deepEqual(overall.map(p => [p.model.id, p.error, p.frontier]), [['complete', .1, true]]);
  const single = paretoPoints(data, [samples[0]], 'wer', sizes);
  assert.equal(single.find(p => p.model.id === 'partial').frontier, true);
  assert.equal(single.find(p => p.model.id === 'complete').frontier, false);
  assert.deepEqual(paretoPoints(data, [], 'wer', sizes), []);
});

test('published plot values match existing mean and per-task scores for every benchmark and metric', () => {
  const data = JSON.parse(readFileSync(new URL('../public/results.json', import.meta.url)));
  for (const benchmark of benchmarks) {
    const selected = data.sample_sets.filter(s => benchmark.sampleIds.includes(s.id));
    for (const metric of ['cer', 'wer']) for (const tasks of [selected, ...selected.map(s => [s])]) {
      const expected = rankModels(data, tasks, null, metric).filter(r => modelParameters[r.model.id]);
      const points = paretoPoints(data, tasks, metric, modelParameters);
      assert.equal(points.length, expected.length);
      for (const point of points) assert.equal(point.error, expected.find(r => r.model.id === point.model.id).metrics[metric]);
    }
  }
  for (const [id, count] of Object.entries(modelParameters)) {
    assert.ok(data.models.some(m => m.id === id));
    assert.ok(Number.isSafeInteger(count.active) && count.active > 0 && count.active <= count.total);
    assert.match(count.revision, /^[a-f0-9]{40}$/);
    assert.deepEqual([...new Set(data.results.filter(r => r.model_id === id).map(r => r.model_revision))], [count.revision]);
  }
});
