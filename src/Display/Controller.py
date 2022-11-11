import os, shutil
import tkinter as tk
from tkinter import filedialog

class Controller:
  def __init__(self, master, model, view):
    self.master = master
    self.model = model
    self.view = view
    self.bind_UI()

  def bind_UI(self):
    self.view.menu.buttons['network']['command'] = self.overwriteNetwork
    self.view.menu.buttons['property']['command'] = self.view.openPropertyDialog
    self.view.menu.buttons['train']['command'] = self.view.openTrainDialog
    self.view.menu.buttons['createData']['command'] = self.view.openCreateLearningDataDialog
    self.view.menu.buttons['test']['command'] = self.view.openTestDataDialog
    self.view.menu.buttons['save']['command'] = self.saveNetwork
    self.view.menu.buttons['quit']['command'] = self.quit

  def overwriteNetwork(self):
    isSave = False
    if os.path.isdir(self.model.basePath):
      isSave = tk.messagebox.askyesno('config', 'save network before overwrite?')
    if isSave:
      self.saveNetwork()
    
    self.openNetworkSettingDialog()

  def openNetworkSettingDialog(self):
    networkData = self.view.openNetworkSettingDialog().result
    if not networkData:
      return
    layers = ['input', 'hidden', 'output']
    if 'input' in networkData:
      result = self.model.newCreateNetwork(**{f'{layer}_num': int(networkData[layer]) for layer in layers})
    else:
      result = self.model.fromFileCreateNetwork(networkData)

    if self.model.isExistNetwork():
      self.view.menu.changeMenuMode(True)
    self.model.layerNums = list(result)
    self.view.openNetworkDialog(result)

  def saveNetwork(self):
    fpath = filedialog.asksaveasfilename(title='Save As')
    self.model.saveNetwork(fpath)

  def quit(self):
    isSave = False
    if os.path.isdir(self.model.basePath):
      isSave = tk.messagebox.askyesno('config', 'quit before save?')
    if isSave:
      self.master.destroy()

