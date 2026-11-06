'''
functions for easy model handling
'''
import numpy as np
from random import randrange

def Training(net, epochs, lr, F_loss, dataset, lr_decay_on = False, debug=False):
    print("started training: epoch - loss")
    
    scheduler = PlateauScheduler(lr)
    for i in range(epochs): #training loop
        loss = 0
        for x, y in dataset:
            # forward
            pred = net.forward(x)

            # loss (average)
            loss += F_loss(pred, y) / len(dataset)

            # backward
            net.backward(y)

            # update
            net.update(lr)
            
        # update lr if needed
        if lr_decay_on: lr = scheduler.step(loss)
        

        if i % (epochs/10) == 0:
            print(i, loss)
            
    if debug:
        print("Debug:")
        print("prediction:", pred)
        print("loss:", loss)

        for i, layer in enumerate(net.layers):
            print("Layer", i)
            print("grad_w")
            print(layer.grad_w)
            print("weights")
            print(layer.weights)

def evaluate(net, inputs, expected):
    
    results = []
    in_arr = [np.array(inp, dtype=float).reshape(-1, 1) for inp in inputs]
    
    for i in in_arr:
        results.append(net.forward(i))
    
    accuracy = [(1 - (r/e)) for r, e in zip(results, expected)]
    return [np.mean((results - expected) ** 2), np.mean(accuracy)]
    
    
class PlateauScheduler:

    def __init__(self,
                 lr,
                 factor=0.9,
                 patience=1000,
                 tolerance=1e-5,
                 min_lr=1e-5):

        self.lr = lr
        self.factor = factor
        self.patience = patience
        self.tolerance = tolerance
        self.min_lr = min_lr
        self.updates = 0

        self.best_loss = float("inf")
        self.wait = -self.patience *100

    def step(self, loss):

        if self.best_loss == float("inf"):
            self.best_loss = loss
            return self.lr

        improvement = (self.best_loss - loss) / max(self.best_loss, 1e-12)

        if improvement > self.tolerance:
            self.best_loss = loss
            self.wait = 0
        else:
            self.wait += 1

        if self.wait >= self.patience:
            self.lr = max(self.lr * self.factor, self.min_lr)
            self.wait = -self.patience *100 #time to sabilize and explore
            self.updates +=1
            print(f"lr updated {self.updates} to {self.lr}")

            

        return self.lr
