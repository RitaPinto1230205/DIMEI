from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Servidor VoiceCRM a funcionar!"})

@app.route('/analyse', methods=['POST'])
def analyse():
    data = request.get_json()
    
    if not data or 'segments' not in data:
        return jsonify({"error": "Nenhum segmento recebido"}), 400
    
    segments = data['segments']
    
    # Por agora devolve os segmentos com um locutor fictício
    # Na próxima iteração aqui entra o pyannote!
    result_segments = []
    for i, seg in enumerate(segments):
        result_segments.append({
            "index": seg['index'],
            "text": seg['text'],
            "timestamp": seg['timestamp'],
            "speaker": "Locutor A" if i % 2 == 0 else "Locutor B"  # simulação simples
        })
    
    return jsonify({
        "status": "ok",
        "total_segments": len(segments),
        "segments": result_segments
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)