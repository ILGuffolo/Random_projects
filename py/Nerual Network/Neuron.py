import math

'''
Functions and classes needed for the neural network
'''

class Neuron:
    def __init__(self, layer, activation, learnRate, LeakAlpha = 0.01):
        
        self.W = [] #list of weights (must be initialized)
        self.B = None #Bias (must be initialized)
        self.layer = layer #layer index
        self.actv = activation #activation function index (0=linear, 1= ReLU, 2= sigmoid, 3 Leaky ReLU)
        self.alpha = LeakAlpha #alpha value for leaky ReLU
        self.x = []
        self.z = None 
        self.a = None 
        self.mu = learnRate
        
        
    
    #initialization of values
    def InitVal(self, BrainStack, val):
        for i in BrainStack[self.layer-1]:
            self.W.append(val[0])
        
        self.B = val[1]
    
    #Activation function
    def activation(self, val):
        match self.actv:
            case 0: #linear
                return val
            case 1: #ReLU
                return max(0, val)
            case 2: #Sigmoid
                return 1 / (1 + math.exp(-val))
            case 3: #Leaky ReLU
                x if x > 0 else self.alpha * x
            
    #Deactivation gradient
    def anti_activation(self, val):
        match self.actv:
            case 0: #linear
                return 1
            case 1: #ReLU
                return 1 if val > 0 else 0
            case 2: #Sigmoid
                return val * (1 - val)
            case 3: #Leaky ReLU
                return 1 if x > 0 else self.alpha
    
    #forward pass
    def FPass(self, BrainStack):
        self.x.clear()
        #get relative input
        if self.layer == 1:
            for i in BrainStack[0]:
                self.x.append(i)
        else:
            for nur in BrainStack[self.layer -1]:
                self.x.append(nur.a)
        
        #pre-activation
        self.z = self.B
        for i in range(len(self.x)):
            self.z += self.x[i] * self.W[i]
            
        #Debug
        if any(math.isnan(v) for v in self.x) or math.isnan(self.z):
            print("NaN detected in pre-activation!")
        
        #activation
        self.a = self.activation(self.z)
        
    
    #Gradiant descent
    def Learn(self, Grad):
        for i in range(len(self.W)):
            self.W[i] -= self.mu[0] * Grad * self.x[i]
        self.B -= self.mu[1] * Grad


    # Gradient function
    def Grad(self, val, pred, functionIndex = 0):
        epsilon = 1e-10
        AntiActv = self.anti_activation(self.a)
        match functionIndex:
            case 0: #L1 (absolute value)
                return AntiActv * (-((val-pred) / (abs(val-pred) + epsilon)))
            case 1: #MSE (square)
                return AntiActv * (2* (val - pred))

# Loss Function
def Loss(val, pred, functionIndex = 0):
    total_loss = 0.0
    for val, pred in zip(val, pred):
        match functionIndex:
            case 0: #L1 (absolute value)
                total_loss += abs(val - pred)
            case 1: #MSE (square)
                total_loss += ((val - pred)**2) /2
                
    return  total_loss


    