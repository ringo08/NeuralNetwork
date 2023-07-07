import tkinter as tk
from tkinter import simpledialog
from . import ButtonBox, Frame

class Dialog(simpledialog.Dialog):
  def __init__(self, master=None, title=None, width=400, height=320, footerHeight=64):
    self.master = master
    self.width = width
    self.height = height
    self.actions = None
    self.footerHeight = footerHeight
    super().__init__(parent=master, title=title)

  def body(self, master, func=None, padx=0, pady=0):
    self.geometry(f'{self.width}x{self.height}')
    self.resizable(width=False, height=False)
    self.config(bg='#FAFAFA')
    self.rootLayout = Frame(master, width=self.width, height=self.height)
    self.rootLayout.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True, ipadx=0, ipady=0, padx=padx, pady=pady)
    bodyLayout = Frame(self.rootLayout, width=self.width, height=self.height-self.footerHeight)
    bodyLayout.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True, ipadx=0, ipady=0, padx=0, pady=0)
    if func:
      func(bodyLayout)
  
  def buttonbox(self, func=None):
    if func:
      func(self.rootLayout)
    else:
      buttons = tuple([
        { 'text': 'ok', 'command': self.ok },
        { 'text': 'cancel', 'command': self.cancel }
      ])
      self.actions = ButtonBox(self.rootLayout, width=self.width, height=self.footerHeight, children=buttons)