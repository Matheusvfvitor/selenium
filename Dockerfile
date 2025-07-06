FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Instala cron + Python
RUN apt-get update && \
    apt-get install -y cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Define diretório do projeto
WORKDIR /app

# Copia arquivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Cria um arquivo de cron separado e instala ele
RUN echo "0 6 * * * root python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/daily-job \
    && chmod 0644 /etc/cron.d/daily-job \
    && crontab /etc/cron.d/daily-job

# Garante que o log exista
RUN touch /var/log/cron.log

# Comando final: start cron e mostra log
CMD cron && tail -f /var/log/cron.log
