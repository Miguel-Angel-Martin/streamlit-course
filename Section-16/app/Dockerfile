FROM python:3.13-slim

WORKDIR /app

# Instala netcat
RUN apt-get update && apt-get install -y nano netcat-openbsd curl wget vim git && rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
