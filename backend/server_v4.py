from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyannote.core import Annotation, Segment
from pyannote.metrics.diarization import DiarizationErrorRate
from pydantic import BaseModel
import os
import json
from groq import Groq

app = FastAPI(title="VoiceCRM API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
from dotenv import load_dotenv
load_dotenv()
groq_client = Groq(api_key=os.getenv("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"))

@app.get("/health")
def health():
    return {"status": "ok", "message": "VoiceCRM backend ready for LLM integration"}

@app.post("/extract")
def extract(data: dict):
    """
    Recebe segmentos transcritos e extrai dados CRM via LLM.
    Input:  { segments: [{ speaker, text, timestamp }] }
    Output: { client_profile, products_mentioned, purchase_intent, follow_up_actions, summary }
    """

    segments = data.get("segments", [])

    if not segments:
        return {"error": "no segments provided"}

# junta todos os segmentos numa transcrição legível
    transcript = "\n".join([
        f"{seg['speaker']}: {seg['text']}"
        for seg in segments
    ])

# prompt que envia ao LLM
    prompt = f"""És um assistente especializado em retalho de luxo.
Analisa esta conversa entre um consultor e um cliente de uma loja de luxo e extrai informação relevante para o CRM.

CONVERSA:
{transcript}

Responde APENAS com um JSON válido com esta estrutura:
{{
    "client_profile": {{
        "gender": "",
        "age_range": "",
        "residence": "",
        "client_tier": "",
        "style_preferences": [],
        "fabric_preferences": [],
        "sizes": {{
            "clothing": "",
            "shoes": "",
            "other": ""
        }}
    }},
    "purchase_history": {{
        "products_owned": [],
        "estimated_spend": "",
        "purchase_frequency": ""
    }},
    "family_relations": [
        {{
            "relation": "",
            "name": "",
            "occasions": [],
            "preferences": []
        }}
    ],
    "memories": [
        {{
            "category": "",
            "content": "",
            "date_mentioned": ""
        }}
    ],
    "current_visit": {{
        "products_mentioned": [],
        "purchase_intent": "high/medium/low",
        "budget_range": "",
        "occasion": ""
    }},

    "follow_up_actions": [],
    "summary": ""
}}"""
    
# prompt que envia ao LLM
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1000
    )

    try:
        content = response.choices[0].message.content.strip()
        # remove markdown se o modelo devolver ```json ... ```
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content.strip())
    except json.JSONDecodeError:
        result = {"raw": response.choices[0].message.content}

    return result


# ── DER endpoint ──────────────────────────────────────────────────────────────

class DiarizationSegment(BaseModel):
    start: float
    end: float
    speaker: str


class DERRequest(BaseModel):
    reference: list[DiarizationSegment]
    hypothesis: list[DiarizationSegment]


@app.post("/der")
def calculate_der(req: DERRequest):

    reference = Annotation()
    for seg in req.reference:
        reference[Segment(seg.start, seg.end)] = seg.speaker

    hypothesis = Annotation()
    for seg in req.hypothesis:
        hypothesis[Segment(seg.start, seg.end)] = seg.speaker

    metric = DiarizationErrorRate()
    result = metric(reference, hypothesis)

    return {
        "der": round(float(result), 4),
        "der_percent": f"{result:.1%}"
    }