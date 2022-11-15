import math
import tkinter as tk
from . import Frame

def particleCount(decay, p0, time):
  p = (p0*math.e)**(-(decay*time))
  return (p)

class Graph(Frame):
  def __init__(self, master, width=420, height=220):
    super().__init__(master, width=width, height=height)
    self.tickSize = (24, 24)
    self.canvasSize = (width-self.tickSize[0], height-self.tickSize[1])
    self.ytickCanvas = tk.Canvas(self, highlightthickness=0)
    self.xtickCanvas = tk.Canvas(self, highlightthickness=0)
    self.graphCanvas = tk.Canvas(self, background="gray", highlightthickness=0)
    self.graphCanvas.bind("<Button-1>", self.click)
    self.init_graph()
    self.pack(fill=tk.BOTH, expand=True)

  def init_graph(self):
    self.data = []
    self.maxPoint = 0
    self.line = self.graphCanvas.create_line((0, self.canvasSize[1]//2, self.canvasSize[0], self.canvasSize[1]//2), tag='line', width=1, fill='black')
    self.ytickPoints = []
    self.ytickLabels = []
    self.xtickPoints = []
    self.xtickLabels = []
    self.ytickCanvas.place(x=0, y=0, width=self.tickSize[0], height=self.canvasSize[1])
    self.xtickCanvas.place(x=self.tickSize[0], y=self.canvasSize[1], width=self.canvasSize[0], height=self.tickSize[1])
    self.graphCanvas.place(x=self.tickSize[0], y=0, width=self.canvasSize[0], height=self.canvasSize[1])

  def click(self, event):
    print(event)
  
  def clear(self):
    self.init_graph()

  def addData(self, x):
    self.data.append(x)
    self.maxPoint = len(self.data)
    self.graph_plot()

  def setData(self, datas):
    self.data = datas
    self.maxPoint = len(self.data)
    self.graph_plot()

  def graph_plot(self):
    w, h = self.canvasSize
    max_y = math.log10(10)
    min_y = math.log10(min(self.data)*1e-2)
    max_X = len(self.data)
    if len(self.data) < 2:
      return

    coords = []
    for n in range(self.maxPoint):
      x = (w * n) / self.maxPoint
      coords.append(x)
      coords.append(h*(math.log10(self.data[n])/(min_y+max_y)))
    
    xn = 5
    xtick = {n: (w*n)/max_X for n in range(1, self.maxPoint+1) if n % xn==0}
    ytick = {t: h*t/int(min_y+max_y) for t in range(int(min_y+max_y), -1)}
    self.tick_plot(xtick, ytick)
    
    self.graphCanvas.coords('line', *coords)
    self.graphCanvas.update()
    self.update()
  
  def tick_plot(self, xtick, ytick):
    if self.ytickPoints:
      self.ytickCanvas.delete(*self.ytickPoints)
    if self.ytickLabels:
      self.ytickCanvas.delete(*self.ytickLabels)
    if self.xtickPoints:
      self.xtickCanvas.delete(*self.xtickPoints)
    if self.xtickLabels:
      self.xtickCanvas.delete(*self.xtickLabels)
    self.ytickPoints = self._create_ticks_points(self.ytickCanvas, ticks=ytick.values(), oriental='y')
    self.ytickLabels = self._create_tick_labels(self.ytickCanvas, labels=list(ytick.keys()), ticks=ytick.values(), oriental='y')
    self.xtickPoints = self._create_ticks_points(self.xtickCanvas, ticks=xtick.values(), oriental='x')
    self.xtickLabels = self._create_tick_labels(self.xtickCanvas, labels=list(xtick.keys()), ticks=xtick.values(), oriental='x')

  def _create_tick_labels(self, canvas, labels=[], ticks=[], oriental='x'):
    w, h = self.tickSize
    if oriental == 'x':
      labels = [canvas.create_text(tick, 4, text=int(labels[i]), anchor=tk.N, font=('', 10)) for i, tick in enumerate(ticks)]
    elif oriental == 'y':
      labels = [canvas.create_text(0, tick, text=int(labels[i]), anchor=tk.W, font=('', 10)) for i, tick in enumerate(ticks)]

    return labels

  def _create_ticks_points(self, canvas, ticks=[], tickLen=4, oriental='x'):
    w, h = self.tickSize
    if oriental == 'x':
      points = [(tick, 0, tick, tickLen) for tick in ticks]
    elif oriental == 'y':
      points = [(w-tickLen, tick, w, tick) for tick in ticks]

    return [canvas.create_line(*point) for point in points]
