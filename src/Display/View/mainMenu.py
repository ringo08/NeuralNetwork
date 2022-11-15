import tkinter as tk
from . import Button, Frame

class MainMenu(Frame):
  def __init__(self, master, columns):
    self.width = 240
    self.height = 540
    super().__init__(master=master, width=self.width, height=self.height)
    self.master = master
    self.menuColumns = columns
    self.initUI()
  
  def initUI(self):
    self.buttons = {}
    for column in self.menuColumns:
      self.buttons[column['value']] = Button(self, text=column['label'], width=128, height=48, fill=tk.BOTH)
      self.buttons[column['value']]['state'] = tk.NORMAL if column['always'] else tk.DISABLED
    self.pack(fill=tk.BOTH, pady=24, padx=24)
  
  def setCommands(self, props: dict):
    for key, value in props.items():
      self.setCommand(key, value)

  def setCommand(self, key, func):
    if key in self.buttons.keys():
      self.buttons[key]['command'] = func

  def changeMenuMode(self, flag: bool):
    for column in self.menuColumns:
      self.buttons[column['value']]['state'] = tk.NORMAL if column['always'] or flag else tk.DISABLED
