from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
