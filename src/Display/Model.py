import os, shutil
from src.NNApp import NNApp
from . import Messages
from multiprocessing import Process
from config.settingConfig import configUpdate

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
    self.layerNums = ()
    self.loadIndexMemory = 0
    self.testMaxIndex = 0
    self.inputSize = 1
    self.colorRange = 2
    self.isSaved = True
    self.learningDataPath = ''
    self.testDataPath = ''
    self.basePath = self.config['Paths']['data']
    self.referencePath = self.config['Paths']['reference']
    self.network = ()
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

  def _read_file(self, path):
    if not os.path.isfile(path):
      self.onError('Not exist file')
      return
    with open(path, 'rt', encoding='utf-8') as f:
      text = f.readlines()
    return text

  def _output_file(self, fpath, string, write_type='at'):
    with open(fpath, write_type, encoding='utf-8') as file:
      print(string, file=file)

  def _print_bw(self, text, front_num, back_num=1):
    array = tuple([tuple([f'{text}{b+1}-b' if f == 0 else f'{text}{b+1}-w{f}' for f in range(front_num+1)]) for b in range(back_num)])
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
        self.isSaved = True
      except Exception as e:
        self.onError(e)

  def copyNetwork(self, fromPath):
    if fromPath and os.path.isdir(fromPath):
      try:
        shutil.copytree(fromPath, self.basePath, dirs_exist_ok=True)
      except Exception as e:
        self.onError(e)

  def readNetworkFile(self, fileIndex=None, isInit=False):
    fpath = self.dataPath['construction'] if isInit else self.dataPath['parameter']
    getIndex = fileIndex if fileIndex != None else -2
    getParamIndex = getIndex+3 if getIndex >= 0 else getIndex
    with open(fpath, 'rt', encoding='utf-8') as file:
      lines = file.readlines()
    if len(lines) == self.loadIndexMemory and not isInit:
      return self.all_w, self.biases
    self.loadIndexMemory = len(lines)
    self.all_w = None
    self.biases = None
    flat_array = tuple([float(s.strip()) if is_num(s.strip()) else 0 for s in lines[getParamIndex].split(',')])
    if all((not bool(s) for s in flat_array)):
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
      biases.append(tuple(bias))
      all_w.append(tuple(weight))
    self.all_w = tuple(all_w)
    self.biases = tuple(biases)
    return self.all_w, self.biases

  def overwriteNetwork(self, toPath=''):
    if not (toPath and os.path.isdir(self.basePath)):
      return
    try:
      self.saveNetwork(toPath)
      self._makeBaseDir()
    except Exception as e:
      self.onError(e)

# Create Network
  def createNetwork(self, out=False):
    if self.process:
      self.process.terminate()
      self.process = None
    self.writeOperation('init')
    self.network = self.NNApp.createNetwork(out=out)
    self.isSaved = False

  # Create network new
  def newCreateNetwork(self, input_num=2, hidden_num=2, output_num=1):
    self._makeBaseDir()
    self.NNApp.createHeader(input_num, hidden_num, output_num)
    self.NNApp.createOutputHeader(input_num, hidden_num, output_num)
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
    learningColumns = ('input', 'target')
    if not any((k in data.keys() for k in learningColumns)):
      print('not found items')
      return
    headerColumns = ','.join([data for data in learningColumns])
    self._output_file(fpath, headerColumns, write_type='wt')

    learningDatas = tuple([data[column] for column in learningColumns])
    headerParams = ','.join([str(len(datas[0].split(' '))) for datas in learningDatas])
    self._output_file(fpath, headerParams)
    inputData, targetData = learningDatas
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
    header, contents = (file[1], file[2:])
    columns = tuple([int(value.strip()) for value in header.split(self.sep)])
    if not (len(columns) == 2 and all(columns)):
      self.onError('Invalid learning data')
      return False

    learning_num, target_num = columns
    for row in contents:
      values = tuple([int(value.strip()) for value in row.split(self.sep)])
      if not (learning_num+target_num == len(values)):
        self.onError('Invalid learning data')
        return False
      learning_data.append(values[:learning_num])
      target_data.append(values[learning_num:])
    return tuple(learning_data), tuple(target_data)

