import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { modelOpenness } from '../src/data/ocr-openness.ts';
import { criteria, opennessAnchor } from '../src/lib/ocr-openness.ts';

test('model releases retain their individual evidence and distinguish partial from unknown', () => {
  const norhand = modelOpenness['Sprakbanken/TrOCR-norhand-v3'];
  assert.equal(norhand.checks.data.status, 'yes');
  assert.equal(norhand.checks.code.status, 'unknown');
  assert.equal(modelOpenness['Riksarkivet/trocr-base-handwritten-hist-swe-2'].checks.data.status, 'partial');
  assert.equal(modelOpenness['google/gemma-3-4b-it'].checks.license.status, 'no');
  assert.equal(modelOpenness['google/gemma-4-E2B-it'].checks.license.status, 'yes');
  assert.equal(modelOpenness['OpenAI/gpt-6.1-sol'].checks.weights.status, 'no');
  assert.equal(modelOpenness['OpenAI/gpt-6.1-sol'].checks.card.status, 'yes');
});

test('all published models have one complete, sourced and dated evidence record', () => {
  const snapshot = JSON.parse(readFileSync(new URL('../public/results.json', import.meta.url)));
  assert.deepEqual(Object.keys(modelOpenness).sort(), snapshot.models.map(m => m.id).sort());
  for (const [id, value] of Object.entries(modelOpenness)) {
    assert.deepEqual(Object.keys(value).sort(), ['checks', 'reviewed']);
    assert.match(value.reviewed, /^\d{4}-\d{2}-\d{2}$/);
    assert.equal(decodeURIComponent(opennessAnchor(id)), id);
    assert.deepEqual(Object.keys(value.checks).sort(), criteria.map(([key]) => key).sort());
    for (const item of Object.values(value.checks)) {
      assert.ok(['yes', 'no', 'partial', 'unknown'].includes(item.status));
      assert.ok(item.note.length > 10 && item.sources.length > 0);
      item.sources.forEach(source => assert.equal(new URL(source).protocol, 'https:'));
    }
  }
});
