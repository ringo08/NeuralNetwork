import tkinter as tk
from . import Frame, Label

defaultProps = {
  'color': '#FAFAFA',
  'padx': 0,
  'pady': 0,
  'anchor': tk.CENTER,
  'side': tk.RIGHT,
  'fill': tk.BOTH,
  'fontSize': 12,
  'expand': True
}

class ColorBar(Frame):
  def __init__(self, master, width=48, height=480, **kwargs):
    self.width = width
    self.height = height
    self.canvasSize = (24, 400)
    labelSize = 24
    props = { key: kwargs[key] if key in kwargs.keys() else value for key, value in defaultProps.items() }
    super().__init__(master, width, height)

    self.canvas = tk.Canvas(self, width=self.canvasSize[0], height=self.canvasSize[1], highlightthickness=0)
    self.create_colorscale()
    
    frame1 = Frame(self, width=1, height=1)
    frame1.pack(expand=True)
    self.plusLabel = Label(self, width=self.canvasSize[0], height=labelSize, text='+')
    self.canvas.pack()
    self.minusLabel = Label(self, width=self.canvasSize[0], height=labelSize, text='-')
    frame2 = Frame(self, width=1, height=1)
    frame2.pack(expand=True)
    
    frameProps = ('padx', 'pady', 'anchor', 'side', 'fill', 'expand')
    self.pack(**{ key: props[key] for key in frameProps })
    
  
  def create_colorscale(self):
    scale = 255
    x0, y0 = (0, 0)
    x1, maxHeight = self.canvasSize
    y1 = maxHeight / (scale*2)
    for s in range(scale, -(scale+1), -1):
      color = f'#0000{s:02x}' if s >= 0 else f'#{abs(s):02x}0000'
      self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='')
      y0 += maxHeight / (scale*2)
      y1 += maxHeight / (scale*2)