import json
import whisper_timestamped as whisper

audio = whisper.load_audio("test.mp3")

model = whisper.load_model("base", device="cpu")

result = whisper.transcribe(model, audio, language="ko")

print(json.dumps(result, indent=2, ensure_ascii=False))
