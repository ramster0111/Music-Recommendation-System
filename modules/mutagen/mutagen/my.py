from mutagen.mp3 import MP3
from mutagen.id3 import ID3
audio = ID3("New_Soul.mp3")
print mp3info("New_Soul")

for i in  audio:
       print i,"    ",audio[i]
