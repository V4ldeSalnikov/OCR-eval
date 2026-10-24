import { rankModels, type Metric, type Model, type SampleSet, type Snapshot } from './ocr-results.ts';

export type ParameterCount = { total: number; active: number; revision: string };
export type ParetoPoint = { model: Model; error: number; parameters: ParameterCount; frontier: boolean };

export function paretoPoints(data: Snapshot, samples: SampleSet[], metric: Metric, counts: Record<string, ParameterCount>): ParetoPoint[] {
  const points = rankModels(data, samples, null, metric).flatMap(row => {
    const parameters = counts[row.model.id];
    return parameters && Number.isFinite(parameters.active) && parameters.active > 0 && row.metrics[metric] >= 0
      ? [{ model: row.model, error: row.metrics[metric], parameters, frontier: false }] : [];
  });
  // A point is dominated only if another is no worse on either axis and better
  // on at least one. Exact ties remain on the frontier together.
  for (const point of points) point.frontier = !points.some(other =>
    other.parameters.active <= point.parameters.active && other.error <= point.error
    && (other.parameters.active < point.parameters.active || other.error < point.error));
  return points.sort((a, b) => a.parameters.active - b.parameters.active || a.error - b.error || a.model.id.localeCompare(b.model.id));
}

export function formatParameters(value: number): string {
  return value >= 1e9 ? `${+(value / 1e9).toPrecision(3)}B` : `${+(value / 1e6).toPrecision(3)}M`;
}
