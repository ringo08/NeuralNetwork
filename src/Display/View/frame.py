import tkinter as tk

class Frame(tk.Frame):
  def __init__(self, master, width, height, color='#FAFAFA'):
    self.width = width
    self.height = height
    super().__init__(master=master, width=width, height=height)
    self.config(bg=color)
    self.propagate(False)
