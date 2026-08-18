from abc import ABC, abstractmethod
from pydantic_evals import Dataset
from pydantic_evals.evaluators import Evaluator



class OCRDataset(ABC):

    """
    Abstract class to standardize the datasets

    Attributes :

    id - name of the dataset
    languages - languages that are present in dataset
    default_evaluator - default evaluator that will be used for the dataset

    Functions :

    Load dataset - responsible to loading the dataset (together with default evaluator)
    """
    id: str
    languages: list[str]
    default_evaluator : Evaluator | None


    @abstractmethod
    def load_dataset(self) -> Dataset:
        ...


