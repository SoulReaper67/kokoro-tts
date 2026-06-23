FROM python:3.11-slim

# Installer espeak-ng avec les droits root
RUN apt-get update && apt-get install -y espeak-ng wget && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Télécharger les modèles Kokoro
RUN wget -q https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
RUN wget -q https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]