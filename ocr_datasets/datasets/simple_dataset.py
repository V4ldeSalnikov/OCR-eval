from pydantic_evals import Case, Dataset
from PIL import Image
from pathlib import Path
from evaluators.standard_evaluator import StandardEvaluator
from models.model_interface import OCRInput
from ocr_datasets.dataset_interface import OCRDataset


class SimpleDataset(OCRDataset):
    id = "simple_dataset"
    languages = ["da"]
    default_evaluator = StandardEvaluator()

    def __init__(self, image_dir: Path | str = None, max_examples: int | None = None):

        if image_dir is None:
            ROOT = Path(__file__).resolve().parents[2]
            self.image_dir = ROOT / "test_images"
        else:
            self.image_dir = Path(image_dir)
        self.max_examples = max_examples

    def load_dataset(self) -> Dataset:

        img1_path = self.image_dir / "test_image_1.jpg"
        img2_path = self.image_dir / "test_image_2.jpg"
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)

        case1 = Case(
            name='first_case',
            inputs=OCRInput(image=img1),
            expected_output='Stå af og træk cyklen',
            metadata={'difficulty': 'easy'},
        )

        case2 = Case(
            name="second_case",
            inputs=OCRInput(image=img2),
            expected_output='Knallert forbudt',
            metadata={'difficulty': 'easy'},
        )

        cases = [case1, case2]
        if self.max_examples is not None:
            cases = cases[:self.max_examples]

        dataset = Dataset(
            name=self.id,
            cases=cases,
            evaluators=[self.default_evaluator],
        )

        return dataset




