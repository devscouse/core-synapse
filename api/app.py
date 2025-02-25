from enum import StrEnum
import logging
import requests
from fastapi import FastAPI, HTTPException
from src.log import logging_config

logging_config()
logger = logging.getLogger(__name__)

app = FastAPI()

SUPPORTED_MODELS = ["sentiment-analysis"]


class CoreSynapseModels(StrEnum):
    sentiment_analysis = "sentiment-analysis"

    @property
    def base_url(self) -> str:
        return f"http://core-synapse-{self}:5000/"

    @property
    def infer_url(self) -> str:
        return self.base_url + "infer"

    @property
    def health_url(self) -> str:
        return self.base_url + "health"

    @property
    def openapi_url(self) -> str:
        return self.base_url + "openapi.json"


@app.post("/calculate/{model_key}")
def calculate(input_data: dict, model_key: CoreSynapseModels):
    if model_key not in SUPPORTED_MODELS:
        raise HTTPException(
            status_code=400, detail=f"{model_key} is not a supported core-synapse model"
        )
    res = requests.post(model_key.infer_url, json=input_data)
    return res.json()


@app.get("/models/openapi")
def get_models_openapi():
    specs = {}
    for model in CoreSynapseModels:
        try:
            res = requests.get(model.openapi_url)
        except requests.exceptions.RequestException:
            continue

        if res.status_code == 200:
            specs[model] = res.json()

    return specs


@app.get("/health")
def health():
    return {"status": "This API is alive and healthy"}
