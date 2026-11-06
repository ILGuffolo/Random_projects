import Neuron as nrn
import Data as dt

import matplotlib.pyplot as plt
import time
import math

'''
Core of the program 
'''

#learning parameters
learnRate = [1, 1] # W, B
activation_Function = [2, 0] #0=linear, 1=ReLU, 2=sigmoid, 3=leaky ReLU
lossFunction = 0        #0=L1, 1=MSE
startingWheight = [1, 1]
inputNumbers = 200 #used for tests
Ntest = "3"
isTest = True 

DataStack = []

#data setup
for i in range(inputNumbers):
    DataStack.append(dt.DataTest(Ntest, isTest))

#brain setup
BrainStack = [range(len(DataStack[0][0]))] # array of array: 0 is input 1,2,3... neuron layers

#neuron setup
BrainStack.append([])
BrainStack[1].append(nrn.Neuron(1, activation_Function[0], learnRate))
BrainStack[1].append(nrn.Neuron(1, activation_Function[1], learnRate))
for n in BrainStack[1]: n.InitVal(BrainStack, startingWheight)

#plot setup
fig, axs = plt.subplots(2, 1)  # 2 row, 1 columns
axs[0].grid(True)
axs[1].grid(True)
lossY = []
relLossY = []
meanLoss = 0

#training loop
epoch = 2000
Ypred = []

print("Training started...")
for e in range(epoch):
    meanLoss = 0
    for d in DataStack:
        BrainStack[0] = d[0]
        for i, n in enumerate(BrainStack[1]):
            n.FPass(BrainStack)
            Ypred.append(n.a)
            n.Learn(n.Grad(d[1][i], Ypred[i], lossFunction))
        
        #diagnose graph
        meanLoss += nrn.Loss(d[1], Ypred, lossFunction)
    lossY.append( meanLoss / len(DataStack))
    if len(lossY) >= 2:
        relLossY.append( (lossY[-2] - lossY[-1]) / lossY[-2])
        
    #markers where loss increasing
    increase_indices = [i for i in range(1, len(lossY)) if lossY[i] > lossY[i-1]]
    increase_values = [lossY[i] for i in increase_indices]

#print results
print("\nCompleted")
print("mean loss last epoch: ", meanLoss/len(DataStack))
#print("rellos: ", relLossY)

#plot print
axs[0].plot(lossY, color='blue')
axs[0].scatter(increase_indices, increase_values, color='red', marker='^', s=80, label='Loss increased')
axs[1].plot(relLossY, color='red')
axs[1].set_yscale('symlog', linthresh=1e-12) 
plt.show() 
