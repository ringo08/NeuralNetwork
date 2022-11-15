import tkinter as tk
import os
from src.Display import Controller, Model, Messages
from config.settingConfig import update
from configparser import ConfigParser, ExtendedInterpolation

class Application(tk.Frame):
  def __init__(self, master, config):
    super().__init__(master)
    master.title("NNApp")
    master.geometry('240x560')
    master.resizable(width=False, height=False)
    master.configure(bg='#FAFAFA')
    self.config(bg='#FAFAFA')
    self.configProp = config

    self.messages = Messages.Messages
    self.model = Model.Model(config, onError=self.onError)
    self.controller = Controller.Controller(master, self.model)
    self.pack(fill='both', expand=True)

  # def __del__(self):
  #   with open(self.configProp['Paths']['operation'], 'wt', encoding='utf-8') as f:
  #     print(self.configProp['Operate']['close'], file=f)

  def onError(self, text):
    tk.messagebox.showwarning('Error', text)

def main():
  config = ConfigParser(interpolation=ExtendedInterpolation())
  path_root = os.getcwd()
  path_config = os.path.join(path_root, 'config/config.ini')

  update(config, { 'Paths': {'root': path_root }}, path_config)
  config.read(path_config)

  root = tk.Tk()
  myapp = Application(root, config)
  myapp.mainloop()

if __name__ == '__main__':
  main()
