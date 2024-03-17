FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update -y
RUN pip install -r requirements.txt

EXPOSE 80
