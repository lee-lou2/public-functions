import io

from PIL import Image
from fastapi import FastAPI, File, UploadFile
from transformers import AutoImageProcessor, AutoModel

app = FastAPI()

processor = AutoImageProcessor.from_pretrained("facebook/dinov2-large")
model = AutoModel.from_pretrained("facebook/dinov2-large")


@app.post("/embeddings/")
async def get_embeddings(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    embedding = outputs.pooler_output.detach().cpu().numpy().squeeze()
    return embedding.tolist()
