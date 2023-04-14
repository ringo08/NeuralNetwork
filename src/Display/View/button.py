import tkinter as tk
from . import Frame

defaultProps = {
  'color': '#FAFAFA',
  'ipadx': 8,
  'ipady': 4,
  'padx': 8,
  'pady': 8,
  'anchor': tk.CENTER,
  'side': tk.TOP,
  'fill': tk.BOTH,
  'fontSize': 14,
  'command': None,
  'expand': False
}

class Button(tk.Button):
  def __init__(self, master, text='', width=64, height=32, **kwargs):
    frame = Frame(master=master, width=width, height=height)
    self.text = tk.StringVar()
    self.text.set(text)
    self.width = width
    self.height = height
    props = { key: kwargs[key] if key in kwargs.keys() else value for key, value in defaultProps.items() }

    super().__init__(frame, textvariable=self.text, font=('', props['fontSize']), command=props['command'], highlightthickness=0, borderwidth=1)
    self.config(background=props['color'])
    self.pack(fill=tk.BOTH, ipadx=props['ipadx'], ipady=props['ipady'])

    frameProps = ('padx', 'pady', 'anchor', 'side', 'fill', 'expand')
    frame.pack(**{ key: props[key] for key in frameProps })
  
  def setLabel(self, text):
    self.text.set(text)

  def getLabel(self):
    return self.text.get()