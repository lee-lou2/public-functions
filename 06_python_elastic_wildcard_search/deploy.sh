docker stop doctor_keyword
docker rm doctor_keyword
docker run --name doctor_keyword --restart=always --expose=80 -v ${PWD}:/app -w /app -d python:3.11-slim bash -c "pip install -U pip && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 80"