# TCET FE Knowledge Base Bot (Flask)

This project runs a document-based FAQ chatbot using content from `TCET_FE_faq.docx`.

## Quick Start
If your environment is already set up, run these commands:

```powershell
.\.venv\Scripts\Activate.ps1
python build_kb.py --docx TCET_FE_faq.docx --out artifacts
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## What It Does
- Extracts FAQ entries from DOCX (paragraphs and tables)
- Trains a TF-IDF retrieval model on FAQ questions
- Writes model artifacts to `artifacts/`
- Serves a chatbot web UI and API with Flask

## Project Structure
- `build_kb.py`: retrains and saves the knowledge base
- `kb_engine.py`: DOCX parsing, retrieval, validation logic
- `app.py`: Flask server (UI + API)
- `templates/index.html`: chatbot UI page
- `static/style.css`: UI styles
- `static/app.js`: browser chat logic
- `artifacts/model.pkl`: trained model
- `artifacts/validation_report.json`: build metrics

## Prerequisites
- Python 3.10+
- pip

## First-Time Setup
1. Open a terminal in the project root.
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
3. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Daily Operation

### 1) Retrain the Knowledge Base
Run this whenever `TCET_FE_faq.docx` changes.

```powershell
python build_kb.py --docx TCET_FE_faq.docx --out artifacts
```

Expected output includes:
- `Knowledge base built with <count> FAQ entries.`
- `Validation report: artifacts\validation_report.json`

### 2) Start the Application
```powershell
python app.py
```

When started, Flask prints URLs such as:
- `http://127.0.0.1:5000`

Open that URL in your browser to use the chatbot.

### 3) Verify Health (Optional)
In a new terminal:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/health -Method Get
```

Expected response shape:
```json
{
  "status": "ok",
  "faq_count": 129
}
```

### 4) Test a Question via API (Optional)
```powershell
$body = @{ question = 'What is the role of EDIC in TCET?' } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/ask -Method Post -ContentType 'application/json' -Body $body
```

## API Endpoints
- `GET /api/health`: app/model health check
- `POST /api/ask`: ask a question
  - Body: `{ "question": "<your question>" }`
  - Response: `answer`, `confidence`, `source_question`

## Stopping the App
- In the terminal running Flask, press `Ctrl+C`.

## Common Issues
- `Source document missing`:
  - Ensure `TCET_FE_faq.docx` exists in the project root.
- `ModuleNotFoundError`:
  - Activate `.venv` and run `pip install -r requirements.txt` again.
- Low-confidence or wrong answers:
  - Retrain after updating the DOCX.
  - Rephrase questions closer to FAQ wording.

## Notes
- `app.py` will auto-load `artifacts/model.pkl` if present.
- If the model does not exist, `app.py` can train from `TCET_FE_faq.docx` on startup.
