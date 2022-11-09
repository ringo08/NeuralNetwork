import tkinter as tk
import os
from . import Button, Frame, ButtonBox, Entry, Dialog, Label

class SelectLearningDataDialog(Dialog):
  def __init__(self, master, title=None, defaultPath='', writeNetworkParam=None, onSelectLearningData=None):
    self.width = 752
    self.height = 380
    self.dataPath = defaultPath
    self.writeNetworkParam = writeNetworkParam
    self.onSelectLearningData = onSelectLearningData
    super().__init__(master, title=title, width=self.width, height=self.height)
 
  def body(self, master):
    super().body(master, self._body)
  
  def buttonbox(self):
    super().buttonbox(self._buttonbox)
  
  def _body(self, master):
    self.learningData = Frame(master, width=624, height=48)
    self.learningData.pack(fill=tk.X, ipady=4, ipadx=16, pady=16, padx=48)

    self.dataPathButton = Button(self.learningData, text='Browse', width=128, side=tk.RIGHT, command=lambda: self.dataPathLabel.setText(self._selectLearningDataFile()))
    self.dataPathLabel = Label(self.learningData, text=self.dataPath if self.dataPath else 'no data', side=tk.LEFT, expand=True)

    paramFrame = Frame(master, width=624, height=256)
    paramFrame.pack(fill=tk.BOTH, padx=48, pady=8, ipady=16, ipadx=16, expand=True)
  
    self.minimum = StyledTextField(master=paramFrame, text='minimum error', defaultValue=1e-5, bindText='1e-')
    self.epochs = StyledTextField(master=paramFrame, text='epochs', defaultValue=100)
    self.updateFrequency = StyledTextField(master=paramFrame, text='update frequency', defaultValue=100)
    self.updateInterval = StyledTextField(master=paramFrame, text='update interval', defaultValue=2)
  
  def _buttonbox(self, master):
    self.footer = [
      { 'text': 'ok', 'command': self.ok },
      { 'text': 'cancel', 'command': self.cancel }
    ]
    self.actions = ButtonBox(master, width=self.width, height=64, children=self.footer, padx=48)

  def _selectLearningDataFile(self):
    typ = [('CSVファイル', '*.csv'), ('テキストファイル','*.txt'), ('DATAファイル', '*.dat')] 
    iDir = os.path.abspath(os.path.dirname(__file__))
    fpath = tk.filedialog.askopenfilename(filetypes=typ, initialdir=iDir)
    return fpath

  def apply(self):
    self.writeNetworkParam({
      'error': self.minimum.get(),
      'epoch': self.epochs.get(),
      'freq': self.updateFrequency.get(),
      'interval': self.updateInterval.get()
    })
    self.onSelectLearningData(self.dataPathLabel.getText())

class StyledTextField(Entry):
  def __init__(self, master, width=256, height=48, text='', defaultValue=0, bindText=''):
    frame = Frame(master=master, width=width, height=height)
    frame.pack(fill=tk.BOTH, side=tk.TOP)

    self.label = Label(master=frame, height=height, text=text, side=tk.LEFT, expand=True, pady=8)
    super().__init__(master=frame, height=height, side=tk.RIGHT, expand=True, pady=8, defaultValue=str(defaultValue), bindText=bindText)

