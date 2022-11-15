import tkinter as tk
from . import Button, Frame, ButtonBox, Dialog, Label

class ParamDialog(Dialog):
  def __init__(self, master, param, title=None, onCut=None, isWeight=True):
    self.width = 400
    self.height = 200
    self.param = param
    self.onCut = onCut
    self.isWeight = isWeight
    super().__init__(master, title=title, width=self.width, height=self.height)
 
  def body(self, master):
    super().body(master, self._body)
  
  def buttonbox(self):
    super().buttonbox(self._buttonbox)
  
  def _body(self, master):
    root = Frame(master, width=320, height=200)
    root.pack(fill=tk.BOTH, ipadx=16, pady=8, padx=48)

    labelFrame = Frame(root, width=320, height=64)
    labelFrame.pack(fill=tk.BOTH, ipadx=16, padx=48)
    self.paramLabel = Label(labelFrame, text='重み' if self.isWeight else '閾値', side=tk.LEFT)
    self.valueLabel = Label(labelFrame, text='{:.3f}'.format(self.param), side=tk.RIGHT)

    if self.isWeight:
      self.cutButton = Button(root, text='結合を切断', width=80, side=tk.BOTTOM, command=self.onClick, expand=True)
    
  def onClick(self):
    self.onCut()
    self.valueLabel.setText('0')
  
  def _buttonbox(self, master):
    self.footer = [
      { 'text': 'ok', 'command': self.ok }
    ]
    self.actions = ButtonBox(master, width=self.width, height=64, children=self.footer, padx=48)
