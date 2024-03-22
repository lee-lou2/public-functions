import pprint
from openai import OpenAI


client = OpenAI()

audio_file = open("test.mp3", "rb")
transcript = client.audio.transcriptions.create(
  file=audio_file,
  model="whisper-1",
  response_format="verbose_json",
  timestamp_granularities=["word", "segment"]
)

pprint.pprint(transcript.dict())
