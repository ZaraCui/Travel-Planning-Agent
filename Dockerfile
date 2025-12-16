FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# install python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

EXPOSE 8000

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "--timeout", "60"]
