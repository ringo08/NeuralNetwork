import math
import tkinter as tk
from . import Frame

def particleCount(decay, p0, time):
  p = (p0*math.e)**(-(decay*time))
  return (p)

class Graph(Frame):
  def __init__(self, master, width=420, height=220):
    super().__init__(master, width=width, height=height)
    self.tickSize = 24
    self.canvasSize = (width-self.tickSize, height-self.tickSize)
    self.pack(fill=tk.BOTH, expand=True)
    self.maximum = math.log10(10)
    self.minimum = math.log10(0.1)
    self.data = []
    self.maxPoint = 0
    self.ytickPoints = []
    self.ytickLabels = []
    self.xtickPoints = []
    self.xtickLabels = []
    self.progress = None
    self._init_graph()
    self.graph_plot()

  def _init_graph(self):
    self.graphCanvas = tk.Canvas(self, background="gray", highlightthickness=0)
    self.graphCanvas.place(x=self.tickSize, y=0, width=self.canvasSize[0], height=self.canvasSize[1])
    self.graphCanvas.bind("<Button-1>", self.click)
    self.line = self.graphCanvas.create_line((0, self.canvasSize[1]//2, self.canvasSize[0], self.canvasSize[1]//2), tag='line', width=1, fill='black')

    self.ytickCanvas = tk.Canvas(self, highlightthickness=0)
    self.xtickCanvas = tk.Canvas(self, highlightthickness=0)
    self.ytickCanvas.place(x=0, y=0, width=self.tickSize, height=self.canvasSize[1])
    self.xtickCanvas.place(x=self.tickSize, y=self.canvasSize[1], width=self.canvasSize[0], height=self.tickSize)

  def click(self, event):
    print(event)

  def clear(self):
    self._init_graph()
    
  def setMinimum(self, minimum):
    self.minimum = math.log10(minimum)

  def addData(self, x):
    self.data.append(x)
    self.graph_plot()

  def setData(self, datas):
    self.data = datas
    self.graph_plot()
  
  def graph_plot(self):
    width, height = self.canvasSize
    minimum = self.minimum - 2
    yRange = (abs(minimum) + abs(self.maximum))
    self.maxPoint = len(self.data)

    if self.maxPoint < 1:
      return
    xtickPoint = int(self.maxPoint/10)
    if xtickPoint > 0:
      xtick = { n: (width/self.maxPoint)*n for n in range(1, self.maxPoint+1, xtickPoint) }
    else:
      xtick = { n: (width/self.maxPoint)*n for n in range(1, self.maxPoint) }
    h = height/yRange
    ytick = { l: h*n for l, n in zip(range(int(self.maximum), int(minimum-1), -1), range(int(yRange+1))) }
    self.tick_plot(xtick, ytick)
    
    if self.maxPoint < 2:
      return
    coords = []
    for n in range(self.maxPoint):
      x = (width * n) / self.maxPoint
      coords.append(x)
      coords.append(h*(-1*math.log10(self.data[n])+self.maximum))

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

  def _create_tick_labels(self, canvas, labels=[], ticks=[], tickPad=4, oriental='x'):
    if oriental == 'x':
      labels = [canvas.create_text(tick, tickPad, text=int(labels[i]), anchor=tk.N, font=('', 10)) for i, tick in enumerate(ticks)]
    elif oriental == 'y':
      labels = [canvas.create_text(tickPad, tick+tickPad, text=int(labels[i]), anchor=tk.W, font=('', 10)) for i, tick in enumerate(ticks)]

    return labels

  def _create_ticks_points(self, canvas, ticks=[], tickLen=4, oriental='x'):
    if oriental == 'x':
      points = [(tick, 0, tick, tickLen) for tick in ticks]
    elif oriental == 'y':
      points = [(self.tickSize-tickLen, tick, self.tickSize, tick) for tick in ticks]

    return [canvas.create_line(*point) for point in points]
