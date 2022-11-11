import tkinter as tk
import os
from . import Button, Frame, DialogFrame, Label

class TestDialog(DialogFrame):
  def __init__(self, master, title, defaultPath, onLoadData=None, onStartTest=None, onChangeTestIndex=None, onPutFile=None):
    self.width = 376
    self.height = 440
    self.testIndex = 0
    self.maxIndex = 0
    self.testDataPath = defaultPath
    self.onLoadData = onLoadData
    self.onChangeTestIndex = onChangeTestIndex
    self.onStartTest = onStartTest
    self.onPutFile = onPutFile
    self.master = master
    super().__init__(master, title=title, width=self.width, height=self.height)

  def init_body(self, master):
    super().init_body(master, self._init_body)
  
  def init_footer(self):
    super().init_footer(self._init_footer)
    
  def onSetIndex(self, number):
    if number >= self.maxIndex:
      self.testIndex = self.maxIndex-1
    elif number < 0:
      self.testIndex = 0
    else:
      self.testIndex = number
    self.onChangeTestIndex(self.testIndex)
    self.indexLabel.setText(f'{self.testIndex+1}/{self.maxIndex}')
  
  def onStart(self):
    self.onLoadData(self.fileLabel.getText())
    self.maxIndex = self.onStartTest()
    self.indexLabel.setText(f'1/{self.maxIndex}')
  
  def _init_body(self, master):
    initButtonsFrame = Frame(master, width=276, height=200)
    initButtonsFrame.pack(side=tk.TOP, anchor=tk.CENTER, pady=(24, 8), padx=32)

    defaultText = self.testDataPath if self.testDataPath else 'no file path'
    self.fileLabel = Label(initButtonsFrame, text=defaultText, width=276, side=tk.TOP, expand=True)
    self.loadData = Button(initButtonsFrame, text='load data', side=tk.TOP, command=lambda: self.fileLabel.setText(self._selectLearningDataFile()))
    self.startTest = Button(initButtonsFrame, text='start', height=64, side=tk.LEFT, expand=True, command=self.onStart)
    self.closeTest = Button(initButtonsFrame, text='close', height=64, side=tk.LEFT, expand=True, command=self.master.destroy)

    dataFrame = Frame(master, width=276, height=200)
    dataFrame.pack(anchor=tk.CENTER, fill=tk.BOTH, ipady=8, padx=16, pady=8, expand=True)
    
    self.indexLabel = Label(dataFrame, text='no data', expand=True)
    buttons = Frame(dataFrame, width=276, height=64)
    self.firstButton = Button(buttons, text='first', side=tk.LEFT, expand=True, command=lambda: self.onSetIndex(0))
    self.prevButton = Button(buttons, text='prev', side=tk.LEFT, expand=True, command=lambda: self.onSetIndex(self.testIndex-1))
    self.nextButton = Button(buttons, text='next', side=tk.LEFT, expand=True, command=lambda: self.onSetIndex(self.testIndex+1))
    self.lastButton = Button(buttons, text='last', side=tk.LEFT, expand=True, command=lambda: self.onSetIndex(self.maxIndex-1))
    buttons.pack(fill=tk.BOTH, anchor=tk.CENTER, side=tk.TOP)
  
    self.showAllButton = Button(dataFrame, text='show all', side=tk.TOP)
    self.putFileButton = Button(dataFrame, text='put file', side=tk.TOP, command=lambda: self.onPutFile(self._selectPutFile()))
  
  def _init_footer(self, master):
    pass
  
  def _selectLearningDataFile(self):
    typ = [('CSVファイル', '*.csv'), ('テキストファイル','*.txt'), ('DATAファイル', '*.dat')] 
    iDir = os.path.abspath(os.path.dirname(__file__))
    fpath = tk.filedialog.askopenfilename(filetypes=typ, initialdir=iDir)
    return fpath

  def _selectPutFile(self):
    fpath = tk.filedialog.asksaveasfilename(title='Save As')
    if fpath != '':
      return fpath
    


