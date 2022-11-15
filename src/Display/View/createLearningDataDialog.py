import tkinter as tk
from tkinter import filedialog
import os
from . import Frame, Button, Dialog, Entry, Listbox, ButtonBox, Label

class CreateLearningDataDialog(Dialog):
  def __init__(self, master, title=None, onLoadFile=None, onMakeFile=None):
    self.width = 976
    self.height = 428
    self.master = master
    self.selectIndex = None
    self.onLoadFile = onLoadFile
    self.onMakeFile = onMakeFile
    super().__init__(master, title=title, width=self.width, height=self.height)

  def body(self, master):
    super().body(master, func=self._body)

  def buttonbox(self):
    super().buttonbox(func=self._buttonbox)

  def _body(self, master):
    inputFrame = Frame(master, width=944, height=64)
    inputFrame.pack(fill=tk.X, anchor=tk.CENTER, padx=32, ipady=4, pady=16)

    self.inputEntry = Entry(inputFrame, multiple=True, side=tk.LEFT, expand=True, pady=16, padx=8)
    self.targetEntry = Entry(inputFrame, multiple=True, side=tk.LEFT, expand=True, pady=16, padx=8)

    entryButtonsFrame = Frame(inputFrame, width=240, height=48)
    entryButtonsFrame.pack(side=tk.LEFT, expand=True)
    self.addButton = HeaderButton(entryButtonsFrame, text='add', command=self.addData)
    self.replaceButton = HeaderButton(entryButtonsFrame, text='overwrite', padx=0, command=self.replaceListItem)
    self.eraseButton = HeaderButton(entryButtonsFrame, text='erase', command=self.eraseData)

    dataFrame = Frame(master, width=944, height=360)
    dataFrame.pack(fill=tk.BOTH, anchor=tk.CENTER, expand=True, padx=32)

    self.inputList = Listbox(dataFrame, side=tk.LEFT, expand=True, padx=8)
    self.inputList.bind("<<ListboxSelect>>", self.selectListItem)
    self.targetList = Listbox(dataFrame, side=tk.LEFT, expand=True, padx=8)
    self.targetList.bind("<<ListboxSelect>>", self.selectListItem)

    editButtonsFrame = Frame(dataFrame, width=240, height=360)
    editButtonsFrame.pack(side=tk.LEFT, expand=True)

    self.deleteButton = Button(editButtonsFrame, width=80, text='delete', side=tk.BOTTOM, command=self.deleteListItem)
    self.editButton = Button(editButtonsFrame, width=80, text='edit list item', command=self.setListItem, side=tk.BOTTOM)
  
  def _buttonbox(self, master):
    props = { 'width': 200, 'side': tk.LEFT, 'anchor': tk.CENTER }
    cancelProps = { **props, 'width': 64 }
    self.footer = [
      { 'text': 'load learning data', **props, 'command': self.loadLearningData },
      { 'text': 'make learning data', **props, 'command': self.makeLearningData },
      { 'text': 'pattern editor', **props },
      { 'text': 'cancel', **cancelProps, 'command': self.cancel }
    ]
    self.actions = ButtonBox(master=master, width=self.width, children=self.footer, padx=32)

  def loadLearningData(self):
    fpath = self._selectLoadFile()
    if not fpath:
      return
    data = self.onLoadFile(fpath)
    if not data:
      return
    inputData, targetData = tuple(data)
    if not (inputData and targetData):
      return
    self.inputList.clearItems()
    self.targetList.clearItems()
    for idata in inputData:
      self.inputList.insert(tk.END, ' '.join([str(d) for d in idata]))
    for tdata in targetData:
      self.targetList.insert(tk.END, ' '.join([str(d) for d in tdata]))

  def makeLearningData(self):
    inputData = self.inputList.getItems()
    targetData = self.targetList.getItems()
    data = { 'input': inputData, 'target': targetData } 
    f = lambda lists: all([len(lists[0].strip().split(' ')) == len(l.strip().split(' ')) for l in lists])
    if not (f(targetData) and f(inputData)):
      self.master.onError('input or target length are disagreement')
      return

    data = { 'input': inputData, 'target': targetData }
    fpath = self._selectSaveFile()
    if not fpath:
      return
    self.onMakeFile(fpath, data)

  def _selectSaveFile(self):
    typ = [('CSVファイル', '*.csv'), ('テキストファイル','*.txt'), ('DATAファイル', '*.dat')] 
    iDir = os.path.abspath(os.path.dirname(__file__))
    fpath = filedialog.asksaveasfilename(filetypes=typ, initialdir=iDir)
    return fpath

  def _selectLoadFile(self):
    typ = [('CSVファイル', '*.csv'), ('テキストファイル','*.txt'), ('DATAファイル', '*.dat')] 
    iDir = os.path.abspath(os.path.dirname(__file__))
    fpath = filedialog.askopenfilename(filetypes=typ, initialdir=iDir)
    return fpath
  
  def setListItem(self):
    if self.selectIndex == None:
      return
    inputData = self.inputList.get(self.selectIndex)
    targetData = self.targetList.get(self.selectIndex)
    if inputData and targetData:
      self.inputEntry.set(inputData)
      self.targetEntry.set(targetData)

  def selectListItem(self, event):
    selection = event.widget.curselection()

    inputSelection = self.inputList.curselection()
    targetSelection = self.targetList.curselection()
    if (inputSelection == targetSelection) or not selection:
      return
    index = selection[0]
    if self.selectIndex != None:
      self.inputList.itemconfig(self.selectIndex, bg='white')
      self.targetList.itemconfig(self.selectIndex, bg='white')
    self.inputList.itemconfig(index, bg='cyan')
    self.targetList.itemconfig(index, bg='cyan')
    if self.selectIndex != index:
      self.inputList.select_set(index)
      self.targetList.select_set(index)
      self.selectIndex = index

  def deleteListItem(self, index=None):
    if self.selectIndex == None:
      return
    _index = index if index != None else self.selectIndex
    self.inputList.delete(_index)
    self.targetList.delete(_index)
    self.selectIndex = None

  def replaceListItem(self):
    index = self.selectIndex
    if index == None:
      return
    self.deleteListItem(index)
    self.addData(index)

  def eraseData(self):
    self.inputEntry.set('')
    self.targetEntry.set('')

  def addData(self, index=None):
    inputData = self.inputEntry.get()
    targetData = self.targetEntry.get()
    if not (inputData and targetData):
      return
    _index = index if index != None else tk.END
    self.inputList.insert(_index, inputData)
    self.targetList.insert(_index, targetData)

class HeaderButton(Button):
  def __init__(self, master, text='', width=80, height=48, padx=8, command=None):
    frame = Frame(master, width=width, height=height)
    super().__init__(frame, text=text, padx=padx, command=command)
    frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
