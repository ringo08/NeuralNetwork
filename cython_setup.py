import os, sys
sys.path.append('.')
from setuptools import setup
from Cython.Build import cythonize

setup(
  name='Neural Network App',
  ext_modules=cythonize(os.path.join('src', 'CythonNeuralNetwork', 'NeuralNetwork.pyx')),
  zip_safe=False
)
