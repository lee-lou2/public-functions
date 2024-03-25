import datetime
import os
import time

from dotenv import load_dotenv

# 토큰 정보로드
load_dotenv()

from openai import OpenAI

print(datetime.datetime.now())
start_time = time.time()
client = OpenAI()

# 전체 음성파일에 대한 트래스크립트 생성
renamed_file = "test.MP3"

from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence


# files
src = renamed_file
dst = renamed_file[:-4] + ".wav"

# # convert wav to mp3
# audSeg = AudioSegment.from_mp3(src)
# audSeg.export(dst, format="wav")

# 오디오 파일 불러오기
audio = AudioSegment.from_file(dst, format="wav")

min_silence_len = 500  # 무음으로 간주될 최소 길이 (밀리초 단위)
silence_thresh = -50  # 무음으로 간주될 데시벨 값

# 무음 부분을 기준으로 오디오 분할
chunks = split_on_silence(
    audio,
    min_silence_len=min_silence_len,  # 무음으로 간주될 최소 길이 (밀리초 단위)
    silence_thresh=silence_thresh,  # 무음으로 간주될 데시벨 값
    keep_silence=0,
)
print(len(chunks))

# for i, chunk in enumerate(chunks):
#     # 잘려진 파일 저장
#     chunk_file = f"chunk_{i}.wav"
#     chunk.export(chunk_file, format="wav")
#
#     # 파일 용량 확인
#     file_size = os.path.getsize(chunk_file)
#     print(f"Chunk {i} file size: {file_size} bytes")
#
#     # 음성 길이 확인
#     duration_ms = len(chunk)
#     duration_sec = duration_ms / 1000
#     print(f"Chunk {i} duration: {duration_sec:.2f} seconds")

silences = detect_silence(
    audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh
)
silences_diff = [s[1] - s[0] for s in silences]

output = chunks[0]
output += audio[silences[0][0] : silences[0][1]]
for i in range(1, 11):
    output += chunks[i]
    output += audio[silences[i][0] : silences[i][1]]

from tqdm import tqdm

# 분할된 각 청크를 파일로 저장 (예시)
current_duration = 0.0
timeline = []
transcripts = []

for i, chunk in tqdm(enumerate(chunks), total=len(chunks)):
    f_name = "sample/chunk{i}.wav"
    chunk.export(f_name, format="wav")
    try:
        transcript = client.audio.transcriptions.create(
            file=open(f_name, "rb"),
            model="whisper-1",
            language="ko",
            response_format="text",
            temperature=0.0,
        )
    except:
        transcript = ""

    start = current_duration
    if i < len(silences_diff):
        end = current_duration + chunk.duration_seconds * \
            1000 + silences_diff[i]
    else:
        end = current_duration + chunk.duration_seconds * 1000

    print(int(start), int(end))
    timeline.append((start, end))
    current_duration = end
    transcripts.append(transcript)

def format_time(ms):
    """밀리초를 SRT 포맷의 시간 문자열로 변환합니다."""
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"


def create_srt(chunks, subtitles, filename):
    """SRT 파일을 생성합니다."""
    with open(filename, "w") as file:
        combined = [
            (start, end, text) for (start, end), text in zip(timeline, transcripts)
        ]
        for i, (start, end, text) in enumerate(combined, start=1):
            file.write(f"{i}\n")
            file.write(f"{format_time(start)} --> {format_time(end)}\n")
            file.write(f"{text}\n\n")


# SRT 파일 생성
create_srt(timeline, transcripts, "subtitles.srt")

print("Done!")
end = time.time()
print(end - start_time)
