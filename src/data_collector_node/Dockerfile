FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV HDFS_HOST=hdfs
ENV HEARTBEAT_INTERVAL=60

CMD ["python", "main.py"]