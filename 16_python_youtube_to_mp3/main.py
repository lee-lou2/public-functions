from pytube import YouTube
import os

# 유튜브 링크
link = "https://youtu.be/mC2b57u_s0k?si=BNdXsU9EPZNqSkzS"

yt = YouTube(link)
filename = yt.streams.filter(only_audio=True).first().download()
renamed_file = filename.replace(".mp4", ".mp3")
os.rename(filename, renamed_file)
