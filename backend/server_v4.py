from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyannote.core import Annotation, Segment
from pyannote.metrics.diarization import DiarizationErrorRate
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
from groq import Groq

load_dotenv()

app = FastAPI(title="VoiceCRM API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@app.get("/health")
def health():
    return {"status": "ok", "message": "VoiceCRM backend ready"}


@app.post("/extract")
def extract(data: dict):
    segments = data.get("segments", [])
    if not segments:
        return {"error": "no segments provided"}

    transcript = "\n".join([
        f"{seg['speaker']}: {seg['text']}"
        for seg in segments
    ])

    prompt = f"""You are a specialist assistant for luxury retafrom fastapi import FastAPI
from fastapi.middleware.cors ALfrom fastapi.middleware.co.
from pyannote.core import Annotation, Segment
frolifrom pyannote.metrics.diarization import Diaiefrom pydantic import BaseModel
from dotenv import load_doten",from dotenv import load_doten  import os
import json
from gr "import jeffrom groq []
load_dotenv()

app efe
app = FastA
  
app.add_middleware(
    CORSMiddleware,
    allo       CORshoes": "",
            "other":     allow_methods=["*"]      allow_headers=["*"]
 )

groq_client = Groq(a: [],

@app.get("/health")
def health():
    return {"staequedef health():
          return {at

@app.post("/extract")
def extract(data: dict):
    segments =me":def extract(data: dica    segments = data.get "    if not segments:
        return {" "        return       
    transcript = "\n".join([
        f"{seg['sten        f"{seg['speaker']}:en        for seg in segments
    ])

    pt_    ])

{{
        "products_mentionfrom fastapi.middleware.cors ALfrom fastapi.middleware.co.
from pyannote.core import Anno  from pyannote.core import Annotation, Segment
frolifrom psufrolifrom pyannote.metrics.diarization imporerfrom dotenv import load_doten",from dotenv import load_doten  import os
import jroimport json
from gr "import jeffrom groq []
load_dotenv()

app efe
app,
from gr "issload_dotenv()

app efe
app = Ft"
app efe
app   app = em  
app.add.1a
     CORSMiddleware20    allo       COR
             "other":     alloi )

groq_client = Groq(a: [],

@app.get("/health")
def health():
   
 
   
@app.get("/health")
def.spdef health():
          return {te          return {at

@app.post(       content = contentdef extract(data: di=     segments =me":def ep(        return {" "        return       
    transcript = "\n".join([
        f"{segsa    transcript = "\n".join([
        f"Di        f"{seg['sten       :
    ])

    pt_    ])

{{
        "products_mentionfrom fastapi.middleware.el
 
    r
{{
        st[ iafrom pyannote.core import Anno  from pyannote.core import Annotation, Segment
frolcafrolifrom psufrolifrom pyannote.metrics.diarization imporerfrom dotenv imporq.import jroimport json
from gr "import jeffrom groq []
load_dotenv()

app efe
app,
from gr "issload_dotenv()

app efe
app = Ft"
aesifrom gr "import jeffs[load_dotenv()

app efe
app,
f= seg.speaker

   app,
fc = Dia
app efe
app = Ft"
app eresapp = meapp efe
erapp   hyapp.add.1a
    re     CORS               "other":     alloi )

gro  
groq_client = Groq(a: [],

@app}"

   }
