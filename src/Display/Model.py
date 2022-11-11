import os, shutil
from ..NNApp import NNApp
from . import Messages
from multiprocessing import Process
from config.settingConfig import update

def is_num(s):
  try:
    float(s)
  except ValueError:
    return False
  else:
    return True

class Model:
  def __init__(self, config, onError=None):
    self.config = config
    self.onError = onError
    self.NNApp = NNApp(config)
    self.process = None
    self.layerNums = []
    self.loadIndexMemory = 0
    self.testMaxIndex = 0
    self.inputSize = 1
    self.colorRange = 2
    self.learningDataPath = ''
    self.testDataPath = ''
    self.basePath = self.config['Paths']['data']
    self.network = []
    self.dataPath = { key: self.config['Paths'][key] for key in self.config['Datas'] }
    self.messages = Messages.Messages(config)
    self.menuColumns = [
      { 'value': 'network', 'label': self.messages.get('menu.network'), 'always': True },
      { 'value': 'onehot', 'label': self.messages.get('menu.onehot'), 'always': False },
      { 'value': 'createData', 'label': self.messages.get('menu.createData'), 'always': True },
      { 'value': 'train', 'label': self.messages.get('menu.train'), 'always': False },
      { 'value': 'test', 'label': self.messages.get('menu.test'), 'always': False },
      { 'value': 'save', 'label': self.messages.get('menu.save'), 'always': False },
      { 'value': 'property', 'label': self.messages.get('menu.property'), 'always': False },
      { 'value': 'quit', 'label': self.messages.get('menu.quit'), 'always': True } 
    ]
    self.sep = ','

  def __del__(self):
    if self.process:
      print('process kill')
      self.process.terminate()

  def _read_file(self, path):
    if not os.path.isfile(path):
      self.onError('Not exist file')
      return False
    with open(path, 'rt', encoding='utf-8') as f:
      text = f.readlines()
    return text

  def _output_file(self, fpath, string, write_type='at'):
    with open(fpath, write_type, encoding='utf-8') as file:
      print(string, file=file)

  def _print_bw(self, text, front_num, back_num=1):
    array = []
    for b in range(back_num):
      array.extend([f'{text}{b+1}-b' if f == 0 else f'{text}{b+1}-w{f}' for f in range(front_num+1)])
    return ','.join(array)
  
  def _makeBaseDir(self):
    if os.path.isdir(self.basePath):
      shutil.rmtree(self.basePath)
    if not os.path.isdir(self.basePath):
      os.mkdir(self.basePath)

  def saveNetwork(self, toPath):
    if toPath and os.path.isdir(self.basePath):
      try:
        shutil.copytree(self.basePath, toPath, dirs_exist_ok=True)
      except Exception as e:
        self.onError(e)

  def copyNetwork(self, fromPath):
    if fromPath and os.path.isdir(fromPath):
      try:
        shutil.copytree(fromPath, self.basePath, dirs_exist_ok=True)
      except Exception as e:
        self.onError(e)

  def readNetworkFile(self, fileIndex=None, isInit=False):
    fpath = self.dataPath['construction'] if isInit else self.dataPath['output']
    getIndex = fileIndex if fileIndex != None else -2
    with open(fpath, 'rt', encoding='utf-8') as file:
      lines = file.readlines()
    if len(lines) == self.loadIndexMemory and not isInit:
      return self.all_w, self.biases
    self.loadIndexMemory = len(lines)
    self.all_w = None
    self.biases = None
    flat_array = [float(s.strip()) if is_num(s.strip()) else 0 for s in lines[getIndex].split(',')]
    if all([not bool(s) for s in flat_array]):
      return
    biases = []
    all_w = []
    for i in range(len(self.layerNums[:-1])):
      bias = []
      weight = []
      for _ in range(self.layerNums[i+1]):
        bias.append(flat_array[0])
        weight.append(flat_array[1:self.layerNums[i]+1])
        flat_array = flat_array[self.layerNums[i]+1:]
      biases.append(bias)
      all_w.append(weight)
    self.all_w = all_w
    self.biases = biases
    return self.all_w, self.biases

  def overwriteNetwork(self, toPath=''):
    if not (toPath and os.path.isdir(self.basePath)):
      return
    try:
      self.saveNetwork(toPath)
      shutil.rmtree(self.basePath)
      self._makeBaseDir()
    except Exception as e:
      self.onError(e)