# Train Setting Dialog Function
  # Set training params
  def writeNetworkParam(self, data):
    columns = ('error', 'epochs', 'batch', 'interval')
    fpath = self.dataPath['setting']
    if columns != tuple(data.keys()):
      return
    wtype = 'wt' if os.path.isfile(fpath) else 'at'
    self._output_file(fpath, ','.join(columns), write_type=wtype)
    self._output_file(fpath, ','.join([data[column] for column in columns])) 
    configUpdate(self.config, { 'Setting': data })

  def onChangeTrainOperation(self, flag):
    if self.readOperation() == self.config['Operate']['end']:
      return False
    self.writeOperation('start' if flag else 'stop')
    if flag and not self.process:
      if not (os.path.isfile(self.dataPath['learning'])):
        self.onError('learning data file was not found')
        return
      if not self.NNApp.network:
        self.onError('create Neural Network before train')
        return
      self.process = Process(target=initNNApp, args=(self.NNApp, ))
      self.process.start()

  # Start train network
  def onLearnNetwork(self, func=None):
    if self.readOperation() == self.config['Operate']['end']:
      func(index=-1)
      self.process.terminate()
      return False
    func()
    return self.readOperation() == self.config['Operate']['start']
  
  def onUpdateNetworkParam(self, fileIndex=None):
    operation = self.readOperation()
    isInit = operation == self.config['Operate']['init']
    datas = self.readLearningDataFile(self.dataPath['learning'])
    fileIndex = -1 if isInit else fileIndex
    getIndex = fileIndex if fileIndex != None else -2
    getOutputIndex = getIndex+4 if getIndex >= 0 else getIndex
    flag = (operation == self.config['Operate']['start']) or isInit
    if not (flag or bool(fileIndex)):
      return
    lines = self._read_file(self.dataPath['output'])
    if lines is None:
      return
    if len(lines)-3 < abs(getOutputIndex):
      return
    header = lines[1]
    input_num, hidden_num, output_num = tuple([int(line.strip()) for line in header.split(',')])

    loss = tuple([float(line.split(',')[0].strip()) for line in lines[4:] if line.split(',')[0].strip() != ''])
    flat_array = tuple([float(line.strip()) if line != '' else None for line in lines[getOutputIndex].split(',')])
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
    return tuple([isInit, loss, tuple([inputData, hidden_out, output_out, targetData]), weights])

  def validateLearingData(self, fpath):
    if not os.path.isfile(fpath):
      return False
    datas = self._read_file(fpath)
    data = tuple([int(d.strip()) for d in datas[1].split(',')])
    validateInOut = (self.network[0], self.network[-1])
    if validateInOut != data:
      self.onError('not equal from network input or output to learning data')
      return False
    return True

  # Select learning data for train
  def onSelectLearningDataForTrain(self, fpath):
    if not fpath:
      return False
    if os.path.isfile(self.dataPath['learning']):
      os.remove(self.dataPath['learning'])
    shutil.copyfile(fpath, self.dataPath['learning'])
    self.learningDataPath = fpath
  
  # Load setting data file
  def readSettingFile(self):
    if not os.path.isfile(self.dataPath['setting']):
      return dict({ key: float(value) for key, value in self.config['Setting'].items() })
    contents = self._read_file(self.dataPath['setting'])
    array = ('error', 'epochs', 'batch', 'interval')
    values = tuple([float(column.strip()) for column in contents[-1].split(self.sep) if is_num(column.strip())])
    return { key: value for key, value in zip(array, values) }

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
    self.validateLearingData(fpath)
    self.testMaxIndex = self.NNApp.setTestData(fpath)

  def startTest(self):
    self.NNApp.createNetwork(readFile=self.dataPath['parameter'], out=False)
    self.testAnswers = tuple([self.NNApp.test(i) for i in range(self.testMaxIndex)])
    return len(self.testAnswers)

  def getTestAnswerByIndex(self, index):
    items = self.testAnswers[index]
    if not items:
      return
    outs, weights, datas = items
    
    return tuple([True, [], tuple([datas[0], *outs[1:], datas[1]]), weights])
  
  def onPutFile(self, fpath):
    if not (fpath and self.testDataPath):
      return
    shutil.copyfile(self.testDataPath, fpath)
    with open(fpath, 'rt') as infile:
      lines = infile.readlines()
    with open(fpath, 'wt') as out:
      print(lines[0].rstrip() + ',output', file=out)
      print(lines[1].rstrip() + f',{lines[1].split(",")[-1].strip()}', file=out)
      for index, line in enumerate(lines[2:]):
        outs, _, _ = self.testAnswers[index]
        print(line.rstrip()+','+','.join(['{:.3f}'.format(ans) for ans in outs[-1]]), file=out)

# Operation    
  def writeOperation(self, key: str):
    if not key in ('init', 'start', 'stop'):
      return
    with open(self.config['Paths']['operation'], 'wt', encoding='utf-8') as f:
      print(self.config['Operate'][key], file=f)

  
  def readOperation(self):
    with open(self.config['Paths']['operation'], 'rt', encoding='utf-8') as f:
      lines = f.readlines()
    return tuple([line.strip().upper() for line in lines])[0]

# Property Dialog
  def propertySubmit(self, fpath, inputSize, colorRange):
    if fpath:
      configUpdate(self.config, { 'Paths': { 'reference': fpath } }, self.config['Paths']['configfile'])
      self.referencePath = fpath
    self.inputSize = inputSize
    self.colorRange = colorRange
    return self.inputSize, self.colorRange
  
  def getParam(self, layer, neuron, weight=None):
    weights, biases = self.readNetworkFile(-1)
    return biases[layer-1][neuron] if weight is None else weights[layer-1][neuron][weight]
  
  def onCutWeight(self, layer, neuron, weight=None, onCut=None):
    if weight is None:
      return
    if self.NNApp.cut_combining(layer, neuron, weight):
      onCut()
      return self.onUpdateNetworkParam(-1)
  
def initNNApp(app):
  app.train_setting()
  app.train_network()
