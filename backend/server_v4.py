from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyannote.core import Annotation, Segment
from pyannote.metrics.diarization import DiarizationErrorRate
from pydantic import BaseModel
from dotenv import load_dotenv
import os, json
from groq import Groq

app = FastAPI(title="VoiceCRM API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def clean_crm_json(data: dict) -> dict:
    """Garante que strings vazias e 'desconhecido' viram null e arrays estão corretos."""
    
    UNKNOWN_VALUES = {"desconhecido", "unknown", "n/a", "não disponível", "não mencionado", ""}
    
    def clean_value(v):
        if isinstance(v, str):
            stripped = v.strip()
            return None if stripped.lower() in UNKNOWN_VALUES else stripped
        if isinstance(v, int) or isinstance(v, float):
            return str(int(v)) 
        if isinstance(v, list):
            return [clean_value(i) for i in v if i not in ("", None, [])] or None
        if isinstance(v, dict):
            if all(isinstance(val, (int, float)) for val in v.values()):
                return ", ".join(f"{k}: {val}€" for k, val in v.items())
            return clean_crm_json(v)
        return v
    
    return {k: clean_value(v) for k, v in data.items()}

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
        "gender": null,
        "age_range": null,
        "residence": null,
        "client_tier": null,
        "style_preferences": [],
        "fabric_preferences": [],
        "sizes": {{"clothing": null, "shoes": null, "other": null}}
    }},
    "purchase_history": {{
        "products_owned": [],
        "estimated_spend": null,
        "purchase_frequency": null
    }},
    "family_relations": [],
    "memories": [],
    "current_visit": {{
        "products_mentioned": [],
        "purchase_intent": "high/medium/low",
        "budget_range": null,
        "occasion": null
    }},
    "follow_up_actions": [],
    "summary": "resumo obrigatório em português europeu, 50-100 palavras"
}}
    
 REGRAS:
- gender: "masculino" ou "feminino" em português europeu, nunca "male" ou "female"
- usa null para campos sem informação, nunca strings vazias ou "desconhecido"
- tamanhos sempre em números ("38", "43"), nunca por extenso
- follow_up_actions: lista de strings simples e accionáveis
- family_relations: lista de objectos com campos: relation, name, occasions, preferences
- purchase_intent: apenas "high", "medium" ou "low" em inglês
- budget_range: sempre uma string simples como "300-2000€" ou "até 500€", nunca um objecto JSON
- sizes.other: sempre uma string simples como "cinto: 92" ou null, nunca um objecto JSON
- O campo summary é OBRIGATÓRIO — escreve sempre um resumo em português europeu entre 50 e 100 palavras, mencionando o perfil do cliente, os produtos discutidos e as acções de seguimento
- Responde APENAS com JSON, sem markdown, sem texto adicional"""

# prompt que envia ao LLM
    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2000
    )

    try:
        content = response.choices[0].message.content.strip()
        # remove markdown se o modelo devolver ```json ... ```
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content.strip())
        result = clean_crm_json(result)
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
