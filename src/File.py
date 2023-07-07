import os, gc, shutil, re
from collections import deque
from configparser import ConfigParser
from config.settingConfig import configUpdate
from src.NNApp.NeuralNetwork import Network

def is_num(value: str) -> bool:
  try:
    float(value)
  except ValueError:
    return False
  else:
    return True

class File:
  def __init__(self, config: ConfigParser, error=None):
    self.config = config
    self.error = error
    self.base_path = self.config['Paths']['data']
    self.data_path = {key: self.config['Paths'][key] for key in self.config['Datas']}

  def on_error(self, text):
    if self.error is None:
      return
    self.error(text)

  def to_type(self, func):
    return lambda value: func(value.strip())

  def read_file(self, fpath: str) -> list[str]:
    if not os.path.isfile(fpath):
      self.on_error(f'Not exist {fpath}')
      return
    with open(fpath, 'rt', encoding='utf-8') as f:
      text = f.readlines()
    return text

  def output_file(self, fpath: str, string: str, write_type='at'):
    with open(fpath, write_type, encoding='utf-8') as f:
      print(string, file=f)

  def create_header(self, input_num=2, hidden_num=2, output_num=1):
    fpaths = (self.data_path[key] for key in ['construction', 'parameter'])
    numdict = { 'input_num': input_num, 'hidden_num': hidden_num, 'output_num': output_num }
    for fpath in fpaths:
      self.output_file(
        fpath,
        '\n'.join([
          ','.join(numdict.keys()),
          ','.join(map(str, numdict.values())),
          f"{self._print_bw('h', input_num, hidden_num)}, {self._print_bw('o', hidden_num, output_num)}"
        ]),
        write_type='wt'
      )

  def create_outputfile_header(self, input_num=2, hidden_num=2, output_num=1):
    fpath = self.data_path['output']
    numdict = { 'input_num': input_num, 'hidden_num': hidden_num, 'output_num': output_num }
    self.output_file(
      fpath,
      '\n'.join([
        ','.join(numdict.keys()),
        ','.join(map(str, numdict.values())),
        f"""loss,test_index,{','.join([f"{key}({','.join([str(i) for i in range(value)])})" for key, value in numdict.items()])}"""
      ]),
      write_type='wt'
    )

  def _print_bw(self, text: str, front_num: int, back_num=1):
    array = tuple([f'{text}{b+1}-b' if f == 0 else f'{text}{b+1}-w{f}' for f in range(front_num+1) for b in range(back_num)])
    return ','.join(array)

# Learning file
  def read_learning_data(self, fpath: str):
    if not os.path.isfile(fpath):
      self.on_error(f'Not exist {fpath}')
      return False

    contents = self.read_file(fpath)[1:]
    columns = list(map(self.to_type(int), contents[0].split(',')))
    if not (len(columns) == 2 and all(columns)):
      self.on_error('Invalid learning data')
      return False

    learning_data = []
    target_data = []
    learning_num, _ = columns
    data = [list(map(self.to_type(float), content.split(','))) for content in contents[1:]]
    for element in data:
      learning_data.append(element[:learning_num])
      target_data.append(element[learning_num:])

    if not all(map(lambda a: sum(map(len, a)) == sum(columns), zip(learning_data, target_data))):
      self.on_error('Invalid learning data')
      return False

    return tuple([columns, tuple(learning_data), tuple(target_data)])

  def make_learning_data(self, fpath: str, data: dict):
    columns = ('input', 'target')
    if not any((k in data.keys() for k in columns)):
      print('not found items')
      return
    learning_data = tuple([data[column] for column in columns])
    input_data, target_data = learning_data

    self.output_file(
      fpath,
      '\n'.join([
        ','.join([column for column in columns]),
        ','.join([str(len(data[0].split(' '))) for data in learning_data]),
        '\n'.join([f"{idata.replace(' ', ',')},{tdata.replace(' ', ',')}" for idata, tdata in zip(input_data, target_data)])
      ]),
      write_type='wt'
    )

  def validate_learning_data(self, fpath: str):
    if not os.path.isfile(fpath):
      return False
    contents = self.read_file(fpath)
    nums = tuple(map(self.to_type(int), contents[1].split(',')))
    columns = tuple(map(self.to_type(int), self.read_file(self.data_path['construction'])[1].split(',')))

    if tuple([columns[0], columns[-1]]) != nums:
      self.on_error('not equal from network input or output to learning data')
      return False
    return True

  # def read_setting_file(self, fpath: str):
  #   contents = self.read_file(fpath)
  #   return tuple([float(column.strip()) for column in contents[-1].split(',') if is_num(column.strip())])

