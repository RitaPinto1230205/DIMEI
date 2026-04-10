"""
Testa o endpoint /diarize-segment com áudio sintético de dois locutores.
Requer o servidor a correr: uv run uvicorn server_v4:app --port 5003
"""
import io
import numpy as np
import requests
import torchaudio
import torch

SERVER = "http://localhost:5003"
SESSION = "test-session"


def make_wav(frequency: float, duration: float = 2.0, sample_rate: int = 16000) -> bytes:
    """Gera um tom sintético como WAV em memória."""
    t = torch.linspace(0, duration, int(sample_rate * duration))
    wave = (torch.sin(2 * torch.pi * frequency * t) * 0.5).unsqueeze(0)
    buf = io.BytesIO()
    torchaudio.save(buf, wave, sample_rate, format="wav")
    buf.seek(0)
    return buf.read()


def send_segment(wav_bytes: bytes, index: int, text: str) -> dict:
    resp = requests.post(
        f"{SERVER}/diarize-segment",
        params={"session_id": SESSION, "index": index, "text": text},
        files={"audio": ("segment.wav", wav_bytes, "audio/wav")},
    )
    resp.raise_for_status()
    return resp.json()


def test_health():
    r = requests.get(f"{SERVER}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    print("✅ /health OK")


def test_two_speakers_identified():
    # Reset sessão
    requests.post(f"{SERVER}/reset", params={"session_id": SESSION})

    # Locutor A — voz grave (120 Hz)
    speaker_a_wav = make_wav(frequency=120.0)
    # Locutor B — voz aguda (250 Hz)
    speaker_b_wav = make_wav(frequency=250.0)

    results = []

    # Alterna A, B, A, B
    for i, (wav, label) in enumerate([
        (speaker_a_wav, "A"),
        (speaker_b_wav, "B"),
        (speaker_a_wav, "A"),
        (speaker_b_wav, "B"),
    ]):
        r = send_segment(wav, index=i + 1, text=f"Fala do locutor {label}")
        print(f"  Segmento {i+1} (esperado {label}): {r['speaker']}  score={r.get('score', '-'):.3f}")
        results.append(r["speaker"])

    # Os segmentos 1 e 3 devem ser o mesmo locutor
    assert results[0] == results[2], f"Segmentos 1 e 3 deviam ser iguais: {results[0]} vs {results[2]}"
    # Os segmentos 2 e 4 devem ser o mesmo locutor
    assert results[1] == results[3], f"Segmentos 2 e 4 deviam ser iguais: {results[1]} vs {results[3]}"
    # Os dois locutores devem ser diferentes
    assert results[0] != results[1], "Locutores A e B deviam ser diferentes"

    print("✅ Dois locutores identificados corretamente!")


def test_reset():
    requests.post(f"{SERVER}/reset", params={"session_id": SESSION})
    # Após reset, o mesmo áudio deve voltar a ser "Locutor A"
    wav = make_wav(frequency=120.0)
    r = send_segment(wav, index=1, text="Primeiro segmento após reset")
    assert r["speaker"] == "Locutor A"
    print("✅ Reset funciona!")


if __name__ == "__main__":
    print(f"A testar servidor em {SERVER}...\n")
    test_health()
    test_two_speakers_identified()
    test_reset()
    print("\n🎉 Todos os testes passaram!")
