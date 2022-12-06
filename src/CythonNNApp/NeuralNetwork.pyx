#   NeuralNetwork.pyx
#cython: language_level=3
#distutils: language=c++

import math, random
from libcpp.vector cimport vector

def is_num(s):
  try:
    float(s)
  except ValueError:
    return False
  else:
    return True

K=5
cdef sigmoid(float x):
  return 1 / (1 + math.exp(-(K*x)))

cdef relu(float x):
  return x * (x > 0.0)

h = 0.001
def derivative(f, x):
  return (f(x+h) - f(x)) / h

cdef mean(list x):
  return sum(x)/len(x)

cdef class Neuron:
  cdef double dendrite
  cdef double axon
  cdef int size
  cdef public double bias
  cdef public vector[double] weight
  cdef public vector[int] alive

  def __init__(self, list init_weight=[], double init_bias=0, func=None):
    self.dendrite = 0.0
    self.axon = 0.0
    self.bias = init_bias

    self.size = len(init_weight)
    self.weight.reserve(self.size)
    self.alive.reserve(self.size)
    for w in init_weight:
      self.weight.push_back(w)
      self.alive.push_back(int(bool(w)))
    self.h = func if func else sigmoid

  cpdef add(self, vector[double] values):
    self.dendrite = self.bias
    self.dendrite += sum([v*w*alive for v, w, alive in zip(values, self.weight, self.alive)])
    self.axon = self.h(self.dendrite)

  cdef set_weight(self, vector[double] weight):
    self.weight = weight

  cdef set_bias(self, double bias):
    self.bias = bias

  cdef set_value(self, double value):
    self.dendrite = value
    self.axon = value

  cdef double get(self):
    return self.axon

  cdef cut(self, int index):
    self.alive[index] = 0

cdef class Layer:
  cdef public int num
  cdef public list neurons

  def __init__(self, list weights=[], list biases=[], int num=0, bint is_input=False):
    self.num = num if num > 0 else len(weights)
    self.neurons.reserve(self.num)

    cdef int i
    if is_input:
      self.neurons = [Neuron() for _ in range(self.num)]
    else:
      self.neurons = [Neuron(init_weight=weights[i], init_bias=biases[i]) for i in range(self.num)]

  def update_attribute(self, list weights, list biases):
    cdef int i
    for i in range(self.num):
      self.neurons[i].set_weight(weights[i])
      self.neurons[i].set_bias(biases[i])

  def set_values(self, list input_value):
    cdef int i
    for i in range(self.num):
      self.neurons[i].set_value(input_value[i])

  cdef list get_values(self):
    cdef Neuron neuron
    return [neuron.get() for neuron in self.neurons]

  cdef forward(self, Layer next_layer):
    cdef int nn
    for nn in range(next_layer.num):
      next_layer[nn].add(self.get_values())

  cdef backward(self, Layer frontLayer, list errors, double n=0.5):
    cdef:
      list new_errors = []
      list weights = [[] for _ in range(self.num)]
      list biases = []
      Neuron neuron
      double diff, error, out_front, back
      int sn, fn

    for sn in range(self.num):
      neuron = self.neurons[sn]
      diff = derivative(neuron.h, neuron.dendrite)
      error = errors[sn]
      back = error*diff
      biases.append(neuron.bias - n*back)
      new_errors.append(back)
      for fn in range(frontLayer.num):
        out_front = frontLayer.neurons[fn].get()
        weights[sn].append(neuron.weight[fn]-n*out_front*back)
    return weights, biases, new_errors


cdef class Network:
  cdef:
    int input_num, hidden_num, output_num
    list all_w, biases, layers, score
  def __init__(self, int input_num=2, int hidden_num=2, int output_num=1, list weights=[], list biases=[]):
    self.input_num = input_num
    self.hidden_num = hidden_num
    self.output_num = output_num
    self.all_w = weights
    self.biases = biases
    self.score = []
    if (not self.all_w) and (not self.biases):
      self._init_net()

    self.layers = [Layer(num=self.input_num, is_input=True)]
    cdef int i
    for i in range(len(self.all_w)):
      self.layers.append(Layer(weights=self.all_w[i], biases=self.biases[i]))

  cdef _init_net(self, bint place=False):
    cdef:
      list biases, hidden_w, output_w
      Layer layer
      int i
    hidden_w = self._init_weight(self.input_num, self.hidden_num)
    output_w = self._init_weight(self.hidden_num, self.output_num)
    biases = self._init_weight(self.hidden_num, 1)
    biases.extend(self._init_weight(self.output_num, 1))
    self.all_w = [hidden_w, output_w]
    self.biases = biases
    if place:
      for i, layer in enumerate(self.layers[:0:-1]):
        layer.update_attribute(self.all_w[i], self.biases[i])

  cdef _init_weight(self, int in_num, int out_num):
    return [[random.uniform(-2, 2) for _ in range(in_num)] for _ in range(out_num)]

  cdef learning(self, list input_values, list targets, double n=0.5):
    cdef:
      int NNUM, index, i, num, en
      Layer net, layer
      list score, input_layer, target, errors, new_weights, new_biases, new_w, new_b, newError
      double e, error
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
        new_w, new_b, errors = net.backward(self.layers[i-1], errors, n=n)
        new_weights.append(new_w)
        new_biases.append(new_b)

        newError = []
        for num in range(len(net.neurons[0].weight)):
          newError.append(sum([error*net.neurons[en].weight[num] for en, error in enumerate(errors)]))
        errors = newError

      # update weight
      for i, layer in enumerate(self.layers[:0:-1]):
        layer.update_attribute(new_weights[i], new_biases[i])
    return score
  
  cdef fit(self, list test_values):
    cdef:
      int i
      Layer n
    self.layers[0].set_values(test_values)
    for i, n in enumerate(self.layers[:-1]):
      n.forward(self.layers[i+1])
    return self.layers[-1].get_values()


if __name__ == '__main__':
  input_num, hidden_num, output_num = (2, 2, 1)
  net = Network(input_num=input_num, hidden_num=hidden_num, output_num=output_num)

  learning_data = [[0, 0], [0, 1], [1, 0], [1, 1]]
  target_data = [[0], [1], [1], [0]]
  score = net.learning(learning_data, target_data, n=0.99, error=1e-5)[1:]

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
