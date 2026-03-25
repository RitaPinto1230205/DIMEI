from flask import Flask, request, jsonify
from flask_cors import CORS
from moshi.models import loaders
import torch
import tempfile
import os

app = Flask(__name__)
CORS(app)

# Usa GPU M1
device = torch.device("mps")
print(f"A usar device: {device}")

print("A carregar modelo Moshi...")
moshi_weight = loaders.hf_hub_download(
    repo_id='kyutai/moshiko-pytorch-bf16',
    filename='model.safetensors'
)
print("✅ Modelo Moshi carregado!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "message": "Servidor Moshi a funcionar!",
        "device": str(device)
    })

@app.route('/analyse', methods=['POST'])
def analyse():
    data = request.get_json()
    if not data or 'segments' not in data:
        return jsonify({"error": "Nenhum segmento recebido"}), 400

    segments = data['segments']
    result_segments = []
    for i, seg in enumerate(segments):
        result_segments.append({
            "index": seg['index'],
            "text": seg['text'],
            "timestamp": seg['timestamp'],
            "speaker": "Locutor A" if i % 2 == 0 else "Locutor B"
        })

    return jsonify({
        "status": "ok",
        "model": "moshi",
        "device": str(device),
        "segments": result_segments
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)