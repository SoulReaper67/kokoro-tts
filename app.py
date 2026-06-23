from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from kokoro_onnx import Kokoro
import soundfile as sf
import numpy as np
import io
import os
import re

app = Flask(__name__)
CORS(app)

kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")

def split_text(text, max_chars=80):
    """Découpe le texte en phrases courtes"""
    phrases = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current = ""
    for phrase in phrases:
        if len(current) + len(phrase) <= max_chars:
            current += " " + phrase
        else:
            if current:
                chunks.append(current.strip())
            current = phrase
    if current:
        chunks.append(current.strip())
    return chunks if chunks else [text]

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "Kokoro TTS opérationnel"})

@app.route('/synthesize', methods=['POST'])
def synthesize():
    try:
        data = request.get_json()
        text = data.get('text', '')
        voice = data.get('voice', 'ff_siwis')
        speed = data.get('speed', 1.0)

        if not text:
            return jsonify({"error": "Texte manquant"}), 400

        chunks = split_text(text)
        all_audio = []
        sample_rate = 24000

        for chunk in chunks:
            samples, sr = kokoro.create(chunk, voice=voice, speed=speed)
            all_audio.append(samples)
            sample_rate = sr

        # Assemble tous les morceaux
        final_audio = np.concatenate(all_audio)

        # Convertir en int16 pour économiser la RAM
        final_audio_int16 = (final_audio * 32767).astype(np.int16)

        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, final_audio_int16, sample_rate, format='WAV', subtype='PCM_16')
        audio_buffer.seek(0)

        return send_file(audio_buffer, mimetype='audio/wav')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)