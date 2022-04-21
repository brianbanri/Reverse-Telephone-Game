import tkinter as tk
from PIL import Image, ImageTk
from game import *
import pyaudio
import wave

root = tk.Tk()

root.title("Reverse Telephone")
canvas = tk.Canvas(root, width=1000,height=700, bg="white")
canvas.grid(columnspan=3)


def getAudioDevice():
    audioList = tk.Label(root, text="Audio Device List", font="Raleway", bg="white")
    audioList.place(x=400, y=100)
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
                if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))


def titleScreen():
    logo = Image.open('title.png')
    logo = ImageTk.PhotoImage(logo)
    logo_label = tk.Label(image=logo)
    logo_label.image = logo
    logo_label.place(x=200, y=10)
    
    local_text = tk.StringVar()
    local_btn = tk.Button(root, textvariable=local_text, font="Raleway", bg="#ff9999", fg="black", width = 20, command=lambda: host_game())
    local_text.set("Start Local Game")
    local_btn.place(x=400, y=260)

    #host and join game
    host_text = tk.StringVar()
    host_btn = tk.Button(root, textvariable=host_text, font="Raleway", bg="#ff9999", fg="black", width = 20, command=lambda: host_game())
    host_text.set("Host Game")
    host_btn.place(x=300, y=300)

    join_text = tk.StringVar()
    join_btn = tk.Button(root, textvariable=join_text, font="Raleway", bg="#ff9999", fg="black", width = 20, command=lambda: join_game())
    join_text.set("Join Game")
    join_btn.place(x=500, y=300)



    #instructions
    instructions = tk.Label(root, text="Reverse Telephone is a variation of the classic telephone game, \ndesigned for any group of all ages! You'll need at least 2 to play, but it only gets more fun with more players.", font="Raleway", bg="white")
    instructions.place(x=150, y=400)


def host_game():
    root.withdraw()
    Window = tk.Toplevel()
    canvas = tk.Canvas(Window, height=1000, width=1000, bg="white")
    Window.title("Reverse Telephone (HOST)")
    canvas.pack()

def join_game():
    Window = tk.Toplevel()
    canvas = tk.Canvas(Window, width=1000,height=1000, bg="white")
    Window.title("Reverse Telephone (JOIN)")
    canvas.pack()




getAudioDevice()
root.mainloop()