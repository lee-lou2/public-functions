docker stop epub
docker rm epub
docker build -t steamlit-epub/lou2 .
docker run --name epub -v ${PWD}:/app -w /app -d steamlit-epub/lou2 bash -c "streamlit run main.py --server.address=0.0.0.0 --server.port=80"