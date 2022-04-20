import Tkinter as tk
from PIL import Image, ImageTk
#from game import *

root = tk.Tk()

root.title("Reverse Telephone")
canvas = tk.Canvas(root, width=1000,height=1000, bg="white")
canvas.grid(columnspan=3)

logo = Image.open('title.png')
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.place(x=200, y=10)


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


telephone = Image.open('telephone.png')
telephone = ImageTk.PhotoImage(telephone)
telephone_label = tk.Label(image=telephone)
telephone_label.image = telephone
telephone_label.place(x=200, y=450)


def host_game():
    Window = tk.Toplevel()
    canvas = tk.Canvas(Window, height=1000, width=1000, bg="white")
    Window.title("Reverse Telephone (HOST)")
    canvas.pack()

def join_game():
    Window = tk.Toplevel()
    canvas = tk.Canvas(Window, width=1000,height=1000, bg="white")
    Window.title("Reverse Telephone (JOIN)")
    canvas.pack()


root.mainloop()