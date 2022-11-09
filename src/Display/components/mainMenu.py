import tkinter as tk
from . import Button, Frame

class MainMenu(Frame):
  def __init__(self, master, columns):
    self.width = 240
    self.height = 540
    super().__init__(master=master, width=self.width, height=self.height)
    self.master = master
    self.menuColumns = columns
    # self.master.geometry(f'{self.width}x{self.height}')
    # self.master.resizable(width=False, height=False)
    self.initUI()
  
  def initUI(self):
    self.buttons = {}
    for column in self.menuColumns:
      self.buttons[column['label']] = Button(self, text=column['label'], width=128, height=48, fill=tk.BOTH)
      self.buttons[column['label']]['state'] = tk.NORMAL if column['always'] else tk.DISABLED
    self.pack(fill=tk.BOTH, pady=24, padx=24)

  def changeMenuMode(self, flag: bool):
    for column in self.menuColumns:
      self.buttons[column['label']]['state'] = tk.NORMAL if column['always'] or flag else tk.DISABLED
