import tkinter as tk
from . import Frame, Label, Entry

defaultProps = {
  'color': '#FAFAFA',
  'ipadx': 8,
  'ipady': 4,
  'padx': 8,
  'pady': 8,
  'anchor': tk.CENTER,
  'side': tk.TOP,
  'fill': tk.X,
  'fontSize': 14,
  'expand': False
}

class TextField(Entry):
  def __init__(self, master, width=256, height=48, textWidth=128, text='', defaultValue='', bindText='', **kwargs):
    props = { key: kwargs[key] if key in kwargs.keys() else value for key, value in defaultProps.items() }
    self.width = width
    self.height = height

    fontSize = props['fontSize']
    frame = Frame(master=master, width=width, height=height)
    self.label = Label(master=frame, height=height, text=text, side=tk.LEFT, expand=True, pady=8)
    super().__init__(master=frame, width=textWidth, height=height, font=('', fontSize), side=tk.RIGHT, expand=True, pady=8, defaultValue=str(defaultValue), bindText=bindText)
    
    frameProps = ['padx', 'pady', 'anchor', 'side', 'fill', 'expand']
    frame.pack(**{ key: props[key] for key in frameProps })
