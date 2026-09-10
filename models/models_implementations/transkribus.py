import os
from time import monotonic, sleep

import requests

from models.image_encoding import image_to_png_base64
from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


TOKEN_URL = (
    "https://account.readcoop.eu/auth/realms/readcoop/"
    "protocol/openid-connect/token"
)
PROCESS_URL = "https://transkribus.eu/processing/v1/processes"


class TranskribusOCR(OCRModel):
    def __init__(
        self,
        model_name: str,
        htr_id: int,
        task: str,
        language_model: str | None = None,
        poll_interval: float = 2.0,
        process_timeout: float = 600.0,
    ):
        self.id = model_name
        self.task = task
        self.htr_id = htr_id
        self.language_model = language_model
        self.poll_interval = poll_interval
        self.process_timeout = process_timeout
        self.username = os.environ["TRANSKRIBUS_USERNAME"]
        self.password = os.environ["TRANSKRIBUS_PASSWORD"]
        self.session = requests.Session()
        self.token_expires_at = 0.0

    def __call__(self, inputs: OCRInput) -> OCROutput:
        return self.batch_call([inputs])[0]

    def batch_call(self, inputs: list[OCRInput]) -> list[OCROutput]:
        process_ids = [self._submit(input_item) for input_item in inputs]
        return [OCROutput(text=self._wait(process_id)) for process_id in process_ids]

    def _ensure_access_token(self) -> None:
        if monotonic() < self.token_expires_at:
            return

        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": "processing-api-client",
            },
            timeout=60,
        )
        response.raise_for_status()
        token = response.json()
        self.session.headers["Authorization"] = f"Bearer {token['access_token']}"
        self.token_expires_at = monotonic() + token["expires_in"] - 30

    def _submit(self, inputs: OCRInput) -> int:
        self._ensure_access_token()
        text_recognition = {"htrId": self.htr_id}
        if self.language_model is not None:
            text_recognition["languageModel"] = self.language_model

        response = self.session.post(
            PROCESS_URL,
            json={
                "config": {"textRecognition": text_recognition},
                "image": {"base64": image_to_png_base64(inputs.image)},
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["processId"]

    def _wait(self, process_id: int) -> str:
        deadline = monotonic() + self.process_timeout
        while monotonic() < deadline:
            self._ensure_access_token()
            response = self.session.get(
                f"{PROCESS_URL}/{process_id}",
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()

            match result["status"]:
                case "FINISHED":
                    return result["content"]["text"]
                case "FAILED":
                    raise RuntimeError(
                        f"Transkribus process {process_id} failed: {result}"
                    )
                case "CREATED" | "WAITING" | "RUNNING":
                    sleep(self.poll_interval)
                case status:
                    raise RuntimeError(
                        f"Unknown Transkribus process status: {status}"
                    )

        raise TimeoutError(f"Transkribus process {process_id} timed out")


TRANSKRIBUS_DANSK_DOKUMENTALIST = ModelMeta(
    loader=TranskribusOCR,
    name="Transkribus/Dansk-Dokumentalist-309713",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={
        "model_name": "Transkribus/Dansk-Dokumentalist-309713",
        "htr_id": 309713,
    },
    family="Transkribus",
    languages=["da-Latn"],
    license="proprietary",
    reference=(
        "https://www.transkribus.org/models/"
        "dansk-dokumentalist-super-model"
    ),
    notes="Broad Danish print and handwriting model",
)

TRANSKRIBUS_DANISH_1870_1950 = ModelMeta(
    loader=TranskribusOCR,
    name="Transkribus/Danish-1870-1950-v3.5-26311",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={
        "model_name": "Transkribus/Danish-1870-1950-v3.5-26311",
        "htr_id": 26311,
    },
    family="Transkribus",
    languages=["da-Latn"],
    license="proprietary",
    reference=(
        "https://www.transkribus.org/models/"
        "danish-handwriting-19th-20th-century-1"
    ),
    notes="Danish historical handwriting model; may overlap historical-danish",
)

TRANSKRIBUS_ROYAL_DANISH_LIBRARY_20TH_CENTURY = ModelMeta(
    loader=TranskribusOCR,
    name="Transkribus/RoyalDanishLibrary-20thCentury-47113",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={
        "model_name": "Transkribus/RoyalDanishLibrary-20thCentury-47113",
        "htr_id": 47113,
    },
    family="Transkribus",
    languages=["da-Latn"],
    license="proprietary",
    reference="https://www.transkribus.org/models/danish-20th-century",
    notes="Modern twentieth-century Danish cursive handwriting model",
)

TRANSKRIBUS_DANISH_NEWSPAPERS = ModelMeta(
    loader=TranskribusOCR,
    name="Transkribus/Danish-Newspapers-1750-1850-306013",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={
        "model_name": "Transkribus/Danish-Newspapers-1750-1850-306013",
        "htr_id": 306013,
        "language_model": "built-in",
    },
    family="Transkribus",
    languages=["da-Latn"],
    license="proprietary",
    reference=(
        "https://www.transkribus.org/models/"
        "danish-newspapers-1750-1850"
    ),
    notes="Danish Fraktur newspaper model with its built-in language model",
)
