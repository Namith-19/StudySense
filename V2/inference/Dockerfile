FROM python:3.11-slim

WORKDIR /app

# system deps needed by many wheels (OpenCV, ffmpeg etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      libglib2.0-0 \
      libgl1 \
      libsm6 \
      libxext6 \
      libxrender1 \
      ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

# upgrade pip, setuptools and wheel first (critical)
RUN python -m pip install --upgrade pip setuptools wheel

# then install python deps
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/

# adjust command as needed:
CMD ["uvicorn", "mood_api:app", "--host", "0.0.0.0", "--port", "8000"]