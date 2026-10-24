export const criteria = [
  ['weights', 'Weights', 'Downloadable model weights, including releases that require accepting terms.'],
  ['license', 'Open license', 'A license permitting use, modification and redistribution, including commercial use, without field-of-use restrictions.'],
  ['code', 'Training code', 'Public code and a recipe for the training that produced this checkpoint; inference code and generic fine-tuning tutorials are insufficient.'],
  ['data', 'Training data', 'The complete training corpus is publicly available, or can be reconstructed from public sources and a released recipe. A description alone is insufficient.'],
  ['paper', 'Paper / report', 'A public technical paper or report describing this model.'],
  ['card', 'Model documentation', 'Public documentation of the model, its intended use and how to run it.'],
] as const;
export type Criterion = typeof criteria[number][0];
export type Status = 'yes' | 'no' | 'partial' | 'unknown';
export type Evidence = { status: Status; note: string; sources: string[] };
export type Checks = Record<Criterion, Evidence>;
export type Openness = { checks: Checks; reviewed: string };
export const statusLabels: Record<Status, string> = { yes: 'Available', no: 'Not open', partial: 'Partial', unknown: 'Unknown' };

const iconPaths: Record<Criterion, string[]> = {
  weights: ['m12 3 9 5v8l-9 5-9-5V8l9-5Z', 'm3 8 9 5 9-5', 'M12 13v8'],
  license: ['M12 3v18M7 21h10M3 7h18', 'm6 7-3 7h6L6 7Zm12 0-3 7h6l-3-7Z'],
  code: ['m8 6-6 6 6 6m8-12 6 6-6 6'],
  data: ['M3 6a9 3 0 1 0 18 0 9 3 0 1 0-18 0', 'M3 6v12a9 3 0 0 0 18 0V6', 'M3 12a9 3 0 0 0 18 0'],
  paper: ['M12 6v15', 'M12 6C9 3 5 3 2 4v16c3-1 7-1 10 1 3-2 7-2 10-1V4c-3-1-7-1-10 2Z'],
  card: ['M14 2H5v20h14V7l-5-5Z', 'M14 2v5h5M8 12h8M8 16h8'],
};

export function opennessIcon(key: Criterion): string {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[key].map(d => `<path d="${d}"/>`).join('')}</svg>`;
}

export const opennessAnchor = (id: string, key?: Criterion) => encodeURIComponent(key ? `${id}--${key}` : id);
