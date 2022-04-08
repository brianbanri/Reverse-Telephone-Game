# saved as greeting-client.py
import pyaudio
import wave

import Pyro4
import socket

import binascii

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "recordedFile.wav"
device_index = 2
audio = pyaudio.PyAudio()

serverhost = Pyro4.Proxy("PYRONAME:example.serverhost")    # use name server object lookup uri shortcut
b = serverhost.getAudio()

b = binascii.unhexlify(b.encode('utf-8'))

waveFile = wave.open("recordedFileFromByte.wav", 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b)
waveFile.close()

wf = wave.open("recordedFileFromByte.wav", 'rb')

p = pyaudio.PyAudio()
stream = p.open(
    format = p.get_format_from_width(wf.getsampwidth()),
    channels = wf.getnchannels(),
    rate = wf.getframerate(),
    output = True
)

data = wf.readframes(CHUNK)
while len(data) > 0:
    stream.write(data)
    data = wf.readframes(CHUNK)

stream.close()
p.terminate()
