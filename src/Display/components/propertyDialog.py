import tkinter as tk
import os
from . import Frame, Button, Dialog, TextField, Label

class PropertyDialog(Dialog):
  def __init__(self, master, title=None, onSubmit=None, onResetDisplay=None):
    self.width = 744
    self.height = 364
    self.master = master
    self.onSubmit=onSubmit
    self.onResetDisplay=onResetDisplay
    super().__init__(master, title=title, width=self.width, height=self.height)

  def body(self, master):
    super().body(master, func=self._body)

  def buttonbox(self):
    super().buttonbox()

  def _body(self, master):
    bodyFrame = Frame(master, width=self.width, height=self.height)
    bodyFrame.pack(fill=tk.BOTH, anchor=tk.CENTER, padx=32, pady=16, expand=True)

    inputLayerSizeFrame = Frame(bodyFrame, width=self.width, height=64)
    inputLayerSizeFrame.pack(fill=tk.BOTH, side=tk.TOP, padx=32)
    self.inputSize = TextField(inputLayerSizeFrame, defaultValue=1, text='size of inputLayer', side=tk.LEFT, expand=True, padx=8)
    self.divideSize = Label(inputLayerSizeFrame, text='x', side=tk.RIGHT, expand=True, pady=16, padx=8)

    weightRangeFrame = Frame(bodyFrame, width=self.width, height=64)
    weightRangeFrame.pack(fill=tk.BOTH, side=tk.TOP, padx=32)
    self.weightRange = TextField(weightRangeFrame, defaultValue=8, text='weight range', side=tk.LEFT, expand=True, padx=8)
    self.weightButton = Button(weightRangeFrame, width=128, height=64, text='fix to maximum absolute', side=tk.RIGHT, anchor=tk.CENTER, expand=True, pady=16, padx=8)

    colorScaleFrame = Frame(bodyFrame, width=self.width, height=64)
    colorScaleFrame.pack(fill=tk.BOTH, side=tk.TOP, padx=32, pady=8)
  
  def apply(self):
    self.onSubmit(int(self.inputSize.get()))
    self.onResetDisplay()

    # self.targetEntry = tk.Checkbox(bodyFrame, multiple=True, side=tk.LEFT, expand=True, pady=16, padx=8)
