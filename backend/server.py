from flask import Flask, request, jsonify
from flask_cors import CORS
from pyannote.audio import Pipeline
import tempfile
import os

app = Flask(__name__)
CORS(app)

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token="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"  
)
print("Modelo carregado!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Servidor VoiceCRM com diarização real!"})

@app.route('/diarize', methods=['POST'])
def diarize():
    if 'audio' not in request.files:
        return jsonify({"error": "Nenhum ficheiro de áudio recebido"}), 400
    
    audio_file = request.files['audio']
    
    # Guarda temporariamente
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        # Diarização real com pyannote!
        diarization = pipeline(tmp_path)
        
        # Formata o resultado
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": round(turn.start, 2),
                "end": round(turn.end, 2),
                "speaker": speaker,
                "duration": round(turn.end - turn.start, 2)
            })
        
        return jsonify({
            "status": "ok",
            "total_segments": len(segments),
            "segments": segments
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.unlink(tmp_path)

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
        "total_segments": len(segments),
        "segments": result_segments
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
