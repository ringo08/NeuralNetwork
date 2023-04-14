import tkinter as tk
from . import Button, Frame

defaultProps = {
  'color': '#FAFAFA',
  'padx': 0,
  'pady': 0,
  'anchor': tk.CENTER,
  'side': tk.TOP,
  'fill': tk.BOTH,
}

defaultButtonProps = {
  'text': 'ok',
  'width': 128,
  'height': 16,
  'padx': 8,
  'color': '#FAFAFA',
  'anchor': tk.CENTER,
  'fill': tk.Y,
  'side': tk.LEFT,
  'expand': True,
  'command': None
}

class ButtonBox(Frame):
  def __init__(self, master, width=64, height=64, children=(), **kwargs):
    props = { key: kwargs[key] if key in kwargs.keys() else value for key, value in defaultProps.items() }
    super().__init__(master=master, width=width, height=height, color=props['color'])
    children = children if children else ({ 'text': 'ok' }, { 'text': 'cancel' })

    self.buttons = {}

    for child in children:
      buttonProps = { key: child[key] if key in child.keys() else value for key, value in defaultButtonProps.items() }
      self.buttons[buttonProps['text']] = Button(self, **buttonProps)

    frameProps = ('padx', 'pady', 'anchor', 'side', 'fill')
    self.pack(**{ key: props[key] for key in frameProps })
    