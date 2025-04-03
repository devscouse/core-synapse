import requests
import httpx
import os
from enum import StrEnum
import logging
from typing import Annotated, Dict
from fastapi import FastAPI, HTTPException, Header, Request
from starlette.background import BackgroundTask
from starlette.datastructures import ImmutableMultiDict
from starlette.responses import StreamingResponse
from src.log import logging_config
from src.schema import ModelSpec
from src.config import cfg, Env

logging_config()
logger = logging.getLogger(__name__)

app = FastAPI()


class CoreSynapseModels(StrEnum):
    sentiment_analysis = "sentiment-analysis"

    @property
    def base_url(self) -> str:
        if cfg.env == "local":
            __import__("dotenv").load_dotenv()
            return os.environ[str(self).replace("-", "_") + "_url"]
        return f"http://core-synapse-{self}:5000/"

    @property
    def openapi_url(self) -> str:
        return self.base_url + "openapi.json"

    async def openapi(self) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            res = await client.get(self.openapi_url)
        return res

    async def proxy_request(
        self, path_name: str, request: Request
    ) -> httpx.Response:
        url = httpx.URL(path=path_name, query=request.url.query.encode("utf-8"))
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60) as client:
            req = client.build_request(
                request.method,
                url,
                headers=request.headers.raw,
                content=request.stream(),
            )
            logger.debug(f"Sending request to {self} API: {req}")
            res = await client.send(req)
        return res


@app.api_route(
    "/service/{path_name:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def service_proxy(
    request: Request, path_name: str, model_key: Annotated[str, Header()]
):
    mdl = CoreSynapseModels(model_key)
    res = await mdl.proxy_request(path_name, request)
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.json()["detail"])
    return res.json()


@app.get(
    "/modelspecs",
    description="Get the specifications for all models currently hosted on the Core Synapse platform.",
)
def get_model_specs() -> Dict[str, ModelSpec]:
    specs = {}
    for model in CoreSynapseModels.__members__.values():
        try:
            res = requests.get(model.openapi_url)
        except httpx.RequestError:
            logger.warning(f"Unable to retrieve openapi.json for {model}")
            continue

        if res.status_code != 200:
            logger.warning(f"Unable to retrieve openapi.json for {model}")
            continue

        specs[str(model)] = ModelSpec.from_openapi(model, res.json())

    logger.debug(specs)
    return specs


@app.get("/health")
def health():
    return {"status": "This API is alive and healthy"}
