import tkinter as tk
from . import Frame, Button, Dialog, TextField, Label

class PropertyDialog(Dialog):
  def __init__(self, master, title, inputLength, defaultWeightRange, rowSize, referencePath, getFilePathDialog=None, onSubmit=None, onResetDisplay=None):
    self.width = 744
    self.height = 364
    self.master = master
    self.inputLength = inputLength
    self.weightRange = defaultWeightRange
    self.referencePath = referencePath
    self.getFilePathDialog = getFilePathDialog
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
    
    referenceFrame = Frame(bodyFrame, width=624, height=64)
    referenceFrame.pack(fill=tk.X, pady=16, padx=48)

    self.dataPathLabel = Label(referenceFrame, width=480, text=self.referencePath, side=tk.LEFT, expand=True)
    self.dataPathButton = Button(referenceFrame, text='Browse', width=128, side=tk.RIGHT, command=self._selectDirectory)

    inputLayerSizeFrame = Frame(bodyFrame, width=self.width, height=64)
    inputLayerSizeFrame.pack(fill=tk.BOTH, side=tk.TOP, padx=32)
    self.inputSizeField = InputTextField(inputLayerSizeFrame, defaultValue=self.rowSize, text='size of inputLayer', onSubmit=self.setLabel, side=tk.LEFT, expand=True, padx=8)
    self.divideSize = Label(inputLayerSizeFrame, text='x', width=176, side=tk.RIGHT, pady=16, padx=8)

    weightRangeFrame = Frame(bodyFrame, width=self.width, height=64)
    weightRangeFrame.pack(fill=tk.BOTH, side=tk.TOP, padx=32)
    self.weightRangeField = WeightTextField(weightRangeFrame, defaultValue=self.weightRange, text='weight range', side=tk.LEFT, expand=True, padx=8)
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
    inputSize = self.inputSizeField.get()
    if not inputSize.isdigit():
      return False
    colSize = float(self.inputLength/float(inputSize))
    return colSize.is_integer()

  def _selectDirectory(self):
    fpath = self.getFilePathDialog(title='reference Directory', isDir=True)
    if fpath:
      self.referencePath = fpath
      self.dataPathLabel.setText(fpath)
  

  def apply(self):
    inputSize = self.inputSizeField.get()
    weightRange = self.weightRangeField.get()
    if '' in (inputSize, weightRange):
      return
    if self.rowSize == inputSize and self.weightRange == weightRange:
      return

    self.onResetDisplay(*self.onSubmit(self.referencePath, int(inputSize), float(weightRange)))

class InputTextField(TextField):
  def __init__(self, master, onSubmit=False, **kwargs):
    self.onSubmit = onSubmit
    vcmd = (master.register(self.validate_inputLength))
    super().__init__(master, multiple=False, vcmd=vcmd, validate='key', **kwargs)

  def validate_inputLength(master, P):
    if P.isdigit() or P == '':
      master.onSubmit(P)
      return True

class WeightTextField(TextField):
  def __init__(self, master, **kwargs):
    vcmd = (master.register(self.validate_float))
    super().__init__(master, multiple=False, vcmd=vcmd, validate='key', **kwargs)

  def validate_float(master, P):
    if P == '':
      return True
    string = P.replace('.', '', 1)
    return string.isdigit()
      

