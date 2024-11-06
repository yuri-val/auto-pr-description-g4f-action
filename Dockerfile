FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

CMD ["python", "/app/main.py"]
