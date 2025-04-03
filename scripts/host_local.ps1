start powershell { cd api; .venv/scripts/activate; uvicorn app:app --host 0.0.0.0 --port 5000 --reload; }
start powershell { cd models/sentiment-analysis; .venv/scripts/activate; uvicorn app:app --host 0.0.0.0 --port 5001 --reload; }
