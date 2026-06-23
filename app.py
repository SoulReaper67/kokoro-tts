from flask import Flask, request, send_file, jsonify
from flask_cors import CORS  # ← ajoute ça
from kokoro_onnx import Kokoro
import soundfile as sf
import io
import os
import urllib.request

app = Flask(__name__)
CORS(app)  # ← et ça

# ... reste du code identique