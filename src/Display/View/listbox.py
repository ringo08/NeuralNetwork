import tkinter as tk
from . import Frame

defaultProps = {
  'color': 'white',
  'ipadx': 0,
  'ipady': 0,
  'padx': 0,
  'pady': 0,
  'anchor': tk.CENTER,
  'side': tk.TOP,
  'fill': tk.BOTH,
  'fontSize': 14,
  'fontColor': 'black',
  'expand': False
}

class Listbox(tk.Listbox):
  def __init__(self, master, width=256, height=160, defaultItems=(), **kwargs):
    props = { key: kwargs[key] if key in kwargs.keys() else value for key, value in defaultProps.items() }
    self.width = width
    self.height = height
    self.items = tk.StringVar(value=defaultItems)
    frame = Frame(master=master, width=width, height=height)

    super().__init__(master=frame, fg=props['fontColor'], selectforeground=props['fontColor'], selectbackground='cyan', listvariable=self.items)
    self.config(bg=props['color'])
    # self.propagate(False)

    self.pack(fill=tk.BOTH, padx=props['ipadx'], pady=props['ipady'], expand=True)
    # self.pack(fill=tk.BOTH, ipadx=props['ipadx'], ipady=props['ipady'], expand=True)
    frameProps = ('padx', 'pady', 'anchor', 'side', 'fill', 'expand')
    frame.pack(**{ key: props[key] for key in frameProps })

  def getItems(self):
    return self.get(0, tk.END)
  
  def clearItems(self):
    self.delete(0, tk.END)