# Network Folder
  def read_network_file(self, fpath: str=None, file_index: int=None, is_init=False) -> \
    tuple[tuple[int], tuple[tuple[tuple[float]]], tuple[tuple[float]]]:
    get_index = -1
    if fpath is None:
      fpath = self.data_path['construction'] if is_init else self.data_path['parameter']
      get_index = file_index if file_index != None else -2
    get_param_index = get_index+3 if get_index >= 0 else get_index
    contents = self.read_file(fpath)
    nums= tuple(map(self.to_type(int), contents[1].split(',')))
    all_w = None
    biases = None
    flat_array: deque[float] = deque(map(
      self.to_type(lambda value: float(value) if is_num(value) else 0.0),
      contents[get_param_index].split(',')
    ))
    if not any((map(bool, list(flat_array)))):
      return tuple([nums, [], []])
    biases = []
    all_w = []
    # for i in range(len(nums[:-1])):
    #   bias = []
    #   weight = []
    #   for _ in range(nums[i+1]):
    #     bias.append(flat_array[0])
    #     weight.append(flat_array[1:nums[i]+1])
    #     flat_array = flat_array[nums[i]+1:]
    for i in range(len(nums)-1):
      bias = []
      weight = []
      for _ in range(nums[i+1]):
        bias.append(flat_array.popleft())
        weight.append([flat_array.popleft() for _ in range(nums[i])])
      biases.append(tuple(bias))
      all_w.append(tuple(weight))
    return nums, tuple(all_w), tuple(biases)
 
  def make_network_folder(self):
    if os.path.isdir(self.base_path):
      shutil.rmtree(self.base_path)
    if not os.path.isdir(self.base_path):
      os.mkdir(self.base_path)

  def overwrite_network(self, to_path: str=''):
    if not (to_path and os.path.isdir(self.base_path)):
      return False
    try:
      self.save_network(to_path)
      self.make_network_folder()
    except Exception as e:
      self.on_error(e)

  def save_network(self, to_path: str):
    if not (to_path and os.path.isdir(self.base_path)):
      return False
    try:
      shutil.copytree(self.base_path, to_path, dirs_exist_ok=True)
      return True
    except Exception as e:
      self.on_error(e)
      return False

  def copy_network(self, from_path: str):
    if not (from_path and os.path.isdir(from_path)):
      return False
    try:
      shutil.copytree(from_path, self.base_path, dirs_exist_ok=True)
      return True
    except Exception as e:
      self.on_error(e)
      return False

  def output_network(self, network: Network, out_file: str, sep=','):
    if not network:
      return
    self.output_file(
      out_file,
      sep.join([
        sep.join([
          sep.join([
            '{:.3f}'.format(neuron.bias),
            *('{:.3f}'.format(w) if alive else str(0) for w, alive in zip(neuron.weight, neuron.alive))
          ]) for neuron in layer.neurons
        ]) for layer in network.layers[1:]
      ])
    )

  def output_layer_out(self, network: Network, out_file: str, index=0, score: float=None, sep=','):
    if not network:
      return

    self.output_file(
      out_file,
      sep.join([
        '{:.3e}'.format(score) if score != None else '',
        str(index),
        sep.join([
          sep.join([
            '{:.3f}'.format(neuron.get()) for neuron in layer.neurons
          ]) for layer in network.layers
        ])
      ])
    )

