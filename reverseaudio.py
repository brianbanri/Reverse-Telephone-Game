import audiofile
import pyaudio
import wave
from pydub import AudioSegment
from pydub.playback import play
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()


wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

af = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
 
# Create an interface to PortAudio
pa = pyaudio.PyAudio()
 
# Open a .Stream object to write the WAV file
# 'output = True' indicates that the
# sound will be played rather than
# recorded and opposite can be used for recording
stream = pa.open(format = pa.get_format_from_width(af.getsampwidth()),
                channels = af.getnchannels(),
                rate = af.getframerate(),
                output = True)
 
# Read data in chunks
rd_data = af.readframes(CHUNK)
 
# Play the sound by writing the audio
# data to the Stream using while loop
while rd_data != '':
    stream.write(rd_data)
    rd_data = af.readframes(CHUNK)
 
# Close and terminate the stream
stream.stop_stream()
stream.close()
pa.terminate()
