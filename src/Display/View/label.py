import tkinter as tk
from . import Frame

defaultProps = {
  'color': '#FAFAFA',
  'ipadx': 0,
  'ipady': 0,
  'padx': 0,
  'pady': 0,
  'anchor': tk.CENTER,
  'side': tk.TOP,
  'fontColor': 'black',
  'fill': tk.BOTH,
  'fontSize': 14,
  'expand': False
}

class Label(tk.Label):
  def __init__(self, master, text='', width=128, height=32, **kwargs):
    frame = Frame(master=master, width=width, height=height)
    self.width = width
    self.height = height
    props = { key: kwargs[key] if key in kwargs.keys() else value for key, value in defaultProps.items() }

    fontSize = props['fontSize']
    frameProps = ['padx', 'pady', 'anchor', 'side', 'fill', 'expand']
    frame.pack(**{ key: props[key] for key in frameProps })
    super().__init__(frame, text=text, font=('', fontSize), fg=props['fontColor'], wraplength=width)
    self.config(bg=props['color'])
    self.pack(fill=tk.BOTH, padx=props['ipadx'], pady=props['ipady'], expand=True)


  def setText(self, string):
    self['text'] = string

  def getText(self):
    return self['text']