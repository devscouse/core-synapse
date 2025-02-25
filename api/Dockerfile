FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl

WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
