# main.py

import json
from datetime import UTC, datetime
from pathlib import Path

from metrics.metrics import cer, wer
from models.model_registry import get_model
from ocr_datasets.datasets.simple_dataset import SimpleDataset
from tasks.ocr_task import run_batch_ocr


def main():
    model = get_model("Qwen/Qwen2-VL-2B-Instruct")
    dataset = SimpleDataset().load_dataset()
    batch_size = 2
    results = run_batch_ocr(model, dataset, batch_size=batch_size)
    predictions = [output.text for _, output in results]
    references = [case.expected_output for case, _ in results]

    case_results = [
        {
            "name": case.name,
            "reference": case.expected_output,
            "prediction": output.text,
            "cer": cer(output.text, case.expected_output),
            "wer": wer(output.text, case.expected_output),
            "metadata": case.metadata,
        }
        for case, output in results
    ]
    corpus_metrics = {
        "cer": cer(predictions, references),
        "wer": wer(predictions, references),
    }
    report = {
        "model": model.id,
        "dataset": dataset.name,
        "batch_size": batch_size,
        "cases": case_results,
        "corpus_metrics": corpus_metrics,
    }

    for case_result in report["cases"]:
        print(case_result["name"])
        print(f"Expected: {case_result['reference']}")
        print(f"Predicted: {case_result['prediction']}")
        print(f"CER: {case_result['cer']:.4f}")
        print(f"WER: {case_result['wer']:.4f}")
        print()

    print("Corpus")
    print(f"CER: {report['corpus_metrics']['cer']:.4f}")
    print(f"WER: {report['corpus_metrics']['wer']:.4f}")

    runs_dir = Path(__file__).resolve().parent / "runs"
    runs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    model_name = model.id.replace("/", "--")
    report_path = runs_dir / f"{timestamp}_{dataset.name}_{model_name}.json"
    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"Saved: {report_path}")


if __name__ == "__main__":
    main()
