import os, gc
from .NeuralNetwork import Network
from configparser import ConfigParser

def is_num(s: float) -> bool:
  try:
    float(s)
  except ValueError:
    return False
  else:
    return True

def mean(x:list[float]) -> float:
  return sum(x)/len(x)

class NNApp:
  def __init__(self, config: ConfigParser):
    self.config = config
    self.base_path = self.config['Paths']['data']
    self.data_path = {key: self.config['Paths'][key] for key in self.config['Datas']}
    self.data_name = {key: self.config['Datas'][key] for key in self.config['Datas']}
    self.operate_path = self.config['Paths']['operation']
    self.network = None

  def _read_learning_data(self, fpath: str):
    learning_data = []
    target_data = []
    with open(fpath, 'rt', encoding='utf-8') as file:
      contents = file.readlines()[1:]
    learning_num, target_num = tuple([int(value.strip()) for value in contents[0].split(',')])
    
    for content in contents[1:]:
      texts = content.split(',')
      learning_data.append([float(text.strip()) for text in texts[:learning_num]])
      target_data.append([float(text.strip()) for text in texts[learning_num:]])
    return learning_data, target_data

  def _read_setting_file(self, fpath: str):
    with open(fpath, 'rt', encoding='utf-8') as file:
      contents = file.readlines()
    return tuple([float(column.strip()) for column in contents[-1].split(',') if is_num(column.strip())])

  def _read_net_file(self, fpath: str):
    with open(fpath, 'rt', encoding='utf-8') as file:
      text = file.readlines()
    self.input_num, self.hidden_num, self.output_num = tuple([int(s.strip()) for s in text[1].split(',')])
    self.all_w = None
    self.biases = None
    nums = tuple([self.input_num, self.hidden_num, self.output_num])
    flat_array = tuple([float(s.strip()) if is_num(s.strip()) else 0 for s in text[-1].split(',')])
    if all((not bool(s) for s in flat_array)):
      return
    biases = []
    all_w = []
    for i in range(len(nums[:-1])):
      bias = []
      weight = []
      for _ in range(nums[i+1]):
        bias.append(flat_array[0])
        weight.append(flat_array[1:nums[i]+1])
        flat_array = flat_array[nums[i]+1:]
      biases.append(tuple(bias))
      all_w.append(tuple(weight))
    self.all_w = tuple(all_w)
    self.biases = tuple(biases)
  
  def _is_read_operation_file(self, key='stop') -> bool:
    with open(self.config['Paths']['operation'], 'rt', encoding='utf-8') as f:
      lines = f.readline()
    return self.config['Operate'][key] == lines.strip()

  def _write_end_operation_file(self, key='end'):
    if not key in ('stop', 'end'):
      return
    with open(self.config['Paths']['operation'], 'wt', encoding='utf-8') as f:
      print(self.config['Operate'][key], file=f)

  def _output_file(self, fpath: str, string: str, write_type='at'):
    with open(fpath, write_type, encoding='utf-8') as f:
      print(string, file=f)

  def createHeader(self, input_num=2, hidden_num=2, output_num=1):
    fpaths = (self.data_path[key] for key in ['construction', 'parameter'])
    for fpath in fpaths:
      self._output_file(fpath, "input_num, hidden_num, output_num", write_type='wt')
      self._output_file(fpath, f"{input_num}, {hidden_num}, {output_num}")
      self._output_file(fpath, f"{self._print_bw('h', input_num, hidden_num)}, {self._print_bw('o', hidden_num, output_num)}")  

  def createOutputHeader(self, input_num=2, hidden_num=2, output_num=1):
    fpath = self.data_path['output']
    self._output_file(fpath, "input_num, hidden_num, output_num", write_type='wt')
    self._output_file(fpath, f"{input_num}, {hidden_num}, {output_num}")
    numdict = { 'input_num': input_num, 'hidden_num': hidden_num, 'output_num': output_num }
    f = lambda nums: ','.join([str(i) for i in range(nums)])
    self._output_file(fpath, f"loss, test_index, {','.join([f'{key}({f(value)})' for key, value in numdict.items()])}") 

  def _print_bw(self, text: str, front_num: int, back_num=1):
    array = tuple([f'{text}{b+1}-b' if f == 0 else f'{text}{b+1}-w{f}' for f in range(front_num+1) for b in range(back_num)])
    return ','.join(array)

  def clearNetwork(self):
    del self.input_num, self.hidden_num, self.output_num, self.all_w, self.biases
    gc.collect()
    self.network = None

  def cut_combining(self, layer_index: int, neuron_index: int, w_index: int):
    if not (
      1 <= layer_index < len(self.network.layers)
      and 0 <= neuron_index < len(self.network.layers[layer_index].neurons)
      and 0 <= w_index < len(self.network.layers[layer_index].neurons[neuron_index].weight)
    ):
      return
    self.createNetwork(readFile=self.data_path['parameter'], out=True)
    self.network.layers[layer_index].neurons[neuron_index].cut(w_index)
    self.output_network(self.data_path['construction'])
    self.output_network(self.data_path['parameter'])
    self.output_layer_out(self.data_path['output'], index=0)
    return True

  def createNetwork(self, readFile: str=None, out=False):
    if self.network:
      self.clearNetwork()
    fpath = readFile if readFile else self.data_path['construction']
    self._read_net_file(fpath)
    self.network = Network(self.input_num, self.hidden_num, self.output_num, weights=self.all_w, biases=self.biases)
    
    if out:
      self.output_network(fpath)
      self.output_network(self.data_path['parameter'])
      self.output_layer_out(self.data_path['output'], index=0)
    return tuple([self.input_num, self.hidden_num, self.output_num])

  def output_network(self, outFile: str, sep=','):
    if not self.network:
      return
    string = sep.join([
      sep.join([
        sep.join(
          ['{:.3f}'.format(neuron.bias), *('{:.3f}'.format(w) if alive else str(0) for w, alive in zip(neuron.weight, neuron.alive))]
        ) for neuron in layer.neurons
      ]) for layer in self.network.layers[1:]
    ])
    with open(outFile, 'at', encoding='utf-8') as f:
      print(string, file=f)

  def output_layer_out(self, outFile: str, index=0, score: float=None, sep=','):
    if not self.network:
      return
    string = '{:.3e}'.format(score) if score != None else ''
    string += sep + str(index) + sep + sep.join([
      sep.join(['{:.3f}'.format(neuron.get()) for neuron in layer.neurons])
      for layer in self.network.layers
    ])
    with open(outFile, 'at', encoding='utf-8') as f:
      print(string, file=f)

  def initWeight(self):
    self.createHeader(self.input_num, self.hidden_num, self.output_num)
    self.createOutputHeader(self.input_num, self.hidden_num, self.output_num)
    self.clearNetwork()
    self.createNetwork(out=True)

  def train_setting(self):
    if not (os.path.isfile(self.data_path['learning']) and os.path.isfile(self.data_path['setting'])):
      return
    self.learning_data, self.target_data = self._read_learning_data(self.data_path['learning'])
    self.error, self.epoch, self.batch, self.interval = self._read_setting_file(self.data_path['setting'])

  def train_network(self, n=0.99):
    count = 0
    e = 0
    answer = []
    score = []
    stoped = True
    while True:
      if self._is_read_operation_file('stop'):
        stoped = True
        continue
      if score and self._is_read_operation_file('init'):
        self.initWeight()
        count = 0
        e = 0
        answer = []
        score = []
      elif stoped:
        stoped = False
        self.createNetwork(readFile=self.data_path['parameter'])
      count += 1
      score = self.network.learning(
        self.learning_data,
        self.target_data,
        n=n,
      )

      if count%self.batch==0:
        self.score = mean(score)
        answer.append(self.score)
        index = e%len(self.target_data)
        self.network.fit(self.learning_data[index])
        self.output_network(self.data_path['parameter'])
        self.output_layer_out(self.data_path['output'], index=index, score=self.score)
        if e >= self.epoch:
          self._write_end_operation_file('stop')
          e = 0
        e += 1
        if answer[-1] < self.error:
          self._write_end_operation_file('end')
          break

    return answer

  def setTestData(self, fpath: str):
    self.test_input_data, self.test_target_data = self._read_learning_data(fpath)
    return len(self.test_input_data)

  def test(self, test_index: int, sep=','):
    if not (self.test_input_data and self.test_target_data):
      return
    if not 0 <= test_index < len(self.test_target_data):
      return

    values = self.network.fit(self.test_input_data[test_index])
    outs = tuple([tuple([neuron.get() for neuron in layer.neurons]) for layer in self.network.layers])
    weights = tuple([tuple([tuple([w*alive for w, alive in zip(neuron.weight, neuron.alive)]) for neuron in layer.neurons]) for layer in self.network.layers[1:]])
    return tuple([outs, weights, tuple([self.test_input_data[test_index], self.test_target_data[test_index]])])

# main
def main(config):
  nnapp = NNApp(config)
  nnapp.train_setting()
  nnapp.train_network(n=0.99)

if __name__ == '__main__':
  from config.settingConfig import configUpdate, configWrite
  from configparser import ConfigParser, ExtendedInterpolation
  config = ConfigParser(interpolation=ExtendedInterpolation())
  path_root = os.getcwd()

  path_config = os.path.join(path_root, 'config', 'config.ini')
  if not os.path.isfile(path_config):
    configWrite(path_config)

  configUpdate(config, { 'Paths': {'root': path_root }}, path_config)
  config.read(path_config)
  main(config)