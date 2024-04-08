import json
from openai import OpenAI
from dotenv import load_dotenv

# 토큰 정보로드
load_dotenv()

client = OpenAI()

audio_file = open("test4.mp3", "rb")
transcript = client.audio.transcriptions.create(
    file=audio_file,
    model="whisper-1",
    response_format="verbose_json",
    timestamp_granularities=["word", "segment"]
)

with open("data.json", "w", encoding="utf-8") as file:
    json.dump(transcript.dict(), file, ensure_ascii=False)
