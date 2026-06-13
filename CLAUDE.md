# VoiceCRM

iOS app de CRM por voz para retalho de luxo — dissertação de mestrado ISEP 2026.

Grava conversas entre consultor e cliente, transcreve em português europeu via SFSpeechRecognizer, faz diarização de locutores via FluidAudio, e extrai dados CRM estruturados via LLM (Llama 4 Scout no Groq).

---

## Arquitectura

```
iPhone (SwiftUI)
    │
    │  POST /analyse  →  transcrição + segmentos de áudio
    │  POST /crm      →  extração CRM via LLM
    │  POST /der      →  cálculo DER (avaliação)
    ▼
Python FastAPI (server_v4.py · porta 5003)
    │
    ├── FluidAudio  →  diarização de locutores
    ├── Groq API    →  Llama 4 Scout (extração CRM)
    └── pyannote    →  cálculo DER
```

---

## ⚠️ Antes de arrancar — actualizar o IP

O IP do Mac está hardcoded no iOS. **Sempre que mudares de rede, actualiza este valor.**

**Ficheiro:** `VoiceCRM/VoiceCRM/ContentView.swift` linha ~228

```swift
// Muda para o IP actual do teu Mac na rede local
let serverURL = URL(string: "http://192.168.1.105:5003/analyse")!
```

Para saber o IP actual do Mac:

```bash
ipconfig getifaddr en0
```

---

## Backend — arrancar o servidor

### Requisitos
- Python 3.11
- [UV](https://astral.sh/uv) (gestor de dependências)
- Conta Groq com API key

### 1. Instalar UV (só uma vez)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Configurar variáveis de ambiente

Cria um ficheiro `.env` na pasta `backend/`:

```bash
cd backend
cp .env.example .env   # se existir, ou cria manualmente
```

Conteúdo do `.env`:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Instalar dependências e arrancar

```bash
cd backend
uv venv --python 3.11   # só na primeira vez
uv sync                  # instala dependências do pyproject.toml
uv run python server_v4.py
```

O servidor fica disponível em `http://0.0.0.0:5003`.

### Verificar que está a correr

```bash
curl http://localhost:5003/health
```

Resposta esperada:
```json
{ "status": "ok", "device": "mps", "model": "llama-4-scout-17b" }
```

### Notas técnicas
- O backend usa `torch.device("mps")` — **só funciona em Mac M1/M2**. Em Intel Mac, muda para `"cpu"` em `server_v4.py`.
- O modelo FluidAudio é descarregado do HuggingFace na primeira execução (~alguns GB). Fica em cache em `~/.cache/huggingface/`.

---

## iOS — arrancar a app

1. Abre `VoiceCRM/VoiceCRM.xcodeproj` no Xcode
2. **Actualiza o IP** conforme descrito acima
3. Liga um iPhone físico (o simulador não suporta microfone)
4. Build & Run (`⌘R`)

Permissões necessárias (já configuradas no `Info.plist`):
- Microfone
- Reconhecimento de voz

O reconhecedor está configurado para `pt-PT` (português europeu).

---

## API — endpoints principais

### `POST /analyse`
Recebe segmentos de áudio transcritos, devolve com identificação de locutores.

```json
// Request
{
  "segments": [
    { "index": 1, "text": "Bom dia, em que posso ajudá-lo?", "timestamp": "10:32:01" }
  ]
}

// Response
{
  "status": "ok",
  "segments": [
    { "index": 1, "text": "Bom dia, em que posso ajudá-lo?", "timestamp": "10:32:01", "speaker": "Consultor" }
  ]
}
```

### `POST /crm`
Extrai dados CRM estruturados da conversa via LLM.

```json
// Request
{
  "transcript": "Consultor: Bom dia...\nCliente: Preciso de..."
}

// Response
{
  "client_profile": { "gender": "feminino", "residence": "Lisboa", ... },
  "current_visit": { "occasion": "gala", "budget_range": "€2000", ... },
  "follow_up_actions": [ "enviar propostas por email" ]
}
```

### `POST /der`
Calcula Diarization Error Rate (usado na avaliação da dissertação).

### `GET /health`
Devolve estado do servidor, device (mps/cpu) e modelo activo.

---

## Estrutura do projecto

```
VoiceCRM/
├── VoiceCRM.xcodeproj
└── VoiceCRM/
    └── ContentView.swift      ← actualizar IP aqui (linha ~228)

backend/
├── server_v4.py               ← entry point, porta 5003
├── pyproject.toml
├── uv.lock
├── .env                       ← GROQ_API_KEY (não commitar)
│
├── eval/                      ← avaliação comparativa de modelos LLM
│   ├── eval_crm.py
│   ├── eval_modelos.py
│   ├── dataset_eval_voicecrm.json
│   ├── dataset_golden_v3.json
│   └── results/
│       └── eval_results_*.json
│
├── metrics/                   ← scripts WER e DER por sessão
│   ├── calc_der.py
│   ├── calc_wer_r01.py
│   └── ...calc_wer_r12.py
│
└── tests/
    ├── test_moshi.py
    ├── test_mps.py
    └── test_resemblyzer.py
```

---

## Checklist — sessão de trabalho típica

```
□ ipconfig getifaddr en0          → ver IP actual do Mac
□ Actualizar IP em ContentView.swift
□ cd backend && uv run python server_v4.py
□ curl http://localhost:5003/health   → confirmar que arrancou
□ Xcode → Build & Run no iPhone
```

---

## Dependências principais

| Pacote | Versão | Para quê |
|---|---|---|
| fastapi | ≥0.110 | servidor HTTP |
| uvicorn | ≥0.29 | ASGI runner |
| groq | ≥0.5 | API Llama 4 Scout |
| torch | ≥2.2 | FluidAudio / MPS |
| pyannote.audio | ≥3.1 | cálculo DER |
| python-dotenv | ≥1.0 | variáveis de ambiente |

Geridas via `pyproject.toml` — instalar com `uv sync`.

---

## Problemas frequentes

**`Connection refused` no iPhone**
→ IP desactualizado. Corre `ipconfig getifaddr en0` e actualiza `ContentView.swift`.

**`GROQ_API_KEY not set`**
→ Falta o ficheiro `.env` em `backend/`. Ver secção de configuração acima.

**Servidor arranca mas diarização falha**
→ Modelo FluidAudio ainda a descarregar. Aguarda e tenta de novo.

**`MPS backend not available`**
→ Estás num Mac Intel. Muda `"mps"` para `"cpu"` em `server_v4.py`.