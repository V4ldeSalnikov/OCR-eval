"""Publish every completed leaderboard report without private runtime metadata."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from metrics.metrics import cer, wer

REPOSITORY = 'https://github.com/V4ldeSalnikov/resultsScandiOCReval'
SECRET = re.compile(r'(?<![A-Za-z0-9_])(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|mstrl_[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9_.-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)')
PRIVATE_FIELDS = {'api_key', 'apikey', 'authorization', 'headers', 'response_headers',
                  'request_headers', 'access_token', 'client_secret', 'organization_id',
                  'project_id', 'raw_response', 'source_file', 'source_image_path',
                  'sample_manifest', 'prediction_checkpoints'}
SETTINGS = {'attention_implementation', 'chat_template_options', 'do_sample', 'document_type',
            'dtype', 'endpoint', 'eos_token_id', 'extract_footer', 'extract_header',
            'image_detail', 'image_encoding', 'image_options', 'image_patch_size',
            'image_processor', 'image_resize', 'include_blocks', 'include_image_base64',
            'max_new_tokens', 'max_pixels', 'min_pixels', 'model_id', 'model_revision',
            'output', 'per_task_settings', 'postprocessing', 'prompt', 'prompt_caching',
            'reasoning', 'sdk_version', 'service_tier', 'store', 'system_prompt',
            'table_format', 'thinking', 'user_prompt'}
PROVENANCE = {'batch_size', 'model_revision', 'started_at', 'finished_at', 'code_revision',
              'implementation_sha256', 'runtime_guards', 'failure_policy', 'gpu_memory',
              'runtime_settings', 'usage_info', 'estimated_cost_usd'}
CASE_METADATA = {'doc_id', 'dpi', 'handle', 'lang', 'license', 'line_bbox', 'line_id',
                 'page', 'page_id', 'page_type', 'pdf_id', 'publication_id', 'reference_tool',
                 'reference_type', 'revision', 'sequence', 'source', 'source_pdf_sha256',
                 'source_row', 'split', 'title', 'url', 'year'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check_public(value, key=''):
    """Fail closed on private fields, credentials or machine paths in metadata."""
    if isinstance(value, dict):
        for field, item in value.items():
            assert field.lower() not in PRIVATE_FIELDS, f'Private field: {field}'
            check_public(item, field)
    elif isinstance(value, list):
        for item in value:
            check_public(item, key)
    elif isinstance(value, str):
        assert not SECRET.search(value), f'Credential pattern in field: {key}'
        if key not in {'reference', 'prediction', 'text'}:
            assert not re.search(r'(?<![A-Za-z0-9])[A-Za-z]:[\\/]|\\\\[^\\]+\\', value), f'Local path in field: {key}'


def write(path, value):
    check_public(value)
    text = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def report_path(model_id, sample_set_id):
    return f"reports/{model_id.replace('/', '--')}/{sample_set_id}.json"


def export(snapshot_path, output, ocr_root=ROOT):
    snapshot = read(snapshot_path)
    samples = {s['id']: s for s in snapshot['sample_sets']}
    datasets = {d['id']: d for d in snapshot['datasets']}
    manifests, published, seen = {}, [], set()
    for row in snapshot['results']:
        identity = (row['model_id'], row['sample_set_id'])
        assert identity not in seen, 'Duplicate model/task result'
        seen.add(identity)
        assert row['status'] == 'completed'
        sample = samples[row['sample_set_id']]
        run = ocr_root / 'runs' / row['run_id']
        folder = run / 'results' / row['model_id'].replace('/', '--') / sample['id']
        raw = read(folder / 'report.json')
        state = read(folder / 'status.json')
        assert state['status'] == 'completed'
        assert raw['model'] == row['model_id'] and raw['task'] == sample['task']
        assert raw['corpus_metrics'] == row['corpus_metrics']
        assert raw['benchmark']['sample_manifest_sha256'] == sample['manifest_sha256']
        if sample['id'] not in manifests:
            # Hosted runs reuse the frozen samples from the first local sweep.
            manifest_path = next(
                ocr_root / 'runs' / source['id'] / 'samples' / sample['id'] / 'manifest.json'
                for source in snapshot['source_runs']
                if (ocr_root / 'runs' / source['id'] / 'samples' / sample['id'] / 'manifest.json').exists()
            )
            assert sha256(manifest_path.read_bytes()).hexdigest() == sample['manifest_sha256']
            manifests[sample['id']] = read(manifest_path)
        manifest = manifests[sample['id']]
        cases = []
        for frozen, case in zip(manifest['cases'], raw['cases'], strict=True):
            assert (frozen['name'], frozen['reference']) == (case['name'], case['reference'])
            item = {key: case[key] for key in ('name', 'reference', 'prediction', 'cer', 'wer')}
            item['inference_status'] = case.get('inference_status', 'success')
            assert item['inference_status'] in {'success', 'failed'}
            if item['inference_status'] == 'failed':
                assert item['prediction'] == ''
            item['image_sha256'] = frozen['image_sha256']
            item['metadata'] = {k: v for k, v in frozen['metadata'].items() if k in CASE_METADATA}
            for key, metric in (('cer', cer), ('wer', wer)):
                assert abs(metric(item['prediction'], item['reference']) - item[key]) < 1e-12
            cases.append(item)
        counts = Counter(case['inference_status'] for case in cases)
        assert len(cases) == row['completed_samples'] == row['selected_samples'] == sample['selected_samples']
        assert counts['failed'] == row['failed_samples'] and counts['success'] == row['successful_samples']
        for key, metric in (('cer', cer), ('wer', wer)):
            actual = metric([c['prediction'] for c in cases], [c['reference'] for c in cases])
            assert abs(actual - row['corpus_metrics'][key]) < 1e-12
        public = {
            'schema_version': 1, 'run_id': row['run_id'], 'model_id': row['model_id'],
            'sample_set_id': sample['id'], 'dataset_id': sample['dataset_id'],
            'dataset_name': raw['dataset'], 'task': sample['task'], 'status': 'completed',
            'selected_samples': len(cases), 'completed_samples': len(cases),
            'successful_samples': counts['success'], 'failed_samples': counts['failed'],
            'corpus_metrics': row['corpus_metrics'],
            'manifest_sha256': sample['manifest_sha256'], 'source_revision': sample['source_revision'],
            'source_url': datasets[sample['dataset_id']]['source_url'], 'split': sample['split'],
            'reference_type': sample['reference_type'], 'seed': manifest['seed'],
            'sampling_method': manifest['sampling_method'],
            **{k: row[k] for k in PROVENANCE if k in row},
            'inference_settings': ({k: v for k, v in raw['inference_settings'].items() if k in SETTINGS}
                                   if raw.get('inference_settings') is not None else None),
            'cases': cases,
        }
        rel = report_path(*identity)
        write(output / rel, public)
        row['public_report_url'] = f'{REPOSITORY}/blob/main/{rel}'
        published.append({'model_id': row['model_id'], 'run_id': row['run_id'],
                          'sample_set_id': sample['id'], 'report': rel,
                          'sha256': sha256((output / rel).read_bytes()).hexdigest(),
                          'samples': len(cases), 'failed_samples': counts['failed'],
                          'corpus_metrics': row['corpus_metrics']})
    counts = {'models': len(snapshot['models']), 'datasets': len(datasets), 'tasks': len(samples),
              'reports': len(published), 'predictions': sum(t['samples'] for t in published),
              'failed_predictions': sum(t['failed_samples'] for t in published)}
    write(output / 'leaderboard.json', snapshot)
    write(output / 'index.json', {'schema_version': 1, 'counts': counts, 'reports': published,
                                 'validation': {'passed': True, 'checks': [
                                     'completed attempts', 'frozen manifest hashes', 'reference alignment',
                                     'per-example and corpus CER/WER recomputation', 'leaderboard score equality',
                                     'failure counts', 'credential and private metadata scan']}})
    write(snapshot_path, snapshot)
    return counts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, default=ROOT / 'website/public/results.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.snapshot.resolve(), args.output.resolve())))
