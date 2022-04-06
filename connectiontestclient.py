# saved as greeting-client.py
import Pyro4

x = int(input("What is your number? "))

serverhost = Pyro4.Proxy("PYRONAME:example.serverhost")    # use name server object lookup uri shortcut
print(serverhost.increment(x))