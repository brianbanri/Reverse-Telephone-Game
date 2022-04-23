
import pyaudio
import wave

import Pyro4
import Pyro4.naming

import os
import socket
import threading
import time

import binascii


@Pyro4.expose
class ServerHost(object):
    def getAudio(self):
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


        #b = ''.join(chr(x) for x in b)
        hex_data = binascii.hexlify(b)
        str_data = hex_data.decode('utf-8')

        wf.close()

        return str_data

def start_name_server():
    Pyro4.naming.startNSloop(host="0.0.0.0")

name_server_thread = threading.Thread(target=start_name_server, daemon=True)
name_server_thread.start()

time.sleep(5)

daemon = Pyro4.Daemon(host=socket.gethostbyname(socket.gethostname()))                # make a Pyro daemon
ns = Pyro4.locateNS()                  # find the name server
uri = daemon.register(ServerHost)   # register the greeting maker as a Pyro object
ns.register("example.serverhost", uri)   # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()                   # start the event loop of the server to wait for calls



