import logging
from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.log import logging_config

logging_config()
logger = logging.getLogger(__name__)

app = FastAPI()


class SentimentAnalysisRequest(BaseModel):
    text: str = Field(min_length=1, description="The text to analyse the sentiment of")


class SentimentAnalysisResponse(BaseModel):
    polarity: float = Field(
        ge=-1,
        le=1,
        description="The polarity of the given text, -1 indicates maximum negativity, 0 indicates neutral, and 1 indicates maximum positivity",
    )


@app.post(
    "/infer",
    description="Analyse the sentiment (positivity or negativity) of a given piece of text",
)
def infer(body: SentimentAnalysisRequest) -> SentimentAnalysisResponse:
    del body
    return SentimentAnalysisResponse(polarity=1)


@app.get("/health")
def health():
    return {"status": "The service is alive and healthy"}
