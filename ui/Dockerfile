FROM python:3.11-slim

WORKDIR /app
COPY ui/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ui/ .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

