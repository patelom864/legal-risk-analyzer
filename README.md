# Legal Risk Analyzer

A small Streamlit app that scores risky clauses in contracts using **IBM watsonx Granite**. It was scaffolded for an IBM 2025 hackathon.

## How it works

- **Upload and parsing.** Upload a PDF or DOCX. Text is extracted with `pypdf` or `python-docx`, then cleaned for mojibake with a custom map plus `ftfy`.
- **Chunking.** Long text is split into word chunks with `chunk_document`.
- **Prompted LLM call.** Each chunk is sent to **Granite 3-3-8B Instruct** via the `ibm-watsonx-ai` SDK with a strict JSON-only prompt. Temperature 0, fixed seed 42.
- **Post-processing.** The app finds the first JSON object or array in the model output, normalizes key names, and computes a dollar impact per clause:

  ```impact_usd = score * factor * contract_value```

- **UI.** Risk items are shown as expandable cards sorted by score. A CSV download is offered. You can tune an impact factor slider and set contract value.

## Files to know

- `src/streamlit_app.py` — Streamlit front end  
- `src/extract_text.py` — PDF and DOCX extraction plus Unicode cleanup  
- `src/chunker.py` — simple word based splitter  
- `src/risk_engine.py` — Granite client, scoring loop, JSON parse, impact calculation  
- `src/prompt_templates/risk_prompt.txt` — JSON only instruction with few-shot examples  
- `quick_test.py` — sanity check for watsonx credentials and model visibility  
- `requirements.txt` — core deps: `ibm-watsonx-ai`, `pypdf`, `python-docx`, `faiss-cpu`, `streamlit`, `ftfy`, `python-dotenv`  
- `Makefile` — `make streamlit` runs the app, `make test` runs pytest

## Setup and run

1. Create `.env` with your watsonx credentials:

   ```
   WX_API_KEY=...
   WX_PROJECT_ID=...
    ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Verify Granite access:
    ```
    python quick_test.py
    ```

6. Start the UI:
   ```
   make streamlit
   # or:
   streamlit run src/streamlit_app.py
   ```
