from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

app = FastAPI(title="core-synapse-ui-backend")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 for templating
templates = Jinja2Templates(directory="templates")

# Mock model services
MODEL_SERVICES = [
    {"name": "Sentiment Analysis", "endpoint": "/predict/sentiment-analysis"},
    {"name": "Image Classification", "endpoint": "/predict/image-classification"}
]

# Serve the main UI
@app.get("/")
def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# HTMX endpoint to fetch available models
@app.get("/models")
def get_models():
    # Render a simple HTML snippet that HTMX will inject into the page
    model_html = "".join(
        f"""
        <div class="model">
            <h3>{model['name']}</h3>
            <button hx-get="{model['endpoint']}" hx-target="#prediction-result">Test Model</button>
        </div>
        """ for model in MODEL_SERVICES
    )
    return model_html

# Mock prediction endpoint
@app.get("/predict/{model_name}")
def predict_model(model_name: str):
    return f"<p id='prediction-result'>Response from {model_name}</p>"


