# saved as greeting-client.py
import pyaudio
import wave

import Pyro4
import socket

chunk = 512

serverhost = Pyro4.Proxy("PYRONAME:example.serverhost")    # use name server object lookup uri shortcut
wf = serverhost.getAudio()

p = pyaudio.PyAudio()
stream = p.open(
    format = p.get_format_from_width(wf.getsampwidth()),
    channels = wf.getnchannels(),
    rate = wf.getframerate(),
    output = True
)

""" Play entire file """
data = wf.readframes(chunk)
while len(data) > 0:
    stream.write(data)
    data = wf.readframes(chunk)

stream.close()
p.terminate()