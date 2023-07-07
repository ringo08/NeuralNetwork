import os, shutil
from src.NNApp import NNApp
from src.NNApp.NeuralNetwork import *
from src.File import File
from . import Messages
from multiprocessing import Process
from config.settingConfig import configUpdate
from configparser import ConfigParser

def is_num(s):
  try:
    float(s)
  except ValueError:
    return False
  else:
    return True

class Model:
  def __init__(self, config: ConfigParser, onError=None):
    self.config = config
    self.onError = onError
    self.file = File(config, onError)
    self.NNApp = NNApp(config)
    self.process = None
    self.loadIndexMemory = 0
    self.testMaxIndex = 0
    self.inputSize = 1
    self.colorRange = 2
    self.isSaved = True
    self.learningDataPath: str = ''
    self.testDataPath: str = ''
    self.basePath = self.config['Paths']['data']
    self.referencePath = self.config['Paths']['reference']
    self.network: Network = ()
    self.dataPath = { key: self.config['Paths'][key] for key in self.config['Datas'] }
    self.messages = Messages.Messages(config)
    self.menuColumns = (
      { 'value': 'network', 'label': self.messages.get('menu.network'), 'always': True },
      { 'value': 'review', 'label': self.messages.get('menu.review'), 'always': False },
      { 'value': 'createData', 'label': self.messages.get('menu.createData'), 'always': True },
      { 'value': 'train', 'label': self.messages.get('menu.train'), 'always': False },
      { 'value': 'test', 'label': self.messages.get('menu.test'), 'always': False },
      { 'value': 'save', 'label': self.messages.get('menu.save'), 'always': False },
      { 'value': 'property', 'label': self.messages.get('menu.property'), 'always': False },
      { 'value': 'quit', 'label': self.messages.get('menu.quit'), 'always': True } 
    )
    self.sep = ','

  def close(self):
    if self.process:
      self.process.terminate()
      self.process = None

  def saveNetwork(self, toPath: str):
    isSaved = self.file.save_network(toPath)
    if isSaved:
      self.isSaved = True

  def overwriteNetwork(self, toPath: str=''):
    return self.file.overwrite_network(toPath)

# Create Network
  def createNetwork(self, out=False):
    if self.process:
      self.process.terminate()
      self.process = None
    self.file.write_operation('init')
    self.network = self.NNApp.create_network(out=out)
    self.isSaved = False

  # Create network new
  def newCreateNetwork(self, input_num=2, hidden_num=2, output_num=1):
    self.file.make_network_folder()
    self.file.create_header(input_num, hidden_num, output_num)
    self.file.create_outputfile_header(input_num, hidden_num, output_num)
    self.createNetwork(True)
    return self.network

  # Create network from file
  def fromFileCreateNetwork(self, fromPath: str):
    if not (fromPath and os.path.isdir(fromPath)):
      self.onError('not found directory path')
    self.file.copy_network(fromPath)
    self.createNetwork()
    if len(self.network) > 3:
      self.onError('require layer length > 3')
    return self.network

  def isExistNetwork(self):
    return bool(self.NNApp.network)

# Create Learning Data
  # Make learning data
  def makeLearningDataFile(self, fpath: str, data: dict):
    self.file.make_learning_data(fpath, data)

  # Load learning data
  def readLearningDataFile(self, fpath: str):
    learning_data = self.file.read_learning_data(fpath)
    if learning_data is False:
      return
    _, input_data, target_data = learning_data
    return input_data, target_data

# Train Setting Dialog Function
  # Set training params
  def writeNetworkParam(self, data: dict):
    self.file.write_network_param(data)

  def onChangeTrainOperation(self, flag: bool):
    if self.file.is_operation('end'):
      return False
    if not (os.path.isfile(self.dataPath['learning'])):
      self.onError('learning data file was not found')
      return

    self.file.write_operation('start' if flag else 'stop')
    if flag and not self.process:
      if not self.NNApp.network:
        self.onError('create Neural Network before train')
        return
      self.process = Process(target=initNNApp, args=(self.NNApp, ))
      self.process.start()

  # Start train network
  def onLearnNetwork(self, func=None):
    if self.file.is_operation('end'):
      func(index=-1)
      self.process.terminate()
      return False
    func()
    return self.file.is_operation('start')
  
  def onUpdateNetworkParam(self, fileIndex: int=None):
    return self.file.read_network_param(file_index=fileIndex)

  # Select learning data for train
  def onSelectLearningDataForTrain(self, fpath: str):
    if not fpath:
      return False
    self.learningDataPath = fpath
    if not self.file.validate_learning_data(fpath):
      return False
    return self.file.select_train_file(fpath)
  
  # Load setting data file
  def readSettingFile(self):
    return self.file.read_setting_file(self.dataPath['setting'])

  def onInitWeight(self, func):
    if self.isExistNetwork():
      if self.process:
        self.process.terminate()
        self.process = None
      self.NNApp.init_weight()
      self.file.write_operation('init')
      func()

# Test Dialog Functions
  def readTestData(self, fpath: str):
    self.testDataPath = fpath
    self.file.validate_learning_data(fpath)
    self.testMaxIndex = self.NNApp.set_test_data(fpath)

  def startTest(self):
    self.NNApp.create_network(readFile=self.dataPath['parameter'], out=False)
    self.testAnswers = tuple([self.NNApp.test(i) for i in range(self.testMaxIndex)])
    return len(self.testAnswers)

  def getTestAnswerByIndex(self, index: int):
    items = self.testAnswers[index]
    if not items:
      return
    outs, weights, datas = items
    return tuple([True, [], tuple([datas[0], *outs[1:], datas[1]]), weights])
  
  def onPutFile(self, fpath: str):
    if not (fpath and self.testDataPath):
      return
    self.file.put_result_file(self.testAnswers, self.testDataPath, fpath)

# Property Dialog
  def propertySubmit(self, dirpath: str, inputSize: str, colorRange: float):
    if self.file.property_submit(dirpath):
      self.referencePath = dirpath
    self.inputSize = inputSize
    self.colorRange = colorRange
    return self.inputSize, self.colorRange

  def getParam(self, layer: Layer, neuron: Neuron, weight=None):
    if layer == 0:
      return None
    _, weights, biases = self.file.read_network_file(file_index=-1)
    return biases[layer-1][neuron] if weight is None else weights[layer-1][neuron][weight]

  def onCutWeight(self, layer: Layer, neuron: Neuron, weight=None, onCut=None):
    if weight is None:
      return
    if self.NNApp.cut_combining(layer, neuron, weight):
      onCut()
      return self.onUpdateNetworkParam(-1)
  
def initNNApp(app):
  app.train_setting()
  app.train_network()
