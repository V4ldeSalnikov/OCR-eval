import { type Metric, type SampleSet, type Snapshot } from '../lib/ocr-results';
import { matrixRows, type Aggregation, type MatrixRow } from '../lib/ocr-matrix';
import { datasetDescriptions, languageNames } from '../data/ocr-datasets';
import { benchmarks, inputDescription } from '../data/ocr-benchmarks';
import { modelOpenness } from '../data/ocr-openness';
import { criteria, opennessIcon, statusLabels, opennessAnchor, type Evidence } from '../lib/ocr-openness';
import { modelParameters } from '../data/ocr-parameters';
import { paretoPoints } from '../lib/ocr-pareto';
import { renderPareto } from './ocr-pareto';

const element = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const search = element<HTMLInputElement>('model-search');
const benchmarkSelect = element<HTMLSelectElement>('benchmark-select');
const aggregationSelect = element<HTMLSelectElement>('aggregation-select');
const metricButtons = [...document.querySelectorAll<HTMLButtonElement>('[data-metric]')];
const viewButtons = [...document.querySelectorAll<HTMLButtonElement>('[data-view]')];
const sizeTaskSelect = element<HTMLSelectElement>('size-task');
let view: 'table' | 'size' = 'table', sizeTask = 'overall';
let data: Snapshot, benchmark = benchmarks[0], metric: Metric = 'wer', aggregation: Aggregation = 'mean';
let sortKey = 'overall', descending = false;
const number = (value: number) => value.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const percent = (value: number) => `${number(value * 100)}%`;
const text = (id: string, value: string) => { element(id).textContent = value; };
const explanations: Record<Aggregation, string> = {
  mean: 'Mean averages the selected error rate across tasks, giving every task equal weight. Lower is better.',
  borda: 'Borda rank averages a model’s position on each task. Ties share the average position. Lower is better.',
  'win-rate': 'Win rate estimates how often a model beats another model, using Bradley–Terry comparisons of task scores. Ties count as half a win. Higher is better.',
};
function node<K extends keyof HTMLElementTagNameMap>(tag: K, value = '', className = '') {
  const item = document.createElement(tag); item.textContent = value; item.className = className; return item;
}
const opennessTooltip = node('div', '', 'openness-tooltip');
opennessTooltip.id = 'openness-tooltip'; opennessTooltip.role = 'tooltip'; opennessTooltip.hidden = true;
document.body.append(opennessTooltip);
let opennessTrigger: HTMLAnchorElement | null = null;
function hideOpenness() {
  opennessTooltip.hidden = true; opennessTrigger?.removeAttribute('aria-describedby'); opennessTrigger = null;
}
function showOpenness(trigger: HTMLAnchorElement, label: string, evidence: Evidence) {
  hideOpenness();
  opennessTrigger = trigger;
  trigger.setAttribute('aria-describedby', opennessTooltip.id);
  const heading = node('div', '', 'openness-tooltip-heading');
  heading.append(node('strong', label), node('span', statusLabels[evidence.status], evidence.status));
  opennessTooltip.replaceChildren(heading, node('p', evidence.note));
  opennessTooltip.hidden = false;
  const rect = trigger.getBoundingClientRect(), width = opennessTooltip.offsetWidth, height = opennessTooltip.offsetHeight;
  opennessTooltip.style.left = `${Math.max(8, Math.min(rect.left, innerWidth - width - 8))}px`;
  opennessTooltip.style.top = `${Math.max(8, rect.bottom + height < innerHeight - 8 ? rect.bottom - 1 : rect.top - height + 1)}px`;
}
opennessTooltip.addEventListener('mouseleave', event => {
  if (!(event.relatedTarget instanceof Node && opennessTrigger?.contains(event.relatedTarget))) hideOpenness();
});
window.addEventListener('scroll', hideOpenness, true);
window.addEventListener('resize', hideOpenness);
document.addEventListener('keydown', event => { if (event.key === 'Escape') hideOpenness(); });
function overallLabel() { return aggregation === 'mean' ? `Mean ${metric.toUpperCase()}` : aggregation === 'borda' ? 'Borda rank' : 'Win rate'; }
function saveSelection(push = false) {
  const params = new URLSearchParams({ benchmark: benchmark.id, metric, aggregation });
  if (view === 'size') params.set('view', 'size');
  if (sizeTask !== 'overall') params.set('size_task', sizeTask);
  if (sortKey !== 'overall') params.set('sort', sortKey);
  if (descending !== (sortKey === 'overall' && aggregation === 'win-rate')) params.set('direction', descending ? 'desc' : 'asc');
  if (search.value.trim()) params.set('q', search.value.trim());
  history[push ? 'pushState' : 'replaceState'](null, '', `${location.pathname}?${params}${location.hash}`);
}
function heading(key: string, label: string, subtitle: string, className: string, description = '') {
  const cell = node('th', '', className); cell.scope = 'col';
  const button = node('button'); button.type = 'button'; button.dataset.sort = key;
  button.append(node('span', label));
  const active = key === sortKey;
  button.append(node('span', active ? (descending ? '↓' : '↑') : '↕', 'sort-arrow'));
  if (subtitle) button.append(node('small', subtitle));
  button.title = description || `Sort by ${label}`;
  button.setAttribute('aria-label', description || `Sort by ${label}, ${subtitle}`);
  if (active) cell.setAttribute('aria-sort', descending ? 'descending' : 'ascending');
  button.addEventListener('click', () => {
    descending = active ? !descending : key === 'overall' && aggregation === 'win-rate';
    sortKey = key; render(); saveSelection(true);
  });
  cell.append(button); return cell;
}
const datasetLanguage = (id: string) => data.datasets.find(dataset => dataset.id === id)!.language_codes[0];
function renderRow(row: MatrixRow, samples: SampleSet[], columns: Record<string, number[]>, groupEnds: Set<string>, languageEnds: Set<string>) {
  const tr = node('tr'); tr.dataset.model = row.model.id;
  const model = node('td', '', 'model-cell');
  const [publisher, ...parts] = row.model.name.split('/');
  const link = node('a', parts.length ? parts.join('/') : publisher, 'model-name');
  link.href = row.model.reference; link.title = row.model.id; model.append(link);
  if (parts.length) model.append(node('span', publisher, 'model-publisher'));
  const overall = node('td', row.aggregate === null ? '—' : aggregation === 'borda' ? number(row.aggregate) : percent(row.aggregate), 'overall-cell');
  if (row.aggregate === null) overall.title = aggregation === 'win-rate' && samples.every(sample => row.scores[sample.id] !== null)
    ? 'Win rate needs at least two fully evaluated models.' : 'An overall score requires a completed evaluation on every task in this benchmark.';
  tr.append(model, overall);
  const openness = node('td', '', 'openness-cell');
  const profile = modelOpenness[row.model.id];
  if (profile) {
    const icons = node('div', '', 'openness-icons');
    for (const [key, label] of criteria) {
      const evidence = profile.checks[key];
      const details = node('a', '', `openness-icon ${evidence.status}`);
      details.href = `/OCR-eval/openness/#${opennessAnchor(row.model.id, key)}`;
      details.dataset.criterion = key;
      details.innerHTML = opennessIcon(key);
      details.setAttribute('aria-label', `${row.model.name}: ${label} — ${statusLabels[evidence.status]}. View evidence.`);
      const reveal = () => requestAnimationFrame(() => {
        if (details.matches(':hover, :focus')) showOpenness(details, label, evidence);
      });
      details.addEventListener('mouseenter', reveal);
      details.addEventListener('focus', reveal);
      details.addEventListener('blur', hideOpenness);
      details.addEventListener('mouseleave', event => {
        if (!(event.relatedTarget instanceof Node && opennessTooltip.contains(event.relatedTarget))) hideOpenness();
      });
      icons.append(details);
    }
    openness.append(icons);
  } else { openness.textContent = 'Unknown'; }
  tr.append(openness);
  for (const sample of samples) {
    const value = row.scores[sample.id];
    const cell = node('td', '', sortKey === sample.id ? 'selected-task' : ''); cell.dataset.sample = sample.id;
    if (groupEnds.has(sample.id)) cell.classList.add('dataset-end');
    if (languageEnds.has(sample.id)) cell.classList.add('language-end');
    cell.setAttribute('headers', `language-${datasetLanguage(sample.dataset_id)} dataset-${sample.dataset_id} task-${sample.id}`);
    if (value === null) { cell.textContent = '—'; cell.classList.add('missing-score'); cell.title = 'No completed score for this task.'; }
    else {
      const scores = columns[sample.id];
      const position = scores.filter(score => score < value).length / Math.max(1, scores.length - 1);
      cell.style.backgroundColor = `rgba(190, 37, 56, ${position * .16})`;
      if (value === Math.min(...scores)) cell.classList.add('best-score');
      const params = new URLSearchParams({ model: row.model.id, view: 'examples', metric, task: sample.task, dataset: sample.dataset_id });
      const score = node('a', percent(value)); score.href = `/OCR-eval/compare/?${params}`;
      score.title = `View ${metric.toUpperCase()} ${percent(value)} examples: ${datasetDescriptions[sample.dataset_id].name}`;
      cell.append(score);
    }
    tr.append(cell);
  }
  return tr;
}
function render() {
  hideOpenness();
  const benchmarkSamples = benchmark.sampleIds.map(id => data.sample_sets.find(sample => sample.id === id)!).filter(Boolean);
  const groups = new Map<string, SampleSet[]>();
  for (const sample of benchmarkSamples) {
    if (!groups.has(sample.dataset_id)) groups.set(sample.dataset_id, []);
    groups.get(sample.dataset_id)!.push(sample);
  }
  const languageGroups = new Map<string, [string, SampleSet[]][]>();
  for (const [datasetId, tasks] of groups) {
    const language = datasetLanguage(datasetId);
    if (!languageGroups.has(language)) languageGroups.set(language, []);
    languageGroups.get(language)!.push([datasetId, tasks]);
  }
  const orderedGroups = [...languageGroups.values()].flat();
  const samples = orderedGroups.flatMap(([, tasks]) => tasks);
  const languageEnds = new Set([...languageGroups.values()].map(datasets => datasets.at(-1)![1].at(-1)!.id));
  if (!benchmark.sampleIds.includes(sizeTask)) sizeTask = 'overall';
  sizeTaskSelect.replaceChildren(new Option('Overall · mean across tasks', 'overall'), ...samples.map(sample =>
    new Option(`${datasetDescriptions[sample.dataset_id].name} · ${sample.task === 'line-recognition' ? 'Cropped lines' : 'Full pages'}`, sample.id)));
  sizeTaskSelect.value = sizeTask;
  const showSize = view === 'size';
  element('table-view').hidden = showSize; element('size-view').hidden = !showSize;
  element('aggregation-control').hidden = showSize; element('size-task-control').hidden = !showSize;
  viewButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === view)));
  const groupEnds = new Set([...groups.values()].map(group => group[group.length - 1].id));
  const rows = matrixRows(data, benchmarkSamples, metric, aggregation);
  const columns = Object.fromEntries(samples.map(sample => [sample.id, rows.map(row => row.scores[sample.id]).filter((value): value is number => value !== null)]));
  const value = (row: MatrixRow) => sortKey === 'overall' ? row.aggregate : row.scores[sortKey];
  rows.sort((a, b) => {
    const x = value(a), y = value(b);
    if (x == null || y == null) return x == y ? a.model.name.localeCompare(b.model.name) : x == null ? 1 : -1;
    return (descending ? y - x : x - y) || a.model.name.localeCompare(b.model.name);
  });
  const query = search.value.trim().toLowerCase();
  const visible = rows.filter(row => `${row.model.name} ${row.model.id} ${row.model.family}`.toLowerCase().includes(query));
  const head = node('tr'), datasetHead = node('tr'), taskHead = node('tr', '', 'task-headings');
  const model = node('th', 'Model', 'model-cell'); model.scope = 'col'; model.rowSpan = 3;
  const overall = heading('overall', overallLabel(), aggregation === 'win-rate' ? 'Higher is better' : 'Lower is better', 'overall-cell');
  overall.rowSpan = 3; head.append(model, overall);
  const openness = node('th', '', 'openness-cell'); openness.scope = 'col'; openness.rowSpan = 3;
  const opennessLink = node('a', 'Openness', 'openness-heading'); opennessLink.href = '/OCR-eval/openness/';
  opennessLink.title = 'Weights, license, training code, training data, paper and documentation. Highlighted icons indicate confirmed availability. Hover or select an icon for details.';
  openness.append(opennessLink);
  head.append(openness);
  for (const [language, datasets] of languageGroups) {
    const cell = node('th', languageNames[language] ?? language, 'language-group language-end');
    cell.id = `language-${language}`; cell.colSpan = datasets.reduce((sum, [, tasks]) => sum + tasks.length, 0);
    head.append(cell);
  }
  const columnGroups = [];
  for (const [datasetId, tasks] of orderedGroups) {
    const { name, shortName } = datasetDescriptions[datasetId];
    const languageId = `language-${datasetLanguage(datasetId)}`;
    const group = node('th', '', `dataset-group dataset-end${languageEnds.has(tasks.at(-1)!.id) ? ' language-end' : ''}`);
    group.id = `dataset-${datasetId}`; group.scope = 'colgroup'; group.colSpan = tasks.length;
    group.setAttribute('headers', languageId);
    const link = node('a', shortName, 'dataset-heading'); link.href = `/OCR-eval/datasets/#${datasetId}`;
    link.title = `Read about ${name}`; group.append(link); datasetHead.append(group);
    const columns = node('colgroup'); columns.span = tasks.length; columns.dataset.dataset = datasetId; columnGroups.push(columns);
    for (const sample of tasks) {
      const label = sample.task === 'line-recognition' ? 'Line' : 'Page';
      const cell = heading(sample.id, label, '', `task-header${groupEnds.has(sample.id) ? ' dataset-end' : ''}${languageEnds.has(sample.id) ? ' language-end' : ''}`,
        `Sort by ${metric.toUpperCase()}: ${name}, ${label}. ${inputDescription(sample.task)}`);
      cell.querySelector('button>span')!.classList.add('input-tag');
      cell.id = `task-${sample.id}`; cell.setAttribute('headers', `${languageId} ${group.id}`); taskHead.append(cell);
    }
  }
  const table = document.querySelector<HTMLTableElement>('.task-matrix')!;
  table.querySelectorAll('colgroup[data-dataset]').forEach(group => group.remove());
  element('matrix-columns').replaceChildren(node('col', '', 'model-column'), node('col', '', 'overall-column'), node('col', '', 'openness-column'));
  element('matrix-columns').after(...columnGroups);
  element('results-head').replaceChildren(head, datasetHead, taskHead);
  element('results-body').replaceChildren(...visible.map(row => renderRow(row, samples, columns, groupEnds, languageEnds)));
  table.style.minWidth = `calc(var(--model-width) + var(--overall-width) + var(--openness-width) + ${96 * samples.length}px)`;
  text('table-caption', `${benchmark.name}: ${overallLabel()} and ${metric.toUpperCase()} for each task, grouped by language and dataset. Cropped lines and full pages are separate tasks. Task error rates are percentages; lower is better.`);
  text('selection-description', `${groups.size} datasets · ${samples.length} tasks · ${metric.toUpperCase()} (%)`);
  text('metric-help', `${metric === 'wer' ? 'WER counts word' : 'CER counts character'} substitutions, deletions and insertions relative to the reference text. Lower is better; scores can exceed 100%.`);
  text('aggregation-help', showSize ? sizeTask === 'overall' ? explanations.mean : 'The plot shows the selected task’s corpus error rate.' : explanations[aggregation]);
  text('view-help', showSize
    ? 'A frontier model has no competitor with both fewer or equal active parameters and lower or equal error, with at least one strict improvement. Overall scores require results on every task. Parameter counts are estimates, not speed or memory measurements.'
    : 'Task cells always show error rates. Overall scores require results on every task. Shading compares models within each task; darker red means higher error.');
  text('visible-models', `${visible.length} model${visible.length === 1 ? '' : 's'}`);
  element<HTMLAnchorElement>('benchmark-about').href = `/OCR-eval/benchmarks/${benchmark.id}/`;
  benchmarkSelect.value = benchmark.id; aggregationSelect.value = aggregation;
  metricButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.metric === metric)));
  element('table-status').hidden = visible.length > 0;
  text('table-status', 'No models match your search.');
  if (showSize) {
    const plotSamples = sizeTask === 'overall' ? samples : samples.filter(sample => sample.id === sizeTask);
    const allPoints = paretoPoints(data, plotSamples, metric, modelParameters);
    // Search hides points but never promotes a dominated model onto the frontier.
    const plotted = allPoints.filter(point => `${point.model.name} ${point.model.id} ${point.model.family}`.toLowerCase().includes(query));
    renderPareto(plotted, metric, sizeTask === 'overall');
    if (sizeTask !== 'overall') text('selection-description', `1 dataset · ${plotSamples[0].task === 'line-recognition' ? 'Cropped lines' : 'Full pages'} · ${metric.toUpperCase()} (%)`);
    text('size-count', `${plotted.length} models · ${sizeTask === 'overall' ? `Mean ${metric.toUpperCase()}` : metric.toUpperCase()} · Parameter estimates`);
    const unknown = data.models.filter(model => !modelParameters[model.id] && plotSamples.every(sample => model.supported_tasks.includes(sample.task)));
    element('size-omissions').hidden = !unknown.length;
    text('size-unknown', unknown.map(model => model.name).join(' · '));
  }
}
function restoreSelection() {
  const params = new URLSearchParams(location.search);
  const legacyLanguage = params.get('language') ?? data.datasets.find(dataset => dataset.id === params.get('dataset'))?.language_codes[0];
  benchmark = benchmarks.find(item => item.id === params.get('benchmark'))
    ?? benchmarks.find(item => item.languages.length === 1 && item.languages[0] === legacyLanguage) ?? benchmarks[0];
  metric = params.get('metric') === 'cer' ? 'cer' : 'wer';
  aggregation = ['borda', 'win-rate'].includes(params.get('aggregation') ?? '') ? params.get('aggregation') as Aggregation : 'mean';
  view = params.get('view') === 'size' ? 'size' : 'table';
  sizeTask = params.get('size_task') ?? 'overall';
  const requested = params.get('sort') ?? params.get('sample') ?? `${params.get('task') ?? 'line-recognition'}/${params.get('dataset') ?? ''}`;
  sortKey = benchmark.sampleIds.includes(requested) ? requested : 'overall';
  descending = params.has('direction') ? params.get('direction') === 'desc' : sortKey === 'overall' && aggregation === 'win-rate';
  search.value = params.get('q') ?? '';
  render(); saveSelection();
}
async function start() {
  const response = await fetch('/OCR-eval/results.json');
  if (!response.ok) throw new Error('Results could not be loaded.');
  data = await response.json(); restoreSelection();
  benchmarkSelect.addEventListener('change', () => { benchmark = benchmarks.find(item => item.id === benchmarkSelect.value)!; sortKey = 'overall'; descending = aggregation === 'win-rate'; render(); saveSelection(true); });
  aggregationSelect.addEventListener('change', () => { aggregation = aggregationSelect.value as Aggregation; sortKey = 'overall'; descending = aggregation === 'win-rate'; render(); saveSelection(true); });
  metricButtons.forEach(button => button.addEventListener('click', () => { metric = button.dataset.metric as Metric; render(); saveSelection(true); }));
  viewButtons.forEach(button => button.addEventListener('click', () => { view = button.dataset.view as typeof view; render(); saveSelection(true); }));
  sizeTaskSelect.addEventListener('change', () => { sizeTask = sizeTaskSelect.value; render(); saveSelection(true); });
  search.addEventListener('input', () => { render(); saveSelection(); });
  const help = document.querySelector<HTMLElement>('.score-help')!;
  help.addEventListener('keydown', event => {
    if (event.key === 'Escape') { help.querySelector<HTMLButtonElement>('button')!.focus(); help.classList.add('dismissed'); }
  });
  help.addEventListener('mouseenter', () => help.classList.remove('dismissed'));
  help.addEventListener('click', () => help.classList.remove('dismissed'));
  help.addEventListener('focusin', () => help.classList.remove('dismissed'));
  window.addEventListener('popstate', restoreSelection);
}
start().catch(() => {
  element('load-error').hidden = false;
  text('load-error', 'The results could not be loaded. Please reload the page or download the results below.');
  element('table-status').hidden = true;
});
