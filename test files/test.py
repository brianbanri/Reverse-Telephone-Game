
import pyaudio
import wave

import Pyro4
import os
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

wf = wave.open("recordedFile.wav", 'rb')

data = wf.readframes(CHUNK)
b = bytearray()
while len(data) > 0:
    b.extend(data)
    data = wf.readframes(CHUNK)

hex_data = binascii.hexlify(b)
str_data = hex_data.decode('utf-8')

binascii.unhexlify(str_data.encode('utf-8'))

print(b)

waveFile = wave.open("recordedFileFromByte.wav", 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b)
waveFile.close()
