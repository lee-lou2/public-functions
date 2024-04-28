import time

import speech_recognition as sr
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play

OPENAI_API_KEY = ""
client = OpenAI(api_key=OPENAI_API_KEY)


def tts(text):
    """텍스트를 음성으로 변환"""
    response = client.audio.speech.create(model="tts-1", voice="alloy", input=text)
    response.stream_to_file("output.mp3")
    song = AudioSegment.from_file("output.mp3", format="mp3")
    play(song)


def stt():
    """음성을 텍스트로 변환"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source, timeout=10, phrase_time_limit=30)
        return r.recognize_whisper_api(audio, api_key=OPENAI_API_KEY)


def conversation(message: str):
    """AI 와 대화"""
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    while True:
        print("🎙️ 녹음을 시작합니다")
        text = stt()
        if text:
            print("👨 사용자 질문 : ", text)
            answer = conversation(text)
            print("🤖 ChatGPT 답변 : ", answer)
            tts(conversation(text))
        else:
            print("👨 사용자 질문가 없습니다")
            time.sleep(1)
