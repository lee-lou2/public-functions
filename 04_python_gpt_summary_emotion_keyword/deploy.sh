docker stop docs
docker rm docs
docker build -t steamlit-docs/lou2 .
docker run --name docs -v ${PWD}:/app -w /app -d steamlit-docs/lou2 bash -c "streamlit run main.py --server.address=0.0.0.0 --server.port=80"