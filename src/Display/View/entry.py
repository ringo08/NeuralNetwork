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
  'vcmd': None,
  'validate': 'all',
  'expand': False
}

class Entry(tk.Entry):
  def __init__(self, master, width=256, height=64, defaultValue='', bindText='', multiple=False, **kwargs):
    props = { key: kwargs[key] if key in kwargs.keys() else value for key, value in defaultProps.items() }
    self.width = width
    self.height = height
    self.bindText = bindText
    frame = Frame(master=master, width=width, height=height)

    defaultVcmd = (master.register(self.multipleCallback)) if multiple else (master.register(self.callback))
    vcmd = props['vcmd'] if (props['vcmd'] is not None) else defaultVcmd
    super().__init__(
      master=frame,
      justify=tk.CENTER,
      validate=props['validate'],
      validatecommand=(vcmd, '%P'),
      highlightthickness=0,
      fg=props['fontColor']
      )
    self.config(bg=props['color'], insertbackground=props['fontColor'])

    if defaultValue:
      self.insert(0, defaultValue)
    self.pack(fill=tk.BOTH, padx=props['ipadx'], pady=props['ipady'], expand=True)
    frameProps = ('padx', 'pady', 'anchor', 'side', 'fill', 'expand')
    frame.pack(**{ key: props[key] for key in frameProps })
  
  def set(self, text):
    self.erase()
    self.insert(0, text)
  
  def erase(self):
    self.delete(0, tk.END)

  def multipleCallback(master, string):
    f = lambda x: True if str.isdigit(x) or x in (' ') else False
    return all((f(s) for s in string))

  def callback(master, string):
    f = lambda x: True if str.isdigit(x) else False
    return (master.bindText in string) and all((f(s) for s in string[len(master.bindText):]))