# Train files
  def write_network_param(self, data):
    columns = ('error', 'epochs', 'batch', 'interval')
    fpath = self.data_path['setting']
    if columns != tuple(data.keys()):
      return
    self.output_file(
      fpath,
      '\n'.join([
        ','.join(columns),
        ','.join([data[column] for column in columns])
      ]),
      write_type='wt'
    )
    configUpdate(self.config, { 'Setting': data })

  def read_network_param(self, file_index=None):
    operation = self.read_operation()
    is_init = operation == self.config['Operate']['init']

    file_index = -1 if is_init else file_index
    get_index = file_index if file_index != None else -2
    output_index = get_index+4 if get_index >= 0 else get_index
    flag = (operation == self.config['Operate']['start']) or is_init
    if not (flag or bool(file_index)):
      return None
    contents = self.read_file(self.data_path['output'])
    if contents is None:
      return None
    if len(contents)-3 < abs(output_index):
      return None
    header = contents[1]
    input_num, hidden_num, output_num = tuple(map(self.to_type(int), header.split(',')))
    loss = tuple(map(self.to_type(float), filter(lambda value: value.strip() != '', map(lambda content: content.split(',')[0], contents[4:]))))
    flat_array: deque[float] = deque(map(
      self.to_type(lambda value: float(value) if value != '' else None),
      contents[output_index].split(',')
    ))
    flat_array.popleft() # cut loss value
    index = int(flat_array.popleft())
    input_out = [flat_array.popleft() for _ in range(input_num)]
    hidden_out = [flat_array.popleft() for _ in range(hidden_num)]
    output_out = list(flat_array)
    _, weights, _ = self.read_network_file(file_index=get_index, is_init=is_init)

    data = self.read_learning_data(self.data_path['learning']) if not is_init else None
    input_data = data[1][index] if data else [0]*input_num
    target_data = data[2][index] if data else [0]*output_num

    return tuple([is_init, loss, tuple([input_data, hidden_out, output_out, target_data]), weights])

  def select_train_file(self, fpath: str):
    if not os.path.isfile(fpath):
      return False
    if os.path.isfile(self.data_path['learning']):
      os.remove(self.data_path['learning'])
    shutil.copyfile(fpath, self.data_path['learning'])
    return True


# Test files
  def put_result_file(self, tests: list, test_path: str, to_path: str):
    if not (to_path and test_path):
      return
    shutil.copyfile(test_path, to_path)
    lines = self.read_file(test_path)
    columns = ['input', 'target', 'output']
    column_nums = map(lambda s: s.strip(), lines[1].split())
    self.output_file(
      to_path,
      '\n'.join([
        ','.join(columns),
        ','.join([*column_nums, column_nums[-1]]),
        *[','.join([
            line.strip(),
            ','.join(['{:.3f}'.format(ans) for ans in tests[index][0][-1]])
          ]) for index, line in enumerate(lines[2:])
        ]
      ]),
      'wt'
    )


# Setting files(Operations, Settings)
  def read_setting_file(self, fpath):
    if not os.path.isfile(fpath):
      return dict({ key: float(value) for key, value in self.config['Setting'].items() })

    contents = self.read_file(fpath)
    keys = ('error', 'epoch', 'batch', 'interval')
    values = tuple(map(self.to_type(float), contents[-1].split(',')))

    return dict({ key: value for key, value in zip(keys, values) })
  
  def read_operation(self):
    lines = self.read_file(self.config['Paths']['operation'])
    if len(lines) > 0:
      return lines[0].strip().upper()
    return None

  def is_operation(self, key='stop') -> bool:
    return self.config['Operate'][key] == self.read_operation()

  def write_operation(self, key='end'):
    self.output_file(self.config['Paths']['operation'], self.config['Operate'][key], 'wt')

# Property Dialog
  def property_submit(self, dirpath):
    if not os.path.isdir(dirpath):
      return False
    configUpdate(self.config, { 'Paths': { 'reference': dirpath } }, self.config['Paths']['configfile'])
    return True


