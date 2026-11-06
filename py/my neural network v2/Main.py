'''
Main script
'''

import numpy as np
from network import Network, Linear, Sigmoid
from model import Training, evaluate
from Datasets import Data

LR = 0.1

net = Network(2, 1, (2, 5, 5, 1), Sigmoid, LR)
net.layers[-1].activation = Linear

def mse(y_pred, y):
    return np.mean((y_pred - y) ** 2)

dataset, X, Y = Data("2d_graph")


Training(net, 100000, LR, mse, dataset, lr_decay_on=True)



error, accuracy = evaluate(net, X, Y)
print(f"Error, accuracy: {error}, {accuracy}")
