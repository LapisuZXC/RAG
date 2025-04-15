FROM python:3.12-slim

WORKDIR /app

COPY etl/ etl/
COPY data/ data/
COPY logger/ logger/
COPY util/ util/

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# RUN apt-get update && apt-get install -y bash   # Для более удобной работы


CMD [ "sleep", "infinity" ]