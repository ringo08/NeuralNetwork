from setuptools import setup
import os
from Cython.Build import cythonize

setup(
  ext_modules=cythonize(os.path.join('src', 'CythonNNApp', 'NeuralNetwork.pyx'))
)