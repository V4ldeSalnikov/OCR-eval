"""Publish Danish Fraktur results with the archived v1 results in the current catalogue."""
import argparse
from datetime import UTC, datetime
from hashlib import sha256
import json
from pathlib import Path
import sys

from export_all_results import ROOT, export, read, write

sys.path.insert(0, str(ROOT / "website/scripts"))
from export_ocr_examples import export_examples
from import_hosted_results import counts

DATASET_ID = "danish-fraktur"
SAMPLE_ID = "page-transcription/danish-fraktur"
SOURCE_URL = "https://github.com/V4ldeSalnikov/OCR-eval/tree/main/ocr_datasets/data/danish_fraktur"


def publish(run, output):
    public = ROOT / "website/public"
    data = read(public / "results.json")
    plan = read(run / "plan.json")
    manifest_path = run / "samples" / SAMPLE_ID / "manifest.json"
    manifest = read(manifest_path)
    manifest_hash = sha256(manifest_path.read_bytes()).hexdigest()
    source_manifest = run / "dataset_provenance/manifest.jsonl"
    assert sha256(source_manifest.read_bytes()).hexdigest() == manifest["source_manifest_sha256"]
    source = [json.loads(line) for line in source_manifest.read_text(encoding="utf-8").splitlines()]
    released = [json.loads(line) for line in (ROOT / "ocr_datasets/data/danish_fraktur/manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    # Release 1.0.0 changes only the status/version, retaining every evaluated field.
    assert [{k: v for k, v in row.items() if k != "dataset_version"} for row in released] == [
        {k: v for k, v in row.items() if k != "dataset_version"} for row in source]
    assert len(source) == len(manifest["cases"]) == 20
    assert [(row["id"], row["text"], row["image_sha256"]) for row in source] == [
        (case["name"], case["reference"], case["image_sha256"]) for case in manifest["cases"]]
    selected = {item["model"]: item for item in plan["selection"]}
    assert len(selected) == len(plan["jobs"]) == 5
    assert DATASET_ID not in {item["id"] for item in data["datasets"]}
    data["datasets"].append({
        "id": DATASET_ID, "label": "Danish Fraktur books", "language_codes": ["da"],
        "document_type": "printed", "source_url": SOURCE_URL,
        "tasks": ["page-transcription"], "version": "1.0.0", "warnings": ["fraktur-reference-review"],
    })
    data["sample_sets"].append({
        "id": SAMPLE_ID, "dataset_id": DATASET_ID, "task": "page-transcription",
        "selected_samples": 20, "target_samples": 20, "source_revision": manifest["source_revision"],
        "split": "test", "sampling_method": manifest["sampling_method"],
        "manifest_sha256": manifest_hash, "reference_type": "annotated_text",
    })
    new_results = []
    for job in plan["jobs"]:
        model_id = job["model"]
        assert model_id in {item["id"] for item in data["models"]}
        assert job["dataset"] == DATASET_ID and job["task"] == "page-transcription"
        directory = run / "results" / model_id.replace("/", "--") / SAMPLE_ID
        report, state = read(directory / "report.json"), read(directory / "status.json")
        assert state["status"] == "completed" and state["completed_samples"] == 20
        benchmark = report["benchmark"]
        assert benchmark["sample_manifest_sha256"] == manifest_hash
        assert benchmark["model_revision"] == selected[model_id]["model_revision"]
        new_results.append({
            "run_id": run.name, "model_id": model_id, "sample_set_id": SAMPLE_ID,
            "status": "completed", "completed_samples": 20, "selected_samples": 20,
            "target_samples": 20, "successful_samples": state["successful_samples"],
            "failed_samples": state["failed_samples"], "corpus_metrics": report["corpus_metrics"],
            "batch_size": job["batch_size"], "started_at": state["started_at"],
            "finished_at": state["finished_at"], "model_revision": benchmark["model_revision"],
            "code_revision": benchmark["git_commit"],
            "implementation_sha256": benchmark["implementation_sha256"],
            "inference_settings": report["inference_settings"],
            "runtime_guards": benchmark["runtime_guards"], "failure_policy": report["failure_policy"],
            "gpu_memory": benchmark["gpu_memory"], "warnings": ["fraktur-reference-review"],
        })
    data["results"].extend(new_results)
    data["source_runs"].append({
        "id": run.name, "git_commit": plan["git_commit"], "seed": None,
        "targets": {"page-transcription": 20}, "metric_policy": data["run"]["metric_policy"],
        "warnings": ["fraktur-reference-review"], "counts": counts(new_results, 5, 1, 1),
        "model_selection": [{key: item[key] for key in ("rank", "model", "license", "swedish_cer", "swedish_wer", "model_revision", "selection_report_sha256")} for item in plan["selection"]],
        "selection_method": plan["selection_method"], "task_note": plan["task_note"],
    })
    data["warnings"].append({"id": "fraktur-reference-review", "message": "Danish Fraktur is a complete 20-page task in the Danish and Scandinavian benchmarks. References have Wikisource validation and an additional AI scan review, not an independent human audit. Initial models were selected by Swedish Fraktur line CER; Danish inputs are whole pages. The completed 1.0.0 release preserves every reference and image; saved evaluations retain their original source revision identifiers."})
    data["generated_at"] = datetime.now(UTC).isoformat()
    data["run"].update(
        id=" + ".join(item["id"] for item in data["source_runs"]),
        git_commit=", ".join(dict.fromkeys(item["git_commit"] for item in data["source_runs"])),
        counts=counts(data["results"], len(data["models"]), len(data["datasets"]), len(data["sample_sets"])),
    )
    catalog = public / "catalog.json"
    write(catalog, data)
    report_counts = export(catalog, output, ROOT)
    example_counts = export_examples(read(catalog), ROOT, public / "examples", output, "catalog.json")["counts"]
    return {"reports": report_counts, "examples": example_counts}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=ROOT / "runs/danish_fraktur_top5_20261104")
    parser.add_argument("--output", type=Path, default=ROOT.parent / "resultsScandiOCReval")
    args = parser.parse_args()
    print(json.dumps(publish(args.run_dir.resolve(), args.output.resolve())))
