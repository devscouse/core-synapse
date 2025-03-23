from typing import Dict, Optional, List
from pydantic import BaseModel, Field


class Info(BaseModel):
    title: str
    version: str


class Schema(BaseModel):
    ref: Optional[str] = Field(default=None, validation_alias="$ref")
    type: Optional[str] = None
    title: Optional[str] = None
    enum: Optional[List[str]] = None


class Parameter(BaseModel):
    name: str
    given_in: str = Field(validation_alias="in")
    required: bool
    dtype: Schema = Field(validation_alias="schema")


class Content(BaseModel):
    dtype: Schema = Field(validation_alias="schema")


class RequestBody(BaseModel):
    required: bool
    content: Dict[str, Content]


class Response(BaseModel):
    description: str
    content: Dict[str, Content]


class Operation(BaseModel):
    operationId: str
    summary: str
    description: str
    parameters: List[Parameter] = Field(default_factory=list)
    requestBody: RequestBody
    responses: Dict[int, Response]


class Path(BaseModel):
    post: Optional[Operation] = None


class Components(BaseModel):
    schemas: Dict[str, Schema]


class OpenApiJson(BaseModel):
    openapi: str
    info: Info
    paths: Dict[str, Path]
    components: Components


class ModelSpec(BaseModel):
    id: str
    name: str
    description: str
    operation: Operation
    response: Optional[Response]
    components: Components

    @classmethod
    def from_openapi(cls, model_id: str, openapi: OpenApiJson):
        if len(openapi.paths) == 0:
            raise ValueError(
                "Cannot create model spec from OpenAPI json, paths is empty"
            )

        operation = None
        for pathstr, path in openapi.paths.items():
            if not pathstr.endswith("infer"):
                continue
            operation = path.post

        if operation is None:
            raise ValueError(
                "Cannot create model spec from OpenAPI json, expected endpoint not found"
            )

        return cls(
            id=model_id,
            name=model_id.replace("-", " ").title(),
            description=operation.description,
            operation=operation,
            response=operation.responses.get(200),
            components=openapi.components,
        )
