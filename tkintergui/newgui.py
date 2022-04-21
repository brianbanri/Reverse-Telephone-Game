import tkinter as tk
import sys

class GUIPrint:
    def __init__(self, text_widget:tk.Text):
        self.old_stdout = sys.stdout
        self.text = text_widget

    def write(self, data:str):
        # Insert the text in the text widget
        self.text.insert("end", data)

    def __enter__(self):
        # Enter the `with` statement
        sys.stdout = self
        return self

    def __exit__(self, *args):
        # Exit the `with` statement
        sys.stdout = self.old_stdout



def function():
	print("\nWelcome to The Reverse Telephone Game!\n")
	print("Type \"Start Local Game\" to start a new game on this device")
	print("Type \"Host Game\" to host a new game")
	print("Type \"Join Game\" to join an existing game")

	user_input = input()
	print()

root = tk.Tk()

text_widget = tk.Text(root)
text_widget.pack()
gui_printer = GUIPrint(text_widget)

print("Normal stdout")
with gui_printer:
    print("Inside the GUI")
    function()
print("Normal stdout")

root.mainloop()