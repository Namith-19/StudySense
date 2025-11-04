# V2/application/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# system deps for opencv, pdf rendering etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    poppler-utils \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app
COPY . /app

EXPOSE 8501
ENV PYTHONUNBUFFERED=1

# Run Streamlit (ensure your entrypoint file is app.py in /app)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
