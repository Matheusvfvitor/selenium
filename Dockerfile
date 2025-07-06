FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo

# Instala cron e dependências do sistema
RUN apt-get update && apt-get install -y \
    cron \
    wget \
    curl \
    unzip \
    gnupg \
    ca-certificates \
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
    procps && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia dependências Python e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do app
COPY . .

# Cria o cronjob para rodar diariamente às 6h
RUN echo "0 6 * * * root python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/daily-job && \
    chmod 0644 /etc/cron.d/daily-job && \
    touch /var/log/cron.log

# Inicia cron e mostra os logs
CMD ["/bin/bash", "-c", "cron && tail -f /var/log/cron.log"]
