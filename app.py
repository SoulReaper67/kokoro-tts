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
        audio_buffer = io.BytesIO()
        sample_rate = 24000
        first = True

        for chunk in chunks:
            samples, sr = kokoro.create(chunk, voice=voice, speed=speed)
            sample_rate = sr
            chunk_int16 = (samples * 32767).astype(np.int16)

            if first:
                sf.write(audio_buffer, chunk_int16, sample_rate, format='WAV', subtype='PCM_16')
                first = False
            else:
                # Ajoute juste les samples bruts après le header WAV
                audio_buffer.write(chunk_int16.tobytes())

            del samples, chunk_int16

        audio_buffer.seek(0)
        return send_file(audio_buffer, mimetype='audio/wav')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)