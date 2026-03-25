# VoiceCRM — Project Context for Claude

## What this project is

A thesis project (TESE) — an iOS app that records speech, segments it by silence, transcribes it via Apple's SpeechRecognizer, and sends segments to a Python backend for speaker diarization. The goal is a Voice CRM that identifies who said what in a conversation.

## Architecture

```
iPhone (SwiftUI) ──POST /analyse──> Python Flask backend ──> speaker diarization model
```

- **iOS frontend**: `VoiceCRM/VoiceCRM/ContentView.swift` — SwiftUI app, records audio, uses `SFSpeechRecognizer` (pt-PT locale), segments speech on 1.5s silence, sends segments to backend
- **Backend (active)**: `backend/server_moshi.py` — Flask on port 5002, loads Moshi model (`kyutai/moshiko-pytorch-bf16`) from HuggingFace, uses Apple MPS (M1 GPU)
- **Backend (old)**: `backend/server.py` — Flask on port 5001, used `pyannote/speaker-diarization-3.1`, now replaced by Moshi

## Backend setup

Managed with **UV**. Python 3.11, venv at `backend/.venv`.

```bash
# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install dependencies
cd backend
uv venv --python 3.11
uv sync

# Run the active server
uv run python server_moshi.py

# Add a dependency
uv add <package>
```

Dependencies are declared in `backend/pyproject.toml`. The old `backend/venv/` folder (pip-managed) can be deleted.

## Running the backend

```bash
cd backend
uv run python server_moshi.py
# Server starts on http://0.0.0.0:5002
```

Check health: `curl http://localhost:5002/health`

## iOS ↔ Backend connection

The iOS app hardcodes the server IP in `ContentView.swift:228`:
```swift
let serverURL = URL(string: "http://192.168.1.105:5001/analyse")!
```
**Update this IP** to match the Mac's local IP whenever the network changes. Also note the port — `server_moshi.py` runs on **5002**, but the Swift code still points to **5001** (needs updating).

## API

### POST /analyse
Receives speech segments from the iPhone, returns them with speaker labels.

Request:
```json
{
  "segments": [
    { "index": 1, "text": "Olá, como estás?", "timestamp": "14:32:01" }
  ]
}
```

Response:
```json
{
  "status": "ok",
  "model": "moshi",
  "device": "mps",
  "segments": [
    { "index": 1, "text": "...", "timestamp": "...", "speaker": "Locutor A" }
  ]
}
```

### GET /health
Returns server status and device (mps/cpu).

## Key technical notes

- **MPS device**: Backend uses `torch.device("mps")` — M1/M2 Mac only. On Intel Macs, change to `"cpu"`.
- **Model loading**: Moshi model is downloaded from HuggingFace on first run (~several GB). Cached in `~/.cache/huggingface/`.
- **Speaker diarization**: Currently a stub (alternates A/B by index). Real Moshi diarization is not yet wired up.
- **Speech language**: iOS recognizer is set to `pt-PT` (European Portuguese).
- **Silence threshold**: 1.5 seconds of silence triggers a new segment (`silenceThreshold` in ContentView).

## iOS project

Xcode project at `VoiceCRM/VoiceCRM.xcodeproj`. Open with Xcode, build and run on a real iPhone (microphone required — simulator won't work for audio).

Required permissions (already in Info.plist): microphone, speech recognition.
