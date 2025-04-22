FROM python:3.12-slim

WORKDIR /app

# Установка зависимостей для Selenium + Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*


COPY etl/ etl/
COPY data/ data/
COPY logger/ logger/
COPY util/ util/

COPY requirements.txt .

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Устанавливаем путь к бинарнику Chromium
ENV CHROME_BIN=/usr/bin/chromium

# RUN apt-get update && apt-get install -y bash   # Для более удобной работы


CMD [ "sleep", "infinity" ]
