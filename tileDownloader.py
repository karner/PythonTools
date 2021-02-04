import Tkinter as tk

class Node:
    def __init__(self):


class Rectangle:
    def __init__(self):
        self.minX =
        self.minY =
        self.maxX =
        self.maxY =


class Application:
    def __init__(self, master):
        frame = tk.Frame(master)
        frame.pack()

        self.button = tk.Button(
            frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=tk.LEFT)

        self.hi_there = tk.Button(
            frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=tk.LEFT)

        self.txtMinLat = tk.Entry(frame, bd=5)
        self.txtMinLat.pack(side=tk.LEFT)

    def say_hi(self):
        print "hi there, everyone!"

root = tk.Tk()

application = Application(root)

root.mainloop()
