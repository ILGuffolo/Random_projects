'''
Layer class
Activation functions
Network class
'''

import numpy as np

class Layer: # --- LAYER --- #

    def __init__(self,
                 input_size,
                 output_size,
                 activation,
                 LearningRate_base):

        limit = np.sqrt(1 / input_size)
        self.weights = np.random.uniform(-limit, limit, size=(output_size, input_size)) * LearningRate_base

        self.biases = np.zeros(
            (output_size, 1)
        )

        self.activation = activation

        self.input = None
        self.z = None
        self.output = None

        self.grad_w = None
        self.grad_b = None
        
    
    def forward(self, x): # Forward pass

        self.input = x

        self.z = self.weights @ x + self.biases

        self.output = self.activation.forward(self.z)

        return self.output
    
    def backward(self, delta, is_activated =True): # Backward prop
        
        if is_activated:
            delta = delta * self.activation.derivative(self.z)

        self.grad_w = delta @ self.input.T

        self.grad_b = delta

        delta_prev = self.weights.T @ delta

        return delta_prev
    
    def update(self, lr): # Gradient descent

        self.weights -= lr * self.grad_w

        self.biases -= lr * self.grad_b
    
    

class Network: # --- NETWORK --- #

    def __init__(self, inputs, outputs, L_size, activation,
                 LearningRate_base):

        self.layers = []
        prev_s = inputs
        
        for s in L_size:
            self.layers.append(Layer(prev_s, s, activation, LearningRate_base))
            prev_s = s
        

    def forward(self, x): # Forward pass

        for layer in self.layers:
            x = layer.forward(x)

        return x
    
    def backward(self, target): #Back prop

        last = self.layers[-1]

        delta = (
            2 * (last.output - target)
        )

        for layer in reversed(self.layers):
            delta = layer.backward(delta)

    def update(self, lr): # Update layers

        for layer in self.layers:
            layer.update(lr)
            
            
# --- ACTIVATION --- #

class Sigmoid: # Sigmoid

    @staticmethod
    def forward(x):
        return 1/(1+np.exp(-x))

    @staticmethod
    def derivative(x):
        s = Sigmoid.forward(x)
        return s*(1-s)
    
class Linear: # Linear

    @staticmethod
    def forward(x):
        return x

    @staticmethod
    def derivative(x):
        return 1