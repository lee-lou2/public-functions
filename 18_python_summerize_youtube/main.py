from pytube import YouTube
from openai import OpenAI

# https://www.youtube.com/watch?v=J3VlVR2H0cw
video_url = input("유튜브 영상 URL을 입력하세요: ")

yt = YouTube(video_url)
audio_stream = yt.streams.filter(only_audio=True).first()
audio_stream.download(filename="audio.mp3")

client = OpenAI()

audio_file = open("audio.mp3", "rb")
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that summarizes transcripts in Korean."},
        {"role": "user", "content": f"""Please summarize the following English transcript in Korean:

{transcription.text}"""}
    ]
)

summary = response.choices[0].message.content
print(summary)
