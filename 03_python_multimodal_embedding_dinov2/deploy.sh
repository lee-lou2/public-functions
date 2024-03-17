#!/bin/bash
docker stop api_embeddings
docker rm api_embeddings
docker run -p 8000:8000 --name api_embeddings -v ${PWD}:/app -w /app -d --restart=always python:3.11-slim bash -c "pip install -U pip && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000"