# Create Network
  def createNetwork(self, out=False):
    if self.process:
      self.process.terminate()
    self.writeOperation('init')
    self.network = self.NNApp.createNetwork(out=out)

  # Create network new
  def newCreateNetwork(self, input_num=2, hidden_num=2, output_num=1):
    self._makeBaseDir()
    self.NNApp.createHeader(input_num, hidden_num, output_num)
    self.NNApp.createParamHeader(input_num, hidden_num, output_num)
    self.createNetwork(True)
    return self.network

  # Create network from file
  def fromFileCreateNetwork(self, fromPath):
    if not (fromPath and os.path.isdir(fromPath)):
      self.onError('not found directory path')
    self.copyNetwork(fromPath)
    self.createNetwork()
    if len(self.network) > 3:
      self.Error('require layer length > 3')
    return self.network

  def isExistNetwork(self):
    return bool(self.NNApp.network)

# Create Learning Data
  # Make learning data
  def makeLearningDataFile(self, fpath, data: dict):
    learningColumns = ['input', 'target']
    if not any([k in data.keys() for k in learningColumns]):
      print('not found items')
      return
    learningDatas = [data[column] for column in learningColumns]
    header = ','.join([str(len(datas[0].split(' '))) for datas in learningDatas])
    self._makeBaseDir()
    self._output_file(fpath, header, write_type='wt')
    inputData, targetData = tuple(learningDatas)
    for idata, tdata in zip(inputData, targetData):
      string = idata.replace(' ', ', ')
      string += ', ' + tdata.replace(' ', ', ')
      self._output_file(fpath, string)

  # Load learning data
  def readLearningDataFile(self, fpath):
    learning_data = []
    target_data = []
    if not os.path.isfile(fpath):
      return
    file = self._read_file(fpath)
    header, contents = (file[0], file[1:])
    columns = [int(value.strip()) for value in header.split(self.sep)]
    if not (len(columns) == 2 and all(columns)):
      self.onError('Invalid learning data')
      return False

    learning_num, target_num = tuple(columns)
    for row in contents:
      values = [int(value.strip()) for value in row.split(self.sep)]
      if not (learning_num+target_num == len(values)):
        self.onError('Invalid learning data')
        return False
      learning_data.append(values[:learning_num])
      target_data.append(values[learning_num:])
    return learning_data, target_data

