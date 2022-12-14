#   NeuralNetwork.pyx
#c: language_level=3
#distutils: language=c++

import math, random, cython as c

@c.cfunc
def sigmoid(x: c.double) -> c.double:
  K:            c.int = 5
  return 1 / (1 + math.exp(-(K*x)))

@c.cfunc
def derivative(x: c.double) -> c.double:
  h:        c.double = 0.001
  return (sigmoid(x+h) - sigmoid(x)) / h

@c.cclass
class Neuron:
  dendrite:     c.double
  axon:         c.double
  w:            c.double
  size:         c.int
  bias:         c.double
  weight:       c.double[:]
  alive:        c.int[:]

  def __init__(self, init_weight: c.double[:], init_bias: c.double=0.0):
    self.dendrite = 0.0
    self.axon = 0.0
    self.bias = init_bias
    self.weight = [w for w in init_weight]
    self.alive = [int(bool(w)) for w in init_weight]
    self.size = len(init_weight)

  @c.cfunc
  def add(self, values: c.double[:]) -> c.void:
    v:          c.double
    w:          c.double
    alive:      c.bint
    self.dendrite = self.bias
    self.dendrite += sum([v*w*alive for v, w, alive in zip(values, self.weight, self.alive)])
    self.axon = sigmoid(self.dendrite)

  @c.cfunc
  def set_weight(self, weight: c.double[:]) -> c.void:
    self.weight = weight

  @c.cfunc
  def set_bias(self, bias: c.double) -> c.void:
    self.bias = bias

  @c.cfunc
  def set_value(self, value: c.double) -> c.void:
    self.dendrite = value
    self.axon = value

  @c.cfunc
  def get(self) -> c.double:
    return self.axon

  @c.cfunc
  def cut(self, index: c.int) -> c.void:
    self.alive[index] = 0

@c.cclass
class Layer:
  num:          c.int
  neurons:      Neuron[:]

  def __init__(self, weights: c.double[:,:], biases: c.double[:], num: c.int=0, is_input: c.bint=False):
    self.num = num if num > 0 else len(weights)
    i:          c.int
    if is_input:
      self.neurons = [Neuron() for _ in range(self.num)]
    else:
      self.neurons = [Neuron(init_weight=weights[i], init_bias=biases[i]) for i in range(self.num)]

  @c.cfunc
  def update_attribute(self, weights: c.double[:,:], biases: c.double[:]) -> c.void:
    i:          c.int
    for i in range(self.num):
      self.neurons[i].set_weight(weights[i])
      self.neurons[i].set_bias(biases[i])

  @c.cfunc
  def set_values(self, input_value: c.double[:]) -> c.void:
    i:          c.int
    for i in range(self.num):
      self.neurons[i].set_value(input_value[i])

  @c.cfunc
  def get_values(self) -> c.double[:]:
    neuron:     Neuron
    return [neuron.get() for neuron in self.neurons]

  @c.cfunc
  def forward(self, next_layer: Layer) -> c.void:
    nn:         Neuron
    for nn in next_layer.neurons:
      nn.add(self.get_values())

  @c.cfunc
  @c.locals(
    new_errors=c.double[:],
    biases=c.double[:],
    weights=c.double[:,:],
    diff=c.double,
    error=c.double,
    out_front=c.double,
    back=c.double,
    neuron=Neuron,
    sn=c.int,
    fn=c.int
  )
  def backward(self, frontLayer: Layer, errors: c.double[:], n: c.double=0.5) -> tuple:
    weights = [[] for _ in range(self.num)]

    for sn in range(self.num):
      neuron = self.neurons[sn]
      back = errors[sn]*derivative(neuron.dendrite)
      biases.append(neuron.bias - n*back)
      new_errors.append(back)
      for fn in range(frontLayer.num):
        out_front = frontLayer.neurons[fn].get()
        weights[sn].append(neuron.weight[fn]-n*out_front*back)
    return weights, biases, new_errors

@c.cclass
class Network:
  input_num:    c.int
  hidden_num:   c.int
  output_num:   c.int
  all_w:        c.double[:,:,:]
  biases:       c.double[:,:]
  score:        c.double[:]
  layers:       Layer[:]
  def __init__(self, input_num: c.int=2, hidden_num: c.int=2, output_num: c.int=1, weights: c.double[:,:,:], biases: c.double[:,:]):
    i:          c.int
    self.input_num = input_num
    self.hidden_num = hidden_num
    self.output_num = output_num
    self.all_w = weights
    self.biases = biases
    if len(self.all_w) < 1 and len(self.biases) < 1:
      self._init_net()

    self.layers = [Layer(num=self.input_num, is_input=True)]
    for i in range(len(self.all_w)):
      self.layers.append(Layer(weights=self.all_w[i], biases=self.biases[i]))
  
  @c.cfunc
  @c.locals(
    hidden_w=c.double[:,:],
    output_w=c.double[:,:],
    biases=c.double[:,:],
    layer=Layer,
    i=c.int,
  )
  def _init_net(self, place: c.bint=False):
    hidden_w = self._init_weight(self.input_num, self.hidden_num)
    output_w = self._init_weight(self.hidden_num, self.output_num)
    biases = self._init_weight(self.hidden_num, 1)
    biases.extend(self._init_weight(self.output_num, 1))
    self.all_w = list((hidden_w, output_w))
    self.biases = biases
    if place:
      for i, layer in enumerate(self.layers[:0:-1]):
        layer.update_attribute(self.all_w[i], self.biases[i])

  @c.cfunc
  def _init_weight(self, in_num: c.int, out_num: c.int) -> c.double[:, :]:
    return [[random.uniform(-2, 2) for _ in range(in_num)] for _ in range(out_num)]

  @c.cfunc
  @c.locals(
    index=c.int,
    i=c.int,
    num=c.int,
    en=c.int,
    net=Layer,
    layer=Layer,
    input_layer=c.double[:],
    new_weights=c.double[:,:,:],
    target=c.double[:],
    errors=c.double[:],
    newError=c.double[:],
    new_biases=c.double[:,:],
    new_w=c.double[:],
    new_b=c.double[:],
    score=c.double[:],
    e=c.double,
    err=c.double,
    NNUM=c.int
  )
  def learning(self, input_values: c.double[:,:], targets: c.double[:,:], n: c.double=0.5) -> c.double[:]:
    NNUM = len(self.layers)
    for index, input_layer in enumerate(input_values):
      self.layers[0].set_values(input_layer)
      target = targets[index]

      for i in range(NNUM-1):
        self.layers[i].forward(self.layers[i+1])

      # calc error and score
      out_values = self.layers[-1].get_values()
      errors = [-(target[i]-out_values[i]) for i in range(len(target))]
      score.append(sum([(1/len(errors))*(e**2) for e in errors]))

      for i in range(NNUM-1, 0, -1):
        net = self.layers[i]
        new_w, new_b, errors = net.backward(self.layers[i-1], errors, n=n)
        new_weights.append(new_w)
        new_biases.append(new_b)

        for num in range(len(net.neurons[0].weight)):
          newError.append(sum([error*net.neurons[en].weight[num] for en, error in enumerate(errors)]))
        errors = newError

      # update weight
      for i, layer in enumerate(self.layers[:0:-1]):
        layer.update_attribute(new_weights[i], new_biases[i])
    return score

  @c.cfunc
  def fit(self, test_values: c.double[:,:]) -> c.double[:]:
    i:          c.int
    n:          Layer
    self.layers[0].set_values(test_values)
    for i, n in enumerate(self.layers[:-1]):
      n.forward(self.layers[i+1])
    return self.layers[-1].get_values()
