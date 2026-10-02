"""Export audited hosted runs as portable public reports, without private runtime data."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from metrics.metrics import cer, wer

MODELS = {
    'Mistral/mistral-ocr-4-1': {'family': 'Mistral OCR', 'reference': 'https://docs.mistral.ai/models/ocr-4-1',
                              'notes': 'Dedicated OCR API; raw Markdown output.'},
    'OpenAI/gpt-6.1-sol': {'family': 'GPT-6.1', 'reference': 'https://developers.openai.com/api/docs/models/gpt-6.1-sol',
                          'notes': 'Standard API, low reasoning, original image detail.'},
}
SETTING_FIELDS = {'model_id', 'endpoint', 'document_type', 'image_encoding', 'image_resize', 'image_detail',
                  'include_blocks', 'include_image_base64', 'table_format', 'extract_header', 'extract_footer',
                  'prompt', 'thinking', 'output', 'sdk_version', 'reasoning', 'service_tier', 'store',
                  'prompt_caching', 'per_task_settings'}
REQUEST_FIELDS = {'model', 'instructions', 'user_prompt', 'detail', 'reasoning', 'max_output_tokens', 'service_tier', 'store'}
RUNTIME_FIELDS = {'workers', 'min_request_interval_seconds', 'request_timeout_seconds', 'timeout_seconds',
                  'sdk_retries', 'rate_limit_retries', 'retry_failed_samples'}
SECRET = re.compile(r'(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|mstrl_[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{20,})')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    text = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + '\n'
    assert not SECRET.search(text), f'Credential pattern detected in export: {path.name}'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def settings(source):
    result = {k: v for k, v in source.items() if k in SETTING_FIELDS}
    if 'per_task_settings' in result:
        result['per_task_settings'] = {task: {k: v for k, v in item.items() if k in REQUEST_FIELDS}
                                       for task, item in result['per_task_settings'].items()}
    return result


def export(run):
    plan, audit, summary = (read(run / name) for name in ('plan.json', 'audit.json', 'summary.json'))
    assert audit['passed'] and summary['status'] == 'completed'
    assert audit['samples_checked'] == 6477 and audit['tasks_checked'] == 11
    model_id = plan['model']
    model = {'id': model_id, 'name': model_id, **MODELS[model_id], 'license': 'proprietary',
             'supported_tasks': ['line-recognition', 'page-transcription'], 'warnings': []}
    out = ROOT / 'results' / run.name
    published = []
    for job in plan['jobs']:
        manifest_path = Path(job['manifest'])
        assert sha256(manifest_path.read_bytes()).hexdigest() == job['sha256']
        manifest = read(manifest_path)
        folder = run / 'results' / model_id.replace('/', '--') / job['task'] / job['dataset']
        report, state = read(folder / 'report.json'), read(folder / 'status.json')
        assert state['status'] == 'completed'
        assert report['model'] == model_id and report['task'] == job['task']
        assert report['benchmark']['sample_manifest_sha256'] == job['sha256']
        cases = []
        for frozen, case in zip(manifest['cases'], report['cases'], strict=True):
            assert frozen['name'] == case['name'] and frozen['reference'] == case['reference']
            item = {k: case[k] for k in ('name', 'reference', 'prediction', 'cer', 'wer', 'inference_status')}
            item['image_sha256'] = frozen['image_sha256']
            if item['inference_status'] == 'failed':
                assert item['prediction'] == ''
            cases.append(item)
        assert len(cases) == job['samples']
        for key, metric in (('cer', cer), ('wer', wer)):
            value = metric([c['prediction'] for c in cases], [c['reference'] for c in cases])
            assert abs(value - report['corpus_metrics'][key]) < 1e-12
        first = manifest['cases'][0]['metadata']
        public = {'schema_version': 1, 'run_id': run.name, 'model_id': model_id,
                  'sample_set_id': f"{job['task']}/{job['dataset']}", 'dataset_id': job['dataset'],
                  'dataset_name': report['dataset'], 'task': job['task'], 'status': 'completed',
                  'selected_samples': len(cases), 'completed_samples': len(cases),
                  'successful_samples': report['execution']['successful_samples'],
                  'failed_samples': report['execution']['failed_samples'], 'batch_size': report['batch_size'],
                  'corpus_metrics': report['corpus_metrics'], 'manifest_sha256': job['sha256'],
                  'source_revision': manifest.get('source_revision'), 'split': first.get('split'),
                  'source_url': f"https://huggingface.co/datasets/{first['source']}",
                  'seed': manifest['seed'], 'sampling_method': manifest['sampling_method'],
                  'reference_type': first.get('reference_type', 'annotated_text'),
                  'started_at': state.get('started_at'), 'finished_at': state.get('finished_at'),
                  'code_revision': plan['git_commit'], 'implementation_sha256': plan['local_runner_sha256'],
                  'inference_settings': settings(report['inference_settings']),
                  'runtime_settings': {k: v for k, v in plan['runtime_settings'].items() if k in RUNTIME_FIELDS},
                  'failure_policy': report['failure_policy'], 'usage_info': report['usage_info'],
                  'estimated_cost_usd': report['estimated_cost_usd'], 'cases': cases}
        rel = f"{job['task']}/{job['dataset']}.json"
        write(out / rel, public)
        published.append({'sample_set_id': public['sample_set_id'], 'report': rel,
                          'sha256': sha256((out / rel).read_bytes()).hexdigest(),
                          'samples': len(cases), 'corpus_metrics': public['corpus_metrics'],
                          'estimated_cost_usd': public['estimated_cost_usd']})
    total = sum(t['estimated_cost_usd'] for t in published)
    index = {'schema_version': 1, 'run_id': run.name, 'model': model, 'status': 'completed',
             'started_at': plan['created_at'], 'finished_at': summary['finished_at'],
             'code_revision': plan['git_commit'], 'seed': public['seed'],
             'targets': {'line-recognition': 1000, 'page-transcription': 100},
             'samples': sum(t['samples'] for t in published), 'failed_samples': summary['failed_samples'],
             'estimated_cost_usd': total, 'benchmarks': audit['benchmarks'], 'tasks': published,
             'validation': {'passed': True, 'tasks_checked': 11, 'samples_checked': 6477,
                            'checks': ['frozen manifest hashes', 'image/reference alignment', 'corpus CER/WER recomputation',
                                       'completed run audit', 'credential pattern scan']}}
    write(out / 'index.json', index)
    lines = [f"# {model_id} — ScandiOCR results", '',
             f"Completed {summary['finished_at'][:10]}: 6,477 images across 11 tasks. Estimated API cost: ${total:.2f} before tax.", '',
             model['notes'], 'Images were sent at their original dimensions as RGB PNG.', '',
             '| Benchmark | CER | WER |', '|---|---:|---:|']
    lines += [f"| {b['benchmark']} | {b['cer']:.2%} | {b['wer']:.2%} |" for b in audit['benchmarks']]
    lines += ['', 'Each task report contains all references, unmodified predictions, per-example and corpus CER/WER, image hashes, source revisions, inference settings and token/page usage. The index records SHA256 hashes of these public reports.', '',
              'Task scores use NFC and whitespace normalization, preserving case and punctuation. Benchmark scores are equal-weight means of task corpus scores. Failed attempts are empty predictions; insertion errors are not capped.', '',
              'Source texts remain subject to the original dataset terms, linked in each report. Input images are not included. Private runtime paths, credentials, HTTP headers and provider response identifiers are excluded.', '',
              '[Leaderboard and dataset documentation](https://v4ldesalnikov.github.io/ocr-eval/)', '']
    (out / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'run': run.name, 'reports': len(published), 'predictions': index['samples'], 'output': str(out)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, action='append', required=True)
    for run in parser.parse_args().run_dir:
        export(run.resolve())
