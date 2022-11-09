import tkinter as tk
import itertools
from . import Frame, DialogFrame, ColorBar, Graph

class NetworkDialog(DialogFrame):
  def __init__(self, master, title=None, onUpdate=None, defaultLayer=[2, 2, 3]):
    self.width = 840
    self.height = 660
    self.pad = 24
    self.layers = defaultLayer
    self.onUpdate = onUpdate
    super().__init__(master, title=title, width=self.width, height=self.height)
    self.onUpdateDisplay()

  def init_body(self, master):
    super().init_body(master, func=self._init_body)

  def init_footer(self):
    super().init_footer(func=self._init_footer)

  def _init_body(self, master):
    leftFrame = Frame(master, width=self.width//2, height=self.height)
    leftFrame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, pady=self.pad)
    
    networkFrame = Network(leftFrame, width=self.width//2, height=self.height//3*2-self.pad*2, layers=self.layers)
    self.graph = Graph(leftFrame, width=self.width//2, height=self.height//3-self.pad)
    
    rightFrame = Frame(master, width=self.width//2, height=self.height)
    rightFrame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, pady=self.pad)
    
    colorbarWidth = 48
    self.connection = DisplayConnection(rightFrame, width=self.width//2-colorbarWidth, height=self.height, layers=self.layers)
    colorscaleFrame = ColorBar(rightFrame, width=colorbarWidth)

  def onResetDisplay(self, inputSize):
    self.connection.setInputSize(inputSize)
    self.connection.replot()

  def onUpdateDisplay(self, func=None):
    items = func() if bool(func) else self.onUpdate()
    if items == None:
      return
    flag, loss, layerOuts, weights = items
    if not flag:
      self.graph.clear()
      return
    if loss:
      self.graph.setData(loss)
    self.connection.update_boxes(layerOuts, weights)

  def _init_footer(self, master):
    pass


class Network(Frame):
  def __init__(self, master, width, height, layers):
    self.width = width
    self.height = height
    self.layers = layers
    self.canvasPad = 16
    self.circlePad = 8
    super().__init__(master, width, height)
    self.pack(fill=tk.BOTH, side=tk.TOP)

    self.canvas = tk.Canvas(self, width=width, height=height, background='white', highlightthickness=0)
    self.canvas.pack()

    self.create_network()
    self.create_connection()
    self.canvas.bind('<Button-1>', lambda e: print(self.click(e)))

  def create_network(self):
    self.all_w = self.width / (2*max(self.layers) + 1)
    self.h = self.height / (2*len(self.layers) + 1)
    self.r = self.all_w/2 if self.all_w < self.h else self.h/2
    self.neurons = []
    for i in range(len(self.layers)):
      y = self.height - self.h*(2*i+1.5)
      neurons = []
      self.w = self.width / (2*self.layers[i] + 1)
      for j in range(self.layers[i]):
        x = self.w*(2*j+1.5)
        neurons.append(self.canvas.create_oval(x-self.r, y-self.r, x+self.r, y+self.r, tag=f'network-layer:{i}-neuron:{j}', fill='#0f0', outline='black'))
      self.neurons.append(neurons)
    
  def create_connection(self):
    self.weights = []
    for i in range(1, len(self.layers)):
      weights = []
      for j in range(self.layers[i]):
        nextNeuron = self.canvas.bbox(f'network-layer:{i}-neuron:{j}')
        x0 = nextNeuron[2]-self.r
        y0 = nextNeuron[3]
        for k in range(self.layers[i-1]):
          frontNeuron = self.canvas.bbox(f'network-layer:{i-1}-neuron:{k}')
          x1 = frontNeuron[2]-self.r
          y1 = frontNeuron[1]
          weights.append(self.canvas.create_line(x0, y0, x1, y1, tag=f'network-layer:{i}-neuron:{j}-weight:{k}', fill='black', activefill='#0f0'))
      self.weights.append(weights)
  
  def click(self, event):
    pic = 2
    tags = [self.canvas.itemcget(obj, 'tags') for obj in self.canvas.find_overlapping(*((event.x-pic, event.y-pic, event.x+pic, event.y+pic)))]
    tagName = None
    for tag in tags:
      tagName = tags[0]
      if 'current' in tag:
        return tag.replace('current', '').strip()
    return tagName
      

class DisplayConnection(Frame):
  def __init__(self, master, width: int, height: int, layers):
    self.width = width
    self.height = height
    self.layers = layers
    self.networkWidth = 340
    self.networkHeight = 72
    super().__init__(master, width, height)
    self.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
    self.canvas = []
    self.inputSize = 1
    self.create_boxes()

  def get_maxmin_flatter(self, array, nest=2):
    for _ in range(nest-1):
      array = list(itertools.chain.from_iterable(array))
    return max(array), min(array)

  def update_boxes(self, layerOuts, weights):
    maxScale = 2
    for canvas in self.canvas:
      for tag in canvas.get_tags():
        values = tag.split('-')[1:]
        n = [int(value.split(':')[1]) for value in values]
        if 'weight' in tag:
          minimum, maximum = self.get_maxmin_flatter(weights[n[0]-1], 2)
          scale = abs(minimum) if abs(minimum) > abs(maximum) else abs(maximum)
          scale = maxScale if scale < maxScale else scale
          color = weights[n[0]-1][n[1]][n[2]]
          canvas.update_color(tag, color, scale)
        else:
          color = layerOuts[n[0]][n[1]]
          canvas.update_color(tag, color, 1)
    self.update()

  def setInputSize(self, size):
    self.inputSize = size

  def replot(self):
    for canvas in self.canvas:
      canvas.destroy()
    self.canvas = []
    self.create_boxes()

  def create_boxes(self):
    lineNum = len(self.layers)*2
    for i in range(lineNum):
      index = i//2
      self.canvas.append(Canvas(self))
      rows = self.inputSize if index == 0 else 1
      if i%2 == 0:
        self.create_layer_box(index=index, rows=rows)
      elif index < len(self.layers)-1:
        self.create_weight_box(indexes=(index, index+1), rows=rows)
    self.create_layer_box(index=len(self.layers)-1, target=True, rows=rows)

  def create_layer_box(self, index=2, rows=1, target=False):
    layer = self.layers[index]
    columns = layer//rows
    width = self.networkWidth/columns
    height = self.networkHeight/rows
    for row in range(rows):
      for column in range(columns):
        self.canvas[-1].create_box((width*column, height*row, width*(column+1), height*(row+1)), f'boxes-layer:{index+1 if target else index}-neuron:{column+row*columns}')

  def create_weight_box(self, indexes: tuple[float, float], rows=1):
    front, next = tuple(indexes)
    frontLayer = self.layers[front]
    columns = frontLayer//rows
    nextLayer = self.layers[next]
    width = self.networkWidth/columns
    height = self.networkHeight/(nextLayer*rows)
    for i in range(nextLayer):
      for row in range(rows):
        for column in range(columns):
          self.canvas[-1].create_box((width*column, height*(row+rows*i), width*(column+1), height*(row+rows*i+1)), f'boxes-layer:{next}-neuron:{i}-weight:{row+rows*i}')
  
  
  def click(self, event):
    pic = 2
    tags = [self.canvas.itemcget(obj, 'tags') for obj in self.canvas.find_overlapping(*((event.x-pic, event.y-pic, event.x+pic, event.y+pic)))]
    tagName = None
    for tag in tags:
      tagName = tags[0]
      if 'current' in tag:
        return tag.replace('current', '').strip()
    return tagName

class Canvas(Frame):
  def __init__(self, master, width=340, height=72):
    self.width = width
    self.height = height
    super().__init__(master, width, height)
    self.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)

    self.canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0)
    self.canvas.bind('<Button-1>', self.click)
    self.canvas.pack()
  
  def create_colorscale(self, num):
    scale = int(255*num if -1 < num < 1 else 255 if num > 0 else -255)
    return  f'#0000{scale:02x}' if scale >= 0 else f'#{abs(scale):02x}0000'
  
  def update_color(self, tag, color, maxValue=1):
    self.canvas.itemconfigure(tag, **{ 'fill': self.create_colorscale(color/maxValue) })

  def get_tags(self):
    ids = self.canvas.find_all()
    return [self.canvas.gettags(_id)[0] for _id in ids]

  def create_box(self, box: tuple[float, float, float, float], tagName: str):
    self.canvas.create_rectangle(*box, tag=tagName, fill='black', outline='white', width=0.1)

  def click(self, event):
    pic = 2
    tags = [self.canvas.itemcget(obj, 'tags') for obj in self.canvas.find_overlapping(*((event.x-pic, event.y-pic, event.x+pic, event.y+pic)))]
    tagName = None
    for tag in tags:
      tagName = tags[0]
      if 'current' in tag:
        return tag.replace('current', '').strip()
    return tagName

