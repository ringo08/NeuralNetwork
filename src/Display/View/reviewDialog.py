import tkinter as tk
from . import Frame, Dialog, Label

class ReviewDialog(Dialog):
  def __init__(self, master, title, onUpdate=None, maxScale=0):
    self.width = 744
    self.height = 364
    self.master = master
    self.maxScale = maxScale
    self.onUpdate = onUpdate
    self.epoch = 0
    self.loss = 0
    super().__init__(master, title=title, width=self.width, height=self.height)

  def body(self, master):
    super().body(master, func=self._body)

  def buttonbox(self):
    super().buttonbox()

  def _body(self, master):
    bodyFrame = Frame(master, width=self.width, height=self.height)
    bodyFrame.pack(fill=tk.BOTH, anchor=tk.CENTER, padx=32, pady=16, expand=True)
    
    viewFrame = Frame(bodyFrame, width=624, height=64)
    viewFrame.pack(fill=tk.X, pady=16, padx=48)

    self.lossLabel = Label(viewFrame, width=480, text=f'loss: {self.loss}', side=tk.TOP, expand=True)
    self.epochLabel = Label(viewFrame, width=480, text=f'epoch: {self.epoch}', side=tk.TOP, expand=True)

    scaleFrame = Frame(bodyFrame, width=self.width, height=64)
    scaleFrame.pack(fill=tk.BOTH, side=tk.TOP, padx=32, pady=8)
    
    self.select = tk.IntVar()
    self.scale = tk.Scale(
      scaleFrame, 
      variable = self.select,
      orient=tk.HORIZONTAL,
      length = 300,
      width = 20,
      to = self.maxScale,
      tickinterval=10
    )
    self.scale.bind("<ButtonRelease-1>", self.onScroll)
    self.scale.pack()

  def onScroll(self, e):
    index = int(self.select.get())
    loss = self.onUpdate(index=index)
    if not loss:
      return
    loss = loss[index]
    self.epoch = index
    self.loss = loss
    self.lossLabel.setText(f'loss: {self.loss}')
    self.epochLabel.setText(f'epoch: {self.epoch}')
    
