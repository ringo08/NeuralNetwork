import tkinter as tk
import os
from . import Button, Frame, DialogFrame

class TrainDialog(DialogFrame):
  def __init__(self, master, title=None, dataPath='', onSettingData=None, onChangeTrainOperation=None, onLearnNetwork=None, onInitWeight=None):
    self.width = 196
    self.height = 200
    self.master = master
    self.isStartTrain = False
    self.onSettingData = onSettingData
    self.dataPath = dataPath
    self.updateTime = 100
    self.onChangeTrainOperation = onChangeTrainOperation
    self.onLearnNetwork = onLearnNetwork
    self.onInitWeight = onInitWeight
    self.afterId = None
    super().__init__(master, title=title, width=self.width, height=self.height)

  def init_body(self, master):
    super().init_body(master, func=self._init_body)

  def init_footer(self):
    super().init_footer(func=self._init_footer)

  def _init_body(self, master):
    root = Frame(master, width=self.width, height=self.height)
    self.settingButton = Button(root, text='setting', side=tk.TOP, expand=True, command=self.isSelectLearningData)
    self.trainButton = Button(root, text='train', side=tk.TOP, expand=True, command=self.onClick)
    self.trainButton['state'] = tk.NORMAL if os.path.isfile(self.dataPath) else tk.DISABLED
    self.initWeightButton = Button(root, text='init weight', side=tk.TOP, expand=True, command=self.isInitWeight)
    self.closeButton = Button(root, text='close', side=tk.TOP, expand=True, command=self.master.destroy)
    root.pack(fill=tk.BOTH, anchor=tk.CENTER, side=tk.TOP, padx=16)
  
  def onClick(self):
    self.isStartTrain = self.onChangeTrainOperation(not self.isStartTrain)
    self.onToggle()
  
  def onToggle(self):
    self.isStartTrain = self.onLearnNetwork()
    if self.isStartTrain:
      self.trainButton.setLabel('stop')
      self.afterId = self.after(self.updateTime, self.onToggle)
    elif self.afterId is not None:
      self.after_cancel(self.afterId)
      self.afterId = None
      self.trainButton.setLabel('train')
    else:
      self.trainButton.setLabel('train')
    self.initWeightButton['state'] = tk.DISABLED if self.isStartTrain else tk.NORMAL
    
  def _init_footer(self, master):
    pass

  def isSelectLearningData(self):
    self.dataPath = self.onSettingData().dataPath
    self.trainButton['state'] = tk.NORMAL if self.dataPath else tk.DISABLED

  def isInitWeight(self):
    result = tk.messagebox.askquestion('override weight', 'can you override all weights in this network')
    if result == 'yes':
      self.onInitWeight()