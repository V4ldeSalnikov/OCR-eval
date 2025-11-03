# main.py

from ocr_datasets.datasets.simple_dataset import SimpleDataset
from tasks.ocr_task import default_ocr_task
from models.model_registry import  get_model

def main():
    model = get_model("Qwen/Qwen2-VL-2B-Instruct")
    dataset = SimpleDataset().load_dataset()
    task = default_ocr_task(model)
    report = dataset.evaluate_sync(task)
    report.print(include_input=True, include_output=True, include_durations=True)

if __name__ == "__main__":
    main()