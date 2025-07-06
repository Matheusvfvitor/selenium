FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo

# Instala dependências
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    xdg-utils \
    procps \
    cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instala Google Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    cron \
    procps \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cria arquivo de cron para rodar diariamente às 6h
RUN echo "0 6 * * * root python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/daily-job && \
    chmod 0644 /etc/cron.d/daily-job && \
    crontab /etc/cron.d/daily-job && \
    touch /var/log/cron.log

# Roda cron e loga a saída
CMD cron && tail -f /var/log/cron.log
