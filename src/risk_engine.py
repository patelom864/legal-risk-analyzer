# ────────────────  src/risk_engine.py  ────────────────
"""
Granite-powered clause-risk scorer for the Legal-Document Risk Analyzer.

• Loads Granite 3-3-8B Instruct once and re-uses it.
• Splits long contracts via chunk_document().
• Returns a list of risk-dicts with dollar impact and UUID.
"""

import os, re, json, uuid
from pathlib import Path
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Model          # SDK 1.3.x
from chunker import chunk_document                         # ← your splitter

# ── locate repo root & prompt template ──────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent
PROMPT_TMPL = (
    REPO_ROOT / "src" / "prompt_templates" / "risk_prompt.txt"
).read_text()

# ── load credentials from .env ─────────────────────────────────
load_dotenv(REPO_ROOT / ".env")
creds = Credentials(
    api_key = os.getenv("WX_API_KEY"),
    url     = "https://us-south.ml.cloud.ibm.com"
)

# ── Granite model handle (reuse across requests) ───────────────
granite = Model(
    model_id   = "ibm/granite-3-3-8b-instruct",
    credentials= creds,
    project_id = os.getenv("WX_PROJECT_ID")
)

# ── main scoring function ──────────────────────────────────────
def score_risk(
    text: str,
    contract_value: float = 100_000,
    factor: float = 0.0001,              # $-impact multiplier (slider-controlled)
) -> list[dict]:
    """
    Analyse contract text and return a list of risk objects.

    Args:
        text            – full contract text
        contract_value  – dollar value of contract (for impact calc)
        factor          – multiplier to convert score → USD

    Returns: list[dict] matching UI schema
    """
    risks: list[dict] = []

    for i, chunk in enumerate(chunk_document(text, max_tokens=2_000)):   # smaller chunks ⇒ richer output
        prompt = PROMPT_TMPL.replace("<<CLAUSE_BLOCK>>", chunk)

        resp = granite.generate_text(
            prompt = prompt,
            params = {
                "max_new_tokens": 1024,
                "temperature":    0.0,     # ← no randomness
                "top_p":          1.0,
                "random_seed":    42       # ← fixed seed
            },
            raw_response = True
        )


        raw_txt = resp["results"][0]["generated_text"]

        # ── DEBUG: print the JSON Granite returned for each chunk ─────
        print(f"\n--- DEBUG: chunk #{i} raw JSON ---\n{raw_txt}\n")

        # ── extract first JSON array / object from model output ──
        json_blocks = re.finditer(r'(\{.*?\}|\[.*?\])', raw_txt, re.S)
        for m in json_blocks:
            try:
                data = json.loads(m.group())
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                data = [data]
            # normalize any broken risk_type key variants
            for obj in data:
                # handle the stray “risk_” key
                if "risk_" in obj and "risk_type" not in obj:
                    obj["risk_type"] = obj.pop("risk_")
                # if you still see the mojibake version
                if "risk_Â­type" in obj:
                    obj["risk_type"] = obj.pop("risk_Â­type")


            for r in data:
                # skip any chunk that didn't return a score
                if "score" not in r:
                    continue

                r["impact_usd"] = round(r["score"] * factor * contract_value, 2)
                r["id"] = uuid.uuid4().hex
                risks.append(r)



    return risks
