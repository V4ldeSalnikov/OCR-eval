from abc import ABC, abstractmethod
from PIL import Image
from dataclasses import dataclass

@dataclass
class OCRInput:
    """
    Data class for input of OCR
    """
    image : Image.Image

@dataclass
class OCROutput:
    """
    Data class for output of OCR
    """
    text : str

class OCRModel(ABC):

    """
    Abstract class to standardize the datasets

    Attributes :
    id - name of the model
    supported task - list of tasks that model supports (will be added in the future)
    """
    id : str
    supported_tasks : list[str]

    @abstractmethod
    def __call__(self, inputs : OCRInput) -> OCROutput:
        ...
    def batch_call(self, inputs: list[OCRInput]) -> list[OCROutput]:
        return [self(inpt) for inpt in inputs]

