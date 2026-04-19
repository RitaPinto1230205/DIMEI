from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyannote.core import Annotation, Segment
from pyannote.metrics.diarization import DiarizationErrorRate
from pydantic import BaseModel

app = FastAPI(title="VoiceCRM API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "message": "VoiceCRM backend ready for LLM integration"}


# LLM endpoint — to be implemented
@app.post("/extract")
def extract(data: dict):
    """
    Receives diarized transcript segments and extracts CRM insights via LLM.
    Input:  { segments: [{ speaker, text, timestamp }] }
    Output: { summary, action_items, sentiment }
    """
    return {"status": "not_implemented"}


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
    """
    Calcula o Diarization Error Rate (DER).
    Input:  { reference: [{start, end, speaker}], hypothesis: [{start, end, speaker}] }
    Output: { der: 0.123, der_percent: "12.3%" }
    """
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