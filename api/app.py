import os
from enum import StrEnum
import logging
from typing import Dict
import requests
from fastapi import FastAPI, HTTPException
from src.log import logging_config
from src.schema import ModelSpec, OpenApiJson
from src.config import cfg, Env

logging_config()
logger = logging.getLogger(__name__)

app = FastAPI()

SUPPORTED_MODELS = ["sentiment-analysis"]


class CoreSynapseModels(StrEnum):
    sentiment_analysis = "sentiment-analysis"

    @property
    def base_url(self) -> str:
        if cfg.env == "local":
            __import__("dotenv").load_dotenv()
            return os.environ[str(self).replace("-", "_") + "_url"]
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


@app.get(
    "/modelspecs",
    description="Get the specifications for all models currently hosted on the Core Synapse platform.",
)
def get_models_openapi() -> Dict[str, ModelSpec]:
    specs = {}
    for model in CoreSynapseModels.__members__.values():
        try:
            res = requests.get(model.openapi_url)
        except requests.exceptions.RequestException:
            logger.warning(f"Unable to retrieve openapi.json for {model}")
            continue

        if res.status_code != 200:
            logger.warning(f"Unable to retrieve openapi.json for {model}")
            continue
        
        data = res.json()
        logger.debug(f"OpenAPI for {model}: {data}")

        spec = OpenApiJson.model_validate(data)
        specs[model] = ModelSpec.from_openapi(model, spec)

    return specs


@app.get("/health")
def health():
    return {"status": "This API is alive and healthy"}
