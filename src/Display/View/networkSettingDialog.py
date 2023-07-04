import tkinter as tk
from . import ButtonBox, Dialog, Frame, Button, Label, Entry

class NetworkSettingDialog(Dialog):
  def __init__(self, master, title=None, getFilePathDialog=None, onSubmit=None, onCancel=None):
    self.width = 520
    self.height = 240
    self.pathLabel = ''
    self.getFilePathDialog=getFilePathDialog
    self.onSubmit = onSubmit if onSubmit else self.ok
    self.onCancel = onCancel if onCancel else self.cancel
    self.onSelectFile = lambda: self.setLabel(self.selectNetwork())
    super().__init__(master, title=title, width=self.width, height=self.height)

  def body(self, master):
    super().body(master, self._body)
  
  def buttonbox(self):
    super().buttonbox(self._buttonbox)
  
  def _body(self, master):
    layerFieldFrame = Frame(master, width=480, height=160)
    layerFieldFrame.pack(fill=tk.BOTH, pady=16, padx=32, expand=True)
  
    self.inputEntry = StyledTextField(master=layerFieldFrame, width=64, defaultValue='2', text='input layer')
    # enable multiple setting for hidden layer
    self.hiddenEntry = StyledTextField(master=layerFieldFrame, width=64, defaultValue='2', text='hidden layer', multiple=False)
    self.outputEntry = StyledTextField(master=layerFieldFrame, width=64, defaultValue='1', text='output layer')

  def _buttonbox(self, master):
    self.footer = (
      { 'text': 'Create', 'width': 80, 'command': self.onSubmit },
      { 'text': 'Select File', 'width': 80, 'command': self.onSelectFile },
      { 'text': 'Cancel', 'width': 80, 'command': self.onCancel }
    )
    self.actions = ButtonBox(master=master, width=self.width, children=self.footer)

  def selectNetwork(self):
    fpath = self.getFilePathDialog(title='Load Network Directory', isDir=True)
    return fpath

  def setLabel(self, string=''):
    if string:
      self.pathLabel = string
      self.onSubmit()

  def apply(self):
    layers = {
      'input': self.inputEntry.get(),
      'hidden': self.hiddenEntry.get().strip(),
      'output': self.outputEntry.get()
    }

    self.result = None
    if self.pathLabel:
      self.result = self.pathLabel
    elif all((bool(v) and v != '0' for v in layers.values())):
      self.result = layers

class StyledTextField(Entry):
  def __init__(self, master, width=256, height=48, defaultValue='', text='', multiple=False):
    frame = Frame(master=master, width=width, height=height)
    frame.pack(fill=tk.BOTH, side=tk.TOP)

    self.label = Label(master=frame, height=height, text=text, side=tk.LEFT, expand=True, pady=8)
    super().__init__(master=frame, height=height, defaultValue=defaultValue, side=tk.RIGHT, expand=True, pady=8, multiple=multiple)
