import random

def my_sign(x):
  return int(x > 0) - int(x < 0)

def linspace(start, end, sep):
  if start - end == 0:
    return []
  if sep > 1:
    div = (end-start) / (sep-1)
  elif sep == 1:
    div = end-start
  return tuple([start + div*i for i in range(sep)])

def test():
  import numpy as np
  ci = 3
  cn = 2
  w_fix = 0.7*(cn**(1/ci))

# Normalize
  wnp = np.random.rand(cn, ci) - 0.5
  wl = [[w for w in wn] for wn in wnp]
  
  wnpb = np.square(wnp).sum(axis=1).reshape(cn, 1)
  wnpr = np.sqrt(1. / wnpb)
  wlr = tuple([(1 / (sum([(w**2) for w in ws])**(1/2))) for ws in wl])

  wnpa = w_fix*wnpr*wnp
  wla = tuple([tuple([w_fix * we * w for w in ws]) for we, ws in zip(wlr, wl)])
  
  bnpline = np.linspace(-1, 1, cn)
  bnpsign = np.sign(wnpa[:, 0])
  bnp = np.array([0]) if cn == 1 else w_fix * bnpline * bnpsign
  
  bllines = linspace(-1, 1, cn)
  blsigns = [my_sign(ws[0]) for ws in wla]
  bl = tuple([0]) if cn == 1 else tuple([w_fix * bll * bls for bll, bls in zip(bllines, blsigns)])
  
# Scaleble to inp_active
  amin, amax = (0, 1) # this network input value is 0 or 1
  X = 0.5 * (amax - amin)
  Y = 0.5 * (amax + amin)
  
  wanp = X * wnpa
  banp = X * bnp + Y
  W = tuple([tuple([X * w for w in ws]) for ws in wla])
  B = tuple([X * b + Y for b in bl])
  
# Scaleble to minmax
  npminmax = np.array([[0, 1] for _ in range(ci)])
  minmax = tuple([(0, 1) for _ in range(ci)])

  npx = 2. / (npminmax[:, 1] - npminmax[:, 0])
  npy = 1. - npminmax[:, 1] * npx
  npw = wanp * npx
  npb = np.dot(npw, npy) + banp
  print(npx)
  print(npy)
  print(npw)
  print(npb)

  minmax = tuple([(0, 1) for _ in range(ci)])
  X = tuple([2 / (s-f) for f, s in minmax])
  Y = tuple([1 - (mm[1] * x) for mm, x in zip(minmax, X)])
  W = tuple([tuple([w * x for w, x in zip(wl, X)]) for wl in W])
  B = tuple([sum([w * y for w, y in zip(wl, Y)]) + b for wl, b in zip(W, B)])
  print(W)
  print(B)
  return wl

# 正規化
# for initialization of the weights of NeuralNetwork to reduce training time
# determining weights of the data generated which will be adjusted to its weight
def NguyenWidrow(ci, cn, defaultMinMax=(0, 1)): # ci: number of input units, cn: number of hidden units
  w_fix = 0.7*(cn**(1/ci)) # scale factor

  # for all input units, random number between -0.5 and -0.5
  initialWeights = tuple([tuple([random.uniform(-0.5, 0.5) for _ in range(ci)]) for _ in range(cn)])

  # calculate the value ||vj(old)||
  if ci == 1:
    W = tuple([tuple([w_fix * (w/abs(w)) for w in wl]) for wl in initialWeights])
  else:
    weights = tuple([sum([(w**2) for w in wl])**(1/2) for wl in initialWeights])
    W = tuple([tuple([w_fix * w / weight for w in wl]) for weight, wl in zip(weights, initialWeights)])

  # bias used as initialization
  lines = linspace(-1, 1, cn)
  signs = [my_sign(wl[0]) for wl in W]
  B = tuple([0]) if cn == 1 else tuple([w_fix * line * sign for line, sign in zip(lines, signs)])
  # B = tuple([random.uniform(-w_fix, w_fix) for _ in range(ci)])

  # Scaleble to inp_active
  amin, amax = defaultMinMax    # this network input value is 0 or 1
  X = 0.5 * (amax - amin)
  Y = 0.5 * (amax + amin)
  W = tuple([tuple([X * w for w in wl]) for wl in W])
  B = tuple([X * b + Y for b in B])

  # Scaleble to minmax
  minmax = tuple([defaultMinMax for _ in range(ci)])
  X = tuple([2 / (s-f) for f, s in minmax])
  Y = tuple([1 - (mm[1] * x) for mm, x in zip(minmax, X)])
  W = tuple([tuple([w * x for w, x in zip(wl, X)]) for wl in W])
  B = tuple([sum([w * y for w, y in zip(wl, Y)]) + b for wl, b in zip(W, B)])
  return W, B

# Self-Organizing Map is a clustering approach for input data
def Kohonen():
  pass

def _kohonen_init():
  return random.random()

if __name__ == '__main__':
  initialW = test()
  W, B = NguyenWidrow(3, 2, initialW)
  print(W)
  print(B)
  pass