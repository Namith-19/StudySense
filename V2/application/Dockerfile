FROM python:3.11-slim

WORKDIR /app

# system deps for opencv etc.
RUN apt-get update && apt-get install -y build-essential ffmpeg libsm6 libxext6 ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8501
ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "app.py", "--server.port=8502", "--server.address=0.0.0.0"]