# Train Setting Dialog Function
  # Set training params
  def writeNetworkParam(self, data):
    columns = ['error', 'epoch', 'freq', 'interval']
    fpath = self.dataPath['setting']
    if columns != list(data.keys()):
      return
    wtype = 'wt' if os.path.isfile(fpath) else 'at'
    self._output_file(fpath, ','.join(columns), write_type=wtype)
    self._output_file(fpath, ','.join([data[column] for column in columns]))

  # Start train network
  def onLearnNetwork(self, flag: bool, func=None):
    if self.readOperation() == self.config['Operate']['end']:
      return

    self.writeOperation('start' if flag else 'stop')
    func()
    if not self.process:
      if not (os.path.isfile(self.dataPath['learning'])):
        self.onError('learning data file was not found')
        return
      if not self.NNApp.network:
        self.onError('create Neural Network before train')
        return
      self.process = Process(target=initNNApp, args=(self.NNApp, ))
      self.process.start()
    return self.readOperation() == self.config['Operate']['start']
  
  def onUpdateNetworkParam(self, fileIndex=None):
    operation = self.readOperation()
    isInit = operation == self.config['Operate']['init']
    datas = self.readLearningDataFile(self.dataPath['learning'])
    fileIndex = -1 if isInit else fileIndex
    getIndex = fileIndex if fileIndex != None else -2
    flag = (operation == self.config['Operate']['start']) or isInit
    if not flag:
      return
    lines = self._read_file(self.dataPath['param'])
    if len(lines)-3 < abs(getIndex):
      return
    header = lines[1]
    input_num, hidden_num, output_num = [int(line.strip()) for line in header.split(',')]

    loss = [float(line.split(',')[0].strip()) for line in lines[4:]]
    flat_array = [float(line.strip()) if line != '' else None for line in lines[getIndex].split(',')]
    index = int(flat_array[1])
    flat_array = flat_array[2:]
    input_out = flat_array[:input_num]
    flat_array = flat_array[input_num:]
    hidden_out = flat_array[:hidden_num]
    flat_array = flat_array[hidden_num:]
    output_out = flat_array[:]
    weights, _ = self.readNetworkFile(getIndex, isInit)

    inputData = datas[0][index] if datas else [0]*input_num
    targetData = datas[1][index] if datas else [0]*output_num

    return (flag, loss, [inputData, hidden_out, output_out, targetData], weights)

  def getLearningData(self, fpath):
    if not os.path.isfile(fpath):
      return
    datas = self._read_file(fpath)
    data = [int(d.strip()) for d in datas[0].split(',')]
    validateInOut = [self.network[0], self.network[-1]]
    if validateInOut != data:
      self.onError('not equal from network input or output to learning data')

  # Select learning data for train
  def onSelectLearningDataForTrain(self, fpath):
    self.getLearningData(fpath)
    if os.path.isfile(self.dataPath['learning']):
      os.remove(self.dataPath['learning'])
    shutil.copyfile(fpath, self.dataPath['learning'])
    self.learningDataPath = fpath
    return fpath
  
  # Load setting data file
  def readSettingFile(self):
    contents = self._read_file(self.dataPath['setting'])
    array = ['error', 'epoch', 'updateFreqency', 'updateInterval']
    values = [float(column.strip()) for column in contents[-1].split(self.sep) if is_num(column.strip())]
    setting = { key: value for key, value in zip(array, values) }

    return setting

  def onInitWeight(self, func):
    if self.isExistNetwork():
      if self.process:
        self.process.terminate()
        self.process = None
      self.NNApp.initWeight()
      self.writeOperation('init')
      func()

# Test Dialog Functions
  def readLearningData(self, fpath):
    self.testDataPath = fpath
    self.getLearningData(fpath)
    self.testMaxIndex = self.NNApp.setTestData(fpath)

  def startTest(self):
    self.testAnswers = []
    self.NNApp.createNetwork(readFile=self.dataPath['output'], out=False)
    for i in range(self.testMaxIndex):
      self.testAnswers.append(self.NNApp.test(i))
    return len(self.testAnswers)

  def getTestAnswerByIndex(self, index):
    items = self.testAnswers[index]
    if not items:
      return
    outs, weights, datas = items
    
    return (True, [], [datas[0], *outs[1:], datas[1]], weights)
    
  def writeOperation(self, key: str):
    if not key in ['init', 'start', 'stop']:
      return
    with open(self.config['Paths']['operation'], 'wt', encoding='utf-8') as f:
      print(self.config['Operate'][key], file=f)

  
  def readOperation(self):
    with open(self.config['Paths']['operation'], 'rt', encoding='utf-8') as f:
      lines = f.readlines()
    return [line.strip().upper() for line in lines][0]

# Property Dialog
  def propertySubmit(self, inputSize, colorRange):
    self.inputSize = inputSize
    self.colorRange = colorRange
    return self.inputSize, self.colorRange
  
def initNNApp(app):
  app.train_setting()
  app.train_network()
