import logging
from fastapi import FastAPI
from pydantic import BaseModel, Field
from ..common.log import logging_config

logging_config()
logger = logging.getLogger(__name__)

app = FastAPI()


class SpamDetectorRequest(BaseModel):
    text: str = Field(min_length=1)


class SpamDetectorResponse(BaseModel):
    is_spam: bool
    confidence: float = Field(ge=0, le=1)


@app.post("/infer")
def infer(body: SpamDetectorRequest) -> SpamDetectorResponse:
    del body
    return SpamDetectorResponse(is_spam=True, confidence=1)
