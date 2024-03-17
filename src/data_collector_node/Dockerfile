FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENV redis_host=redis
ENV redis_port=6379

CMD ["python", "main.py"]