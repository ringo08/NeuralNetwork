import tkinter as tk
from tkinter import ttk
from . import Frame

defaultProps = {
  'color': 'white',
  'ipadx': 0,
  'ipady': 0,
  'padx': 0,
  'pady': 0,
  'anchor': tk.CENTER,
  'ianchor': tk.CENTER,
  'side': tk.TOP,
  'iside': tk.TOP,
  'fill': tk.BOTH,
  'fontSize': 14,
  'fontColor': 'black',
  'vcmd': None,
  'validate': 'all',
  'expand': False,
  'iexpand': True,
  'state': 'normal'
}

class ComboBox(ttk.Combobox):
  def __init__(self, master, width=128, height=64, defaultValue=[], items='', **kwargs):
    props = { key: kwargs[key] if key in kwargs.keys() else value for key, value in defaultProps.items() }
    self.width = width
    self.height = height
    frame = Frame(master=master, width=width, height=height)
    if items:
      self.items = items

    super().__init__(
      master=frame,
      justify=tk.CENTER,
      values=items,
      state=props['state']
    )
    # self.config(bg=props['color'], insertbackground=props['fontColor'])
    if defaultValue in items:
      self.set(defaultValue)

    selfProps = ['ipadx', 'ipady', 'ianchor', 'iside', 'iexpand']
    self.pack(fill=tk.BOTH, **{ key[1:]: props[key] for key in selfProps })
    frameProps = ['padx', 'pady', 'anchor', 'side', 'fill', 'expand']
    frame.pack(**{ key: props[key] for key in frameProps })
