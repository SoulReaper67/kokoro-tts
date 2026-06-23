from flask import Flask, request, send_file, jsonify
from kokoro import KPipeline
import soundfile as sf
import io
import os

app = Flask(__name__)

# Chargement du modèle au démarrage
pipeline = KPipeline(lang_code='fr')

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

        audio_buffer = io.BytesIO()
        for _, _, audio in pipeline(text, voice='ff_siwis'):
            sf.write(audio_buffer, audio, 24000, format='WAV')

        audio_buffer.seek(0)
        return send_file(
            audio_buffer,
            mimetype='audio/wav',
            as_attachment=False
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)