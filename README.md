# AI Intrusion Detection System

## How to Run

1. Train the model (if not already trained):
```bash
python -m model.train
```

2. Start the API server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. Open `frontend/index.html` in your browser

## API Endpoints

- GET `/` - Check if API is running
- POST `/predict` - Detect intrusions from network traffic data

  # Commands 
## Create new venv
python -m venv venv

## Activate
venv\Scripts\activate

## Install dependencies
pip install -r requirements.txt

## Train model
python -m model.train

## Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
