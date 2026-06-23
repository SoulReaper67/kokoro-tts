from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from kokoro_onnx import Kokoro
import soundfile as sf
import io
import os

app = Flask(__name__)
CORS(app)

kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "Kokoro TTS opérationnel"})

@app.route('/synthesize', methods=['POST'])
def synthesize():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({"error": "Texte manquant"}), 400
        samples, sample_rate = kokoro.create(text, voice="ff_siwis", speed=1.0, lang="fr")
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, samples, sample_rate, format='WAV')
        audio_buffer.seek(0)
        return send_file(audio_buffer, mimetype='audio/wav')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)