import { formatParameters, type ParetoPoint } from '../lib/ocr-pareto';
import type { Metric } from '../lib/ocr-results';

const chart = document.getElementById('size-chart')!;
const detail = document.getElementById('size-detail')!;
let points: ParetoPoint[] = [], metric: Metric = 'wer', overall = true, selected: string | null = null;
const metricLabel = () => `${overall ? 'Mean ' : ''}${metric.toUpperCase()}`;
const percent = (value: number) => `${(value * 100).toFixed(2)}%`;
function svg<K extends keyof SVGElementTagNameMap>(tag: K, attributes: Record<string, string | number>, text = '') {
  const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [name, value] of Object.entries(attributes)) element.setAttribute(name, String(value));
  if (text) element.textContent = text;
  return element;
}
function html(tag: string, text: string, className = '') {
  const element = document.createElement(tag); element.textContent = text; element.className = className; return element;
}
function select(point: ParetoPoint) {
  selected = point.model.id;
  chart.querySelectorAll('[data-model]').forEach(el => {
    const active = (el as SVGElement).dataset.model === selected;
    el.classList.toggle('selected', active); el.setAttribute('aria-pressed', String(active));
  });
  const name = html('a', point.model.name.split('/').at(-1)!, 'size-model-name') as HTMLAnchorElement;
  name.href = point.model.reference;
  const stats = html('dl', '');
  for (const [label, value] of [
    [metricLabel(), percent(point.error)], ['Active parameters', formatParameters(point.parameters.active)],
    ['Total parameters', formatParameters(point.parameters.total)],
  ]) { const row = html('div', ''); row.append(html('dt', label), html('dd', value)); stats.append(row); }
  const source = html('a', 'Parameter source ↗') as HTMLAnchorElement;
  source.href = `https://huggingface.co/${point.model.id}/blob/${point.parameters.revision}/config.json`;
  source.target = '_blank'; source.rel = 'noreferrer';
  const method = html('a', 'How parameters are counted →') as HTMLAnchorElement;
  method.href = '/OCR-eval/methodology/#model-size';
  detail.replaceChildren(html('span', point.frontier ? 'Pareto frontier' : 'Model details', 'size-detail-label'), name,
    html('p', point.model.name.split('/')[0], 'size-publisher'), stats, source, method);
}
function draw() {
  if (chart.closest<HTMLElement>('[hidden]')) return;
  chart.replaceChildren();
  if (!points.length) {
    chart.append(html('p', 'No models with a verified parameter estimate and a complete score match this selection.', 'message'));
    detail.replaceChildren(); selected = null; return;
  }
  const width = Math.max(280, chart.clientWidth), height = 400;
  const left = 62, right = width - 24, top = 32, bottom = height - 62;
  const values = points.map(p => Math.log10(p.parameters.active));
  const min = Math.min(...values), max = Math.max(...values), padding = Math.max(.08, (max - min) * .06);
  const low = min - padding, high = max + padding;
  const x = (value: number) => left + (Math.log10(value) - low) / (high - low) * (right - left);
  const maxError = Math.max(.01, ...points.map(p => p.error));
  const stepPower = 10 ** Math.floor(Math.log10(maxError * 100 / 4));
  const step = [1, 2, 5, 10].find(n => n * stepPower >= maxError * 100 / 4)! * stepPower / 100;
  const ceiling = Math.ceil(maxError / step) * step;
  const y = (value: number) => bottom - value / ceiling * (bottom - top);
  const plot = svg('svg', { viewBox: `0 0 ${width} ${height}`, role: 'group', 'aria-label': `${metricLabel()} versus estimated active parameters. Lower and further left is better.` });
  const axes = svg('g', { class: 'size-axes', 'aria-hidden': 'true' });
  for (let value = 0; value <= ceiling + step / 2; value += step) {
    axes.append(svg('line', { x1: left, y1: y(value), x2: right, y2: y(value) }));
    axes.append(svg('text', { x: left - 12, y: y(value) + 4, 'text-anchor': 'end' }, `${+(value * 100).toFixed(2)}%`));
  }
  let previous = -Infinity;
  for (let power = Math.floor(low); power <= Math.ceil(high); power++) for (const factor of [1, 2, 5]) {
    const value = factor * 10 ** power, position = x(value);
    if (position < left || position > right || position - previous < 50) continue;
    axes.append(svg('line', { x1: position, y1: top, x2: position, y2: bottom }));
    axes.append(svg('text', { x: position, y: bottom + 24, 'text-anchor': 'middle' }, formatParameters(value)));
    previous = position;
  }
  if (previous === -Infinity) axes.append(svg('text', { x: x(points[0].parameters.active), y: bottom + 24, 'text-anchor': 'middle' }, formatParameters(points[0].parameters.active)));
  axes.append(svg('text', { x: left, y: 17, class: 'size-axis-title' }, `${metricLabel()} ↓`));
  axes.append(svg('text', { x: (left + right) / 2, y: height - 12, 'text-anchor': 'middle', class: 'size-axis-title' }, 'Active parameters · log scale'));
  plot.append(axes);
  const frontier = points.filter(point => point.frontier);
  if (frontier.length > 1) plot.append(svg('path', {
    d: frontier.map((p, i) => `${i ? 'H' : 'M'}${x(p.parameters.active)}${i ? 'V' : ','}${y(p.error)}`).join(' '), class: 'size-frontier', 'aria-hidden': 'true',
  }));
  for (const point of points) {
    const group = svg('g', { transform: `translate(${x(point.parameters.active)},${y(point.error)})`,
      class: `size-point${point.frontier ? ' frontier' : ''}`, tabindex: '0', role: 'button', 'data-model': point.model.id,
      'aria-pressed': 'false', 'aria-label': `${point.model.name}, ${percent(point.error)} ${metricLabel()}, ${formatParameters(point.parameters.active)} active parameters${point.frontier ? ', Pareto frontier' : ''}. Show details.` });
    group.append(svg('circle', { r: 12, class: 'size-hit' }), svg('circle', { r: 5, class: 'size-dot' }));
    group.addEventListener('mouseenter', () => select(point));
    group.addEventListener('focus', () => select(point));
    group.addEventListener('click', () => select(point));
    group.addEventListener('keydown', event => { if (['Enter', ' '].includes(event.key)) { event.preventDefault(); select(point); } });
    plot.append(group);
  }
  chart.append(plot);
  select(points.find(point => point.model.id === selected) ?? frontier[0] ?? points[0]);
}
export function renderPareto(next: ParetoPoint[], nextMetric: Metric, isOverall: boolean) {
  points = next; metric = nextMetric; overall = isOverall; draw();
}
new ResizeObserver(draw).observe(chart);
