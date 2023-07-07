import os, gc
from .NeuralNetwork import Network
from src.File import File
from configparser import ConfigParser

def mean(x:list[float]) -> float:
  return sum(x)/len(x)

class NNApp:
  def __init__(self, config: ConfigParser):
    self.config = config
    self.file = File(config)
    self.base_path = self.config['Paths']['data']
    self.data_path = {key: self.config['Paths'][key] for key in self.config['Datas']}
    self.data_name = {key: self.config['Datas'][key] for key in self.config['Datas']}
    self.operate_path = self.config['Paths']['operation']
    self.network = None

  def clear_network(self):
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
    self.create_network(readFile=self.data_path['parameter'], out=True)
    self.network.layers[layer_index].neurons[neuron_index].cut(w_index)
    self.file.output_network(self.network, self.data_path['construction'])
    self.file.output_network(self.network, self.data_path['parameter'])
    self.file.output_layer_out(self.network, self.data_path['output'], index=0)
    return True

  def create_network(self, readFile: str=None, out=False):
    if self.network:
      self.clear_network()
    fpath = readFile if readFile else self.data_path['construction']
    
    items = self.file.read_network_file(fpath)
    nums, self.all_w, self.biases = items
      
    self.input_num, self.hidden_num, self.output_num = nums
    self.network = Network(self.input_num, self.hidden_num, self.output_num, weights=self.all_w, biases=self.biases)
    
    if out:
      self.file.output_network(self.network, fpath)
      self.file.output_network(self.network, self.data_path['parameter'])
      self.file.output_layer_out(self.network, self.data_path['output'], index=0)
    return tuple([self.input_num, self.hidden_num, self.output_num])

  def init_weight(self):
    self.file.create_header(self.input_num, self.hidden_num, self.output_num)
    self.file.create_outputfile_header(self.input_num, self.hidden_num, self.output_num)
    self.clear_network()
    self.create_network(out=True)

  def train_setting(self):
    if not (os.path.isfile(self.data_path['learning']) and os.path.isfile(self.data_path['setting'])):
      return
    data = self.file.read_learning_data(self.data_path['learning'])
    if (data is False):
      return
    _, self.learning_data, self.target_data = data
    self.error, self.epoch, self.batch, self.interval = self.file.read_setting_file(self.data_path['setting']).values()

  def train_network(self, n=0.99):
    count = 0
    e = 0
    answer = []
    score = []
    stoped = True
    while True:
      if self.file.is_operation('stop'):
        stoped = True
        continue
      if score and self.file.is_operation('init'):
        self.init_weight()
        count = 0
        e = 0
        answer = []
        score = []
      elif stoped:
        stoped = False
        self.create_network(readFile=self.data_path['parameter'])
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
        self.file.output_network(self.network, self.data_path['parameter'])
        self.file.output_layer_out(self.network, self.data_path['output'], index=index, score=self.score)
        if e >= self.epoch:
          self.file.write_operation('stop')
          e = 0
        e += 1
        if answer[-1] < self.error:
          self.file.write_operation('end')
          break

    return answer

  def set_test_data(self, fpath: str):
    learning_data = self.file.read_learning_data(fpath)
    if (learning_data is False):
      return 0
    
    _, self.test_input_data, self.test_target_data = learning_data
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