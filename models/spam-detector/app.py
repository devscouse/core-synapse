from fastapi import FastAPI
from pydantic import BaseModel, Field

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
