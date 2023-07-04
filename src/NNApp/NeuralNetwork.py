import math, random
from .NetworkParam import K, H, weightRange as wRange
from .functions import NguyenWidrow

def is_num(s):
  try:
    float(s)
  except ValueError:
    return False
  else:
    return True

def sigmoid(x: float):
  return 1 / (1 + math.exp(-(K*x)))

def relu(x: float):
  return x * (x > 0.0)

def derivative(f, x, h):
  return (f(x+h) - f(x)) / h

def mean(x:list):
  return sum(x)/len(x)

class Neuron:
  def __init__(self, init_weight=None, init_bias=None, func=None):
    self.dendrite = 0.0
    self.axon = 0.0
    self.weight = init_weight
    self.bias = init_bias
    if init_weight:
      self.alive = [1 if bool(w) else 0 for w in init_weight]
    self.h = func if func else sigmoid

  def set_weight(self, weight):
    self.weight = weight

  def set_bias(self, bias):
    self.bias = bias

  def set_value(self, value):
    self.dendrite = value
    self.axon = value
  
  def add(self, values: list):
    self.dendrite = self.bias
    self.dendrite += sum((v*w*alive for v, w, alive in zip(values, self.weight, self.alive)))
    self.axon = self.h(self.dendrite)

  def get(self):
    return self.axon

  def cut(self, index):
    self.alive[index] = 0

class Layer:
  def __init__(self, weights=[], biases=[], num=0, is_input=False):
    self.num = num if num > 0 else len(weights)
    if is_input:
      self.neurons = tuple([Neuron() for _ in range(self.num)])
    else:
      self.neurons = tuple([Neuron(init_weight=weights[i], init_bias=biases[i]) for i in range(self.num)])

  def update_attribute(self, weights, biases):
    for i, neuron in enumerate(self.neurons):
      neuron.set_weight(weights[i])
      neuron.set_bias(biases[i])

  def set_values(self, input_value):
    for i, neuron in enumerate(self.neurons):
      neuron.set_value(input_value[i])

  def get_values(self):
    return tuple([neuron.get() for neuron in self.neurons])

  def forward(self, next_layer):
    for nn in next_layer.neurons:
      nn.add(self.get_values())

  def backward(self, frontLayer, errors, n, h):
    new_errors = []
    weights = tuple([[] for _ in range(self.num)])
    biases = []
    for sn in range(self.num):
      neuron = self.neurons[sn]
      diff = derivative(neuron.h, neuron.dendrite, h)
      error = errors[sn]
      back = error*diff
      biases.append(neuron.bias - n*back)
      new_errors.append(back)
      for fn in range(frontLayer.num):
        out_front = frontLayer.neurons[fn].get()
        weights[sn].append(neuron.weight[fn]-n*out_front*back)
    return weights, tuple(biases), tuple(new_errors)


class Network:
  def __init__(self, input_num=2, hidden_num=2, output_num=1, weights=[], biases=[]):
    self.input_num = input_num
    self.hidden_num = hidden_num
    self.output_num = output_num
    self.all_w = weights
    self.biases = biases
    self.score = None
    if (not self.all_w) and (not self.biases):
      # self._init_net()
      self._init_net_with_nguyen_widrow()

    self.layers = [Layer(num=self.input_num, is_input=True)]
    for i in range(len(self.all_w)):
      self.layers.append(Layer(weights=self.all_w[i], biases=self.biases[i]))

  def _init_net(self, place=False):
    self.all_w = [
      self._init_weight(self.input_num, self.hidden_num),
      self._init_weight(self.hidden_num, self.output_num)
    ]
    self.biases = self._init_weight(self.hidden_num, 1)
    self.biases.extend(self._init_weight(self.output_num, 1))

    if place:
      for i, layer in enumerate(self.layers[:0:-1]):
        layer.update_attribute(self.all_w[i], self.biases[i])

  def _init_net_with_nguyen_widrow(self, place=False):
    hidden_w, hidden_b = NguyenWidrow(self.input_num, self.hidden_num)
    output_w, output_b = NguyenWidrow(self.hidden_num, self.output_num)
    self.all_w = [hidden_w, output_w]
    self.biases = [hidden_b, output_b]

    if place:
      for i, layer in enumerate(self.layers[:0:-1]):
        layer.update_attribute(self.all_w[i], self.biases[i])

  def _init_weight(self, in_num, out_num, wRange=1):
    return [[random.uniform(-wRange, wRange) for _ in range(in_num)] for _ in range(out_num)]

  def learning(self, input_values, targets, n=0.99):
    NNUM = len(self.layers)
    score = []
    for index, input_layer in enumerate(input_values):
      self.layers[0].set_values(input_layer)
      target = targets[index]

      for i in range(NNUM-1):
        self.layers[i].forward(self.layers[i+1])

      # calc error and score
      out_values = self.layers[-1].get_values()
      errors = [-(target[i]-out_values[i]) for i in range(len(target))]
      score.append(sum([(1/len(errors))*(e**2) for e in errors]))

      new_weights = []
      new_biases = []
      for i in range(NNUM-1, 0, -1):
        net = self.layers[i]
        new_w, new_b, errors = net.backward(self.layers[i-1], errors, n=n, h=H*score[-1])
        new_weights.append(new_w)
        new_biases.append(new_b)
        newError = tuple([
          sum([error*net.neurons[en].weight[num] for en, error in enumerate(errors)])
          for num in range(len(net.neurons[0].weight))
        ])
        errors = newError

      # update weight
      [layer.update_attribute(new_weights[i], new_biases[i]) for i, layer in enumerate(self.layers[:0:-1])]
    return score
  
  def fit(self, test_values):
    self.layers[0].set_values(test_values)
    for i, n in enumerate(self.layers[:-1]):
      n.forward(self.layers[i+1])
    return self.layers[-1].get_values()


if __name__ == '__main__':
  input_num, hidden_num, output_num = (2, 2, 1)
  net = Network(input_num=input_num, hidden_num=hidden_num, output_num=output_num)

  learning_data = [[0, 0], [0, 1], [1, 0], [1, 1]]
  target_data = [[0], [1], [1], [0]]
  score = net.learning(learning_data, target_data, error=1e-5)[1:]

  player = ''
  while True:
    player = input('input int array >>> ')
    if player == 'q':
      exit()
    input_strings = [s.strip() for s in player.split(',')]
    if not all([is_num(s) for s in input_strings]):
      print('invalid value')
      continue
    if net.input_num != len(input_strings):
      print('invalid length')
      continue
    test_values = [int(v) for v in input_strings]
    out_values = net.fit(test_values)
    print(out_values)
