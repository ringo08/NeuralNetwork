import tkinter as tk
from . import ButtonBox, Dialog, Frame, Button, Label, Entry

class NetworkSettingDialog(Dialog):
  def __init__(self, master, title=None, getFilePathDialog=None, onSubmit=None, onCancel=None):
    self.width = 752
    self.height = 320
    self.pathLabel = ''
    self.getFilePathDialog=getFilePathDialog
    self.onSubmit = onSubmit if onSubmit else self.ok
    self.onCancel = onCancel if onCancel else self.cancel
    super().__init__(master, title=title, width=self.width, height=self.height)

  def body(self, master):
    super().body(master, self._body)
  
  def buttonbox(self):
    super().buttonbox(self._buttonbox)
  
  def _body(self, master):
    pathFrame = Frame(master, width=624, height=48)
    pathFrame.pack(fill=tk.BOTH, pady=8, padx=32)

    self.label = Label(pathFrame, text=self.pathLabel if self.pathLabel else 'no file path', fontSize=12, anchor=tk.CENTER, side=tk.LEFT, expand=True)
    self.cancelPathButton = Button(pathFrame, text='Del', width=80, side=tk.RIGHT, command=lambda: self.setLabel(''))
    self.selectPathButton = Button(pathFrame, text='From File', width=80, side=tk.RIGHT, command=lambda: self.setLabel(self.selectNetwork()))

    layerFieldFrame = Frame(master, width=624, height=160)
    layerFieldFrame.pack(fill=tk.BOTH, pady=8, padx=32, expand=True)
  
    self.inputEntry = StyledTextField(master=layerFieldFrame, defaultValue='2', text='input layer')
    self.hiddenEntry = StyledTextField(master=layerFieldFrame, defaultValue='2', text='hidden layer', multiple=True)
    self.outputEntry = StyledTextField(master=layerFieldFrame, defaultValue='1', text='output layer')

  def _buttonbox(self, master):
    self.footer = [
      { 'text': 'Create', 'width': 80, 'command': self.onSubmit },
      { 'text': 'cancel', 'width': 80, 'command': self.onCancel }
    ]
    self.actions = ButtonBox(master=master, width=self.width, children=self.footer)

  def selectNetwork(self):
    fpath = self.getFilePathDialog(title='Load Network Directory', isDir=True)
    return fpath

  def setLabel(self, string=''):
    if string:
      self.label.setText(string)
      self.inputEntry['state'] = tk.DISABLED
      self.hiddenEntry['state'] = tk.DISABLED
      self.outputEntry['state'] = tk.DISABLED
      self.pathLabel = string
    else:
      self.label.setText('no file path')
      self.pathLabel = ''
      self.inputEntry['state'] = tk.NORMAL
      self.hiddenEntry['state'] = tk.NORMAL
      self.outputEntry['state'] = tk.NORMAL

  def apply(self):
    layers = {
      'input': self.inputEntry.get(),
      'hidden': self.hiddenEntry.get().strip(),
      'output': self.outputEntry.get()
    }

    self.result = None
    if self.pathLabel:
      self.result = self.pathLabel
    elif all([v for v in layers.values()]):
      self.result = layers

class StyledTextField(Entry):
  def __init__(self, master, width=256, height=48, defaultValue='', text='', multiple=False):
    frame = Frame(master=master, width=width, height=height)
    frame.pack(fill=tk.BOTH, side=tk.TOP)

    self.label = Label(master=frame, height=height, text=text, side=tk.LEFT, expand=True, pady=8)
    super().__init__(master=frame, height=height, defaultValue=defaultValue, side=tk.RIGHT, expand=True, pady=8, multiple=multiple)
