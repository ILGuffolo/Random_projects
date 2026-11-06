'''
a set of tests for the Layer class
'''

import numpy as np
from network import Layer, Sigmoid


print("\n Debug: sanity test - ((2, 3)(3, 1)(2, 1))")
x = np.array([
    [1],
    [2],
    [3]
])
layer = Layer(3, 2, Sigmoid)

print(layer.weights.shape)
print(x.shape)
print(layer.forward(x).shape)


print("\n Debug: forward test - 27, 59")
layer.weights = np.array([
    [1.,2.],
    [3.,4.]
])

layer.biases = np.array([
    [10.],
    [20.]
])

x = np.array([
    [5.],
    [6.]
])

layer.forward(x)
print(layer.z)


print("\n Debug: activation test - 0.5, 0.25")
print(Sigmoid.forward(0))
print(Sigmoid.derivative(0))

print("\n Debug: gradient test - [[0.1 0.2] [0.3 0.6]]")
layer.input = np.array([
    [1.],
    [2.]
])

delta = np.array([
    [0.1],
    [0.3]
])

layer.backward(delta, is_activated=False)

print(layer.grad_w)


print("\n Debug: update test - [[0.9,1.8], [2.7,3.6]]")
layer.weights = np.array([[1.,2.], [3.,4.]])

layer.grad_w = np.array([[0.1,0.2], [0.3,0.4]])

lr = 1.

layer.update(lr)
print(layer.weights)


