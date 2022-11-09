import tkinter as tk
import os
from . import Frame, Button, Dialog, TextField, Label

class PropertyDialog(Dialog):
  def __init__(self, master, title, inputLength, rowSize, onSubmit=None, onResetDisplay=None):
    self.width = 744
    self.height = 364
    self.master = master
    self.inputLength = inputLength
    self.rowSize = rowSize
    self.onSubmit=onSubmit
    self.onResetDisplay=onResetDisplay
    self.init = True
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
    self.inputSize = StyledTextField(inputLayerSizeFrame, defaultValue=self.rowSize, text='size of inputLayer', onSubmit=self.setLabel, side=tk.LEFT, expand=True, padx=8)
    self.divideSize = Label(inputLayerSizeFrame, text='x', width=176, side=tk.RIGHT, pady=16, padx=8)

    weightRangeFrame = Frame(bodyFrame, width=self.width, height=64)
    weightRangeFrame.pack(fill=tk.BOTH, side=tk.TOP, padx=32)
    self.weightRange = TextField(weightRangeFrame, defaultValue=8, text='weight range', side=tk.LEFT, expand=True, padx=8)
    self.weightButton = Button(weightRangeFrame, width=176, height=64, text='fix to maximum absolute', side=tk.RIGHT, anchor=tk.CENTER, pady=16, padx=8)

    colorScaleFrame = Frame(bodyFrame, width=self.width, height=64)
    colorScaleFrame.pack(fill=tk.BOTH, side=tk.TOP, padx=32, pady=8)
    self.init = False
    self.setLabel(self.rowSize)

  def setLabel(self, rowSize):
    if self.init or rowSize == '':
      return
    colSize = float(self.inputLength/float(rowSize))
    if colSize.is_integer():
      self.text = ' x ' + str(int(colSize))
      self.colSize = colSize
      self.divideSize.setText(self.text)

  def validate(self):
    inputSize = self.inputSize.get()
    if not inputSize.isdigit():
      return False
    colSize = float(self.inputLength/float(inputSize))
    return colSize.is_integer()

  def apply(self):
    inputSize = self.inputSize.get()
    if inputSize != '':
      self.onSubmit(int(inputSize))
      self.onResetDisplay()

class StyledTextField(TextField):
  def __init__(self, master, onSubmit=False, **kwargs):
    self.onSubmit = onSubmit
    vcmd = (master.register(self.validate_inputLength))
    super().__init__(master, multiple=False, vcmd=vcmd, validate='key', **kwargs)

  def validate_inputLength(master, P):
    if P.isdigit() or P == '':
      master.onSubmit(P)
      return True
