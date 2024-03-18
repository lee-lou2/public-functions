import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./config.json"

from google.cloud import texttospeech

# 클라이언트 초기화
client = texttospeech.TextToSpeechClient()

# 텍스트 입력 설정
synthesis_input = texttospeech.SynthesisInput(
    text="""
"""
)

# 음성 설정
voice = texttospeech.VoiceSelectionParams(language_code="ko-KR", name="ko-KR-Wavenet-D")

# 오디오 설정
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16, pitch=0, speaking_rate=1.2
)

# TTS 요청 및 응답
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# 음성 파일 저장
with open("output.wav", "wb") as out:
    out.write(response.audio_content)
    print("출력 완료")
