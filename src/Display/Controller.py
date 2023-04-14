import os
from .View import (
  CreateLearningDataDialog,
  MainMenu,
  PropertyDialog,
  NetworkDialog,
  NetworkSettingDialog,
  SelectLearningDataDialog,
  TrainDialog,
  TestDialog,
  ParamDialog,
  ReviewDialog
)
import tkinter as tk
from tkinter import filedialog

class Controller:
  def __init__(self, master, model):
    self.master = master
    self.model = model
    self.menu = MainMenu(master=master, columns=model.menuColumns)
    self.networkDialog = None
    self.trainDialog = None
    self.testDialog = None
    self.bind_UI()

  def bind_UI(self):
    self.menu.setCommands({
      'network': self.overwriteNetwork,
      'review': self.openReviewNetwork,
      'property': self.openPropertyDialog,
      'train': self.openTrainDialog,
      'createData': self.openCreateLearningDataDialog,
      'test': self.openTestDataDialog,
      'save': self.saveNetwork,
      'quit': self.quit
    })

  def overwriteNetwork(self):
    isSave = False
    if os.path.isdir(self.model.basePath):
      isSave = tk.messagebox.askyesno('config', 'save network before overwrite?')
    if isSave:
      self.saveNetwork()
    
    self.openCreateNetworkDialog()

  def openCreateNetworkDialog(self):
    networkData = self.openNetworkSettingDialog().result
    if not networkData:
      return
    if self.trainDialog and self.trainDialog.winfo_exists():
      self.trainDialog.destroy()
    layers = ['input', 'hidden', 'output']
    if 'input' in networkData:
      result = self.model.newCreateNetwork(**{f'{layer}_num': int(networkData[layer]) for layer in layers})
    else:
      result = self.model.fromFileCreateNetwork(networkData)

    if self.model.isExistNetwork():
      self.menu.changeMenuMode(True)
    self.model.layerNums = list(result)
    self.openNetworkDialog(result)

  def openReviewNetwork(self):
    if not self.networkDialog.winfo_exists():
      self.openNetworkDialog(self.model.layerNums)
    updateDisplay = self.NetworkDialog.onUpdateDisplay
    return ReviewDialog(
      master=self.networkDialog,
      onUpdate=updateDisplay,
      title='Review'
    )

  def saveNetwork(self):
    fpath = self.getFilePathDialog(title='Save As', isDir=True, isSave=True)
    self.model.saveNetwork(fpath)

  def quit(self):
    if not self.model.isSaved:
      if tk.messagebox.askyesno('config', 'quit before save?'):
        return
    self.master.destroy()

  def openNetworkDialog(self, defaultLayer=[2, 2, 1]):
    if self.networkDialog and self.networkDialog.winfo_exists():
      self.networkDialog.destroy()
    self.networkDialog = tk.Toplevel(self.master)
    
    setting = self.model.readSettingFile()
    self.NetworkDialog = NetworkDialog(
      master=self.networkDialog,
      title='network',
      onUpdate=self.model.onUpdateNetworkParam,
      minimum=setting.get('error'),
      onClick=self.openParamDialog,
      defaultLayer=defaultLayer
    )
    return self.NetworkDialog

  def openParamDialog(self, tagName, onCut):
    if tagName is None:
      return
    params = [int(tag.split(':')[1]) for tag in tagName.split('-')[1:]]
    value = self.model.getParam(*params)
    if value is None:
      return
    return ParamDialog(
      self.networkDialog, 
      value, 
      title='Param', 
      isWeight=('weight' in tagName),
      onCut=lambda: self.NetworkDialog.onUpdateDisplay(lambda: self.model.onCutWeight(*params, onCut))
    )

  def openNetworkSettingDialog(self):
    dialog = NetworkSettingDialog(
      master=self.master,
      getFilePathDialog=self.getFilePathDialog,
      title='create network'
    )
    return dialog
  
  def onSelectLearningData(self, minimum, fpath):
    if not self.model.validateLearingData(fpath):
      return False
    self.model.onSelectLearningDataForTrain(fpath)
    self.NetworkDialog.setMinimumError(minimum)
    return True

  def openSelectLearningDataDialog(self, master):
    return SelectLearningDataDialog(
      master=master,
      title='learning prop',
      defaultValues={ 'path': self.model.learningDataPath, **self.model.readSettingFile() },
      getFilePathDialog=self.getFilePathDialog,
      onSelectLearningData=self.onSelectLearningData,
      writeNetworkParam=self.model.writeNetworkParam
    )

  def openCreateLearningDataDialog(self):
    return CreateLearningDataDialog(
      master=self.master,
      title='Learning Data',
      getFilePathDialog=self.getFilePathDialog,
      onLoadFile=self.model.readLearningDataFile,
      onMakeFile=self.model.makeLearningDataFile
    )

  def openTrainDialog(self):
    if self.testDialog and self.testDialog.winfo_exists():
      self.trainDialog.destroy()
    self.trainDialog = tk.Toplevel(self.master)
    updateDisplay = self.NetworkDialog.onUpdateDisplay
    return TrainDialog(
      master=self.trainDialog,
      dataPath=self.model.learningDataPath,
      onSettingData=lambda: self.openSelectLearningDataDialog(self.trainDialog),
      onLearnNetwork=lambda: self.model.onLearnNetwork(func=updateDisplay),
      onChangeTrainOperation=self.model.onChangeTrainOperation,
      onInitWeight=lambda: self.model.onInitWeight(func=updateDisplay),
      title='Train'
    )

  def openTestDataDialog(self):
    if self.testDialog and self.testDialog.winfo_exists():
      self.testDialog.destroy()
    self.testDialog = tk.Toplevel(self.master)
    
    return TestDialog(
      master=self.testDialog,
      defaultPath=self.model.testDataPath,
      onLoadData=self.model.readLearningData,
      onStartTest=self.model.startTest,
      getFilePathDialog=self.getFilePathDialog,
      onPutFile=self.model.onPutFile,
      onChangeTestIndex=lambda index: self.NetworkDialog.onUpdateDisplay(lambda: self.model.getTestAnswerByIndex(index)),
      title='Test'
    )

  def openPropertyDialog(self):
    return PropertyDialog(
      master=self.master,
      inputLength=self.model.layerNums[0],
      rowSize=self.model.inputSize,
      defaultWeightRange=self.model.colorRange,
      getFilePathDialog=self.getFilePathDialog,
      onSubmit=self.model.propertySubmit,
      referencePath=self.model.referencePath,
      onResetDisplay=self.NetworkDialog.onResetDisplay,
      title='Property'
    )
  
  def getFilePathDialog(self, title, isDir=False, isSave=False):
    types = [('CSVファイル', '*.csv'), ('テキストファイル','*.txt'), ('DATAファイル', '*.dat')]
    if isSave:
      return filedialog.asksaveasfilename(title='Save As', initialdir=self.model.referencePath, filetypes='' if isDir else types)
    if isDir:
      return filedialog.askdirectory(title=title, initialdir=self.model.referencePath)

    return filedialog.askopenfilename(filetypes=types, initialdir=self.model.referencePath)

  # def openAlertDialog(self):
  #   return AlertDialog(
  #     master=self.master,
  #     title='Alart'
  #   )