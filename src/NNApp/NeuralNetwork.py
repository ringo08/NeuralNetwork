from __future__ import annotations
import math, random
from .NetworkParam import K, H, weightRange as wRange
from .functions import NguyenWidrow

def sigmoid(x: float) -> float:
  return 1 / (1 + math.exp(-(K*x)))

def relu(x: float) -> float:
  return x * (x > 0.0)

def derivative(f, x: float, h: float) -> float:
  return (f(x+h) - f(x)) / h

def mean(x:list) -> float:
  return sum(x)/len(x)

class Neuron:
  def __init__(self, init_weight: list[float]=None, init_bias: float=None, func=None):
    self.dendrite = 0.0
    self.axon = 0.0
    self.weight = init_weight
    self.bias = init_bias
    if init_weight:
      self.alive = [1 if bool(w) else 0 for w in init_weight]
    self.h = func if func else sigmoid

  def set_params(self, weight: list[float]=None, bias: float=None):
    if weight is not None:
      self.weight = weight
    if bias is not None:
      self.bias = bias

  def init_status(self, value: float):
    self.dendrite = value
    self.axon = value
  
  def add(self, values: list[float]):
    self.dendrite = self.bias
    self.dendrite += sum((v*w*alive for v, w, alive in zip(values, self.weight, self.alive)))
    self.axon = self.h(self.dendrite)

  def get(self) -> float:
    return self.axon

  def cut(self, index: int):
    self.alive[index] = 0

class Layer:
  def __init__(self, weights: list[list[float]]=[], biases: list[float]=[], num=0, is_input=False):
    self.num = num if num > 0 else len(weights)
    if is_input:
      self.neurons = tuple([Neuron() for _ in range(self.num)])
    else:
      self.neurons = tuple([Neuron(init_weight=weights[i], init_bias=biases[i]) for i in range(self.num)])

  def update_attribute(self, weights: list[list[float]], biases: list[float]):
    [neuron.set_params(weight=weight, bias=bias) for neuron, weight, bias in zip(self.neurons, weights, biases)]

  def set_values(self, input_values):
    [neuron.init_status(value) for neuron, value in zip(self.neurons, input_values)]

  def get_values(self) -> tuple[float]:
    return tuple([neuron.get() for neuron in self.neurons])

  def forward(self, next_layer: Layer):
    [nn.add(self.get_values()) for nn in next_layer.neurons]

  def backward(self, frontLayer: Layer, errors: list[float], n: float, h: float) -> \
    tuple[tuple[list[float]], tuple[float], tuple[float]]:

    new_errors: list[float] = []
    biases: list[float] = []
    weights: tuple[list[float]] = tuple([[] for _ in range(self.num)])
    for sn in range(self.num):
      neuron = self.neurons[sn]
      diff = derivative(neuron.h, neuron.dendrite, h)
      back = errors[sn]*diff
      biases.append(neuron.bias - n*back)
      new_errors.append(back)
      for fn in range(frontLayer.num):
        out_front = frontLayer.neurons[fn].get()
        weights[sn].append(neuron.weight[fn]-n*out_front*back)
    return weights, tuple(biases), tuple(new_errors)


class Network:
  def __init__(self, input_num=2, hidden_num=2, output_num=1, weights: list[list[list[float]]]=[], biases: list[list[float]]=[]):
    self.input_num = input_num
    self.hidden_num = hidden_num
    self.output_num = output_num
    self.score = None
    if (not weights) and (not biases):
      weights, biases = self._init_net()
      # self._init_net_with_nguyen_widrow()

    self.layers = [Layer(num=self.input_num, is_input=True)]
    for weight, bias in zip(weights, biases):
      self.layers.append(Layer(weights=weight, biases=bias))

  def _init_net(self, place=False):
    weights = [
      self._init_weight(self.input_num, self.hidden_num),
      self._init_weight(self.hidden_num, self.output_num)
    ]
    biases = self._init_weight(self.hidden_num, 1)
    biases.extend(self._init_weight(self.output_num, 1))

    if place:
      [layer.update_attribute(weight, bias) for layer, weight, bias in zip(self.layers[:0:-1], weights, biases)]
    return weights, biases

  def _init_net_with_nguyen_widrow(self, place=False):
    hidden_w, hidden_b = NguyenWidrow(self.input_num, self.hidden_num)
    output_w, output_b = NguyenWidrow(self.hidden_num, self.output_num)
    weights = [hidden_w, output_w]
    biases = [hidden_b, output_b]

    if place:
      [layer.update_attribute(weight, bias) for layer, weight, bias in zip(self.layers[:0:-1], weights, biases)]

  def _init_weight(self, in_num: int, out_num: int, wRange=1):
    return [[random.uniform(-wRange, wRange) for _ in range(in_num)] for _ in range(out_num)]

  def learning(self, input_values: list[list[float]], targets: list[list[float]], n=0.99):
    NNUM = len(self.layers)
    score = []
    for index, input_layer in enumerate(input_values):
      self.layers[0].set_values(input_layer)
      target = targets[index]

      for i in range(NNUM-1):
        self.layers[i].forward(self.layers[i+1])

      # calc error and score
      out_values = self.layers[-1].get_values()
      # errors = [-(t-value[i]) for t, value in zip(target, out_values)]
      errors = [-(t-value) for t, value in zip(target, out_values)]
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
      [layer.update_attribute(weight, bias) for layer, weight, bias in zip(self.layers[:0:-1], new_weights, new_biases)]
    return score
  
  def fit(self, test_values: list[float]):
    self.layers[0].set_values(test_values)
    for i, layer in enumerate(self.layers[:-1]):
      layer.forward(self.layers[i+1])
    return self.layers[-1].get_values()
