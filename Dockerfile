FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Instala cron e python
RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cria cron job: executa script todo dia às 6h
RUN echo "0 6 * * * python /app/main.py >> /var/log/cron.log 2>&1" >> /etc/crontab

# Executa o cron no foreground para manter o container ativo
CMD ["cron", "-f"]
