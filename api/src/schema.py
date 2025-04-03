import logging
from typing import Dict, Optional, List

from requests.models import RequestField
from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class ModelRequestField(BaseModel):
    key: str
    title: str
    label: str = ""
    dtype: str
    description: str
    default: Optional[str]
    required: bool

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    gt: Optional[float] = None
    ge: Optional[float] = None
    lt: Optional[float] = None
    le: Optional[float] = None

    @model_validator(mode="after")
    def use_title_as_label_if_label_is_empty(self):
        if self.label == "":
            self.label = self.title
        return self


class ModelEndpoint(BaseModel):
    endpoint: str
    description: str = ""
    label: str = ""
    http_method: str
    request_schema: List[ModelRequestField]

    @model_validator(mode="after")
    def use_endpoint_as_label_if_empty(self):
        if self.label == "":
            self.label = self.endpoint[1:]
        return self


class ModelSpec(BaseModel):
    id: str
    name: str
    description: str
    endpoints: List[ModelEndpoint]

    @classmethod
    def from_openapi(cls, model_id: str, openapi: dict):
        logger.debug(f"Creating ModelSpec for {model_id} using OpenAPI JSON: {openapi}")
        if len(openapi["paths"]) == 0:
            raise ValueError(
                "Cannot create model spec from OpenAPI json, paths is empty"
            )

        endpoints = []
        desc = ""
        for pathstr, path in openapi["paths"].items():
            logger.debug(f"Parsing path {pathstr}")

            if pathstr == "/infer":
                desc = path["post"]["description"]

            for method, operation in path.items():
                logger.debug(f"Parsing HTTP method {method}")
                ep = ModelEndpoint(
                    endpoint=pathstr,
                    http_method=method,
                    request_schema=[],
                    label=operation.get("summary", ""),
                    description=operation.get("description", ""),
                )

                if "requestBody" not in operation:
                    endpoints.append(ep)
                    continue

                component_id = operation["requestBody"]["content"]["application/json"][
                    "schema"
                ]["$ref"]
                logger.debug(f"Parsing request body (id={component_id})")
                component_parts = component_id.split("/")
                tgt = openapi
                for part in component_parts:
                    if part == "#":
                        continue
                    tgt = tgt[part]
                logger.debug(f"(id={component_id}) extracted from OpenAPI spec: {tgt}")

                for name, property in tgt["properties"].items():
                    ep.request_schema.append(
                        ModelRequestField(
                            key=name,
                            title=property.get("title", name.title()),
                            description=property.get("description", ""),
                            min_length=property.get("minLength"),
                            dtype=property["type"],
                            required=name in tgt["required"],
                            default=None,
                        )
                    )
                endpoints.append(ep)

        return cls(
            id=model_id,
            name=model_id.replace("-", " ").title(),
            description=desc,
            endpoints=endpoints,
        )
