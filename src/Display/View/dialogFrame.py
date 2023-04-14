import tkinter as tk
from . import ButtonBox, Frame

class DialogFrame(tk.Frame):
  def __init__(self, master, title=None, width=400, height=320, footerHeight=64):
    self.master = master
    self.master.geometry(f'{width}x{height}')
    self.master.resizable(width=False, height=False)
    self.master.config(bg='#FAFAFA')
    self.master.title(title)

    self.width = width
    self.height = height
    self.footerHeight = footerHeight
    super().__init__(master)
    self.init_body(self.master)
    self.init_footer()

  def init_body(self, master, func=None):
    self.rootLayout = Frame(master, width=self.width, height=self.height)
    self.rootLayout.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True, ipadx=0, ipady=0, padx=0, pady=0)

    bodyLayout = Frame(self.rootLayout, width=self.width, height=self.height-self.footerHeight)
    bodyLayout.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True, ipadx=0, ipady=0, padx=0, pady=0)
    if func:
      func(bodyLayout)

  def init_footer(self, func=None):
    if func:
      func(self.rootLayout)
    else:
      buttons = (
        { 'text': 'ok' },
        { 'text': 'cancel', 'command': self.cancel }
      )
      self.actions = ButtonBox(self.rootLayout, width=self.width, height=self.footerHeight, children=buttons)
