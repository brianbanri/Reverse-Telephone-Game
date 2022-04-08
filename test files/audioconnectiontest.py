
import pyaudio
import wave

import Pyro4
import os
import socket


@Pyro4.expose
class ServerHost(object):
    def getAudio(self):
        wf = wave.open("recordedFile.wav", 'rb')
        

daemon = Pyro4.Daemon(host=socket.gethostbyname(socket.gethostname()))                # make a Pyro daemon
ns = Pyro4.locateNS()                  # find the name server
uri = daemon.register(ServerHost)   # register the greeting maker as a Pyro object
ns.register("example.serverhost", uri)   # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()                   # start the event loop of the server to wait for calls



