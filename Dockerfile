FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/production_logs reports

EXPOSE 8501

CMD [ "python", "-m", "streamlit", "run", "src.dashboard.py", "--server.port=8501", "--server.address=0.0.0.0" ]