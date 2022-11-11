from .components import (
  CreateLearningDataDialog,
  MainMenu,
  PropertyDialog,
  NetworkDialog,
  NetworkSettingDialog,
  SelectLearningDataDialog,
  TrainDialog,
  TestDialog,
  ParamDialog
)
import tkinter as tk

class View:
  def __init__(self, master, model):
    self.master = master
    self.model = model
    self.menu = MainMenu(master=master, columns=model.menuColumns)
    self.networkDialog = None
    self.trainDialog = None
    self.testDialog = None

  def openNetworkDialog(self, defaultLayer=[2, 2, 1]):
    if self.networkDialog:
      self.networkDialog.destroy()
    self.networkDialog = tk.Toplevel(self.master)
    self.NetworkDialog = NetworkDialog(
      master=self.networkDialog,
      title='network',
      onUpdate=self.model.onUpdateNetworkParam,
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
      title='create network'
    )
    return dialog

  def openSelectLearningDataDialog(self, master):
    return SelectLearningDataDialog(
      master=master,
      title='learning prop',
      defaultPath=self.model.learningDataPath,
      onSelectLearningData=self.model.onSelectLearningDataForTrain,
      writeNetworkParam=self.model.writeNetworkParam
    )

  def openCreateLearningDataDialog(self):
    return CreateLearningDataDialog(
      master=self.master,
      title='Learning Data',
      onLoadFile=self.model.readLearningDataFile,
      onMakeFile=self.model.makeLearningDataFile
    )

  def openTrainDialog(self):
    if self.trainDialog:
      self.trainDialog.destroy()
    self.trainDialog = tk.Toplevel(self.master)
    updateDisplay = self.NetworkDialog.onUpdateDisplay
    return TrainDialog(
      master=self.trainDialog,
      dataPath=self.model.learningDataPath,
      onSettingData=lambda : self.openSelectLearningDataDialog(self.trainDialog),
      onLearnNetwork=lambda flag: self.model.onLearnNetwork(flag, func=updateDisplay),
      onInitWeight=lambda: self.model.onInitWeight(func=updateDisplay),
      title='Train'
    )

  def openTestDataDialog(self):
    if self.testDialog:
      self.testDialog.destroy()
    self.testDialog = tk.Toplevel(self.master)
    
    return TestDialog(
      master=self.testDialog,
      defaultPath=self.model.testDataPath,
      onLoadData=self.model.readLearningData,
      onStartTest=self.model.startTest,
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
      onSubmit=self.model.propertySubmit,
      onResetDisplay=self.NetworkDialog.onResetDisplay,
      title='Property'
    )
  # def openAlertDialog(self):
  #   return AlertDialog(
  #     master=self.master,
  #     title='Alart'
  #   )