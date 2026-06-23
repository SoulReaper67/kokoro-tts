from flask import Flask, request, send_file, jsonify
from kokoro_onnx import Kokoro
import soundfile as sf
import io
import os
import urllib.request

app = Flask(__name__)

# Chemins des modèles
MODEL_PATH = "kokoro-v1.0.onnx"
VOICES_PATH = "voices-v1.0.bin"
BASE_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"

# Téléchargement automatique si absents
if not os.path.exists(MODEL_PATH):
    print("Téléchargement du modèle ONNX...")
    urllib.request.urlretrieve(BASE_URL + MODEL_PATH, MODEL_PATH)
    print("Modèle téléchargé !")

if not os.path.exists(VOICES_PATH):
    print("Téléchargement des voix...")
    urllib.request.urlretrieve(BASE_URL + VOICES_PATH, VOICES_PATH)
    print("Voix téléchargées !")

kokoro = Kokoro(MODEL_PATH, VOICES_PATH)

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