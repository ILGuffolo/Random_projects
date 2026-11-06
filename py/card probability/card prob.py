from math import factorial as fact

Nr = 4
U = []

def binDist(k, p):
    #binomial distribution
    delta = fact(Nr) / (fact(k) * fact(Nr - k))
    P = delta * (p**k) * ((1 - p)**(Nr - k))
    #print(f"debug: P({k}) = {P})")
    #print(f"debug: d={delta}, p={p}")
    return P


def victoryMean(val, numList):
    #mean victory of an occurrence
    if val not in U:
        U.append(val)
        somma = 0
        for i in range(Nr+1):
            somma += i * binDist(i, numList.count(val) / len(numList))
            
        return somma
    else:
        #print(f"debug: skipped repeated value")
        return 0

def victoryTotal(numList):
    #sum of victories
    U.clear()
    somma = 0
    for i in range(len(numList)):
        somma += victoryMean(numList[i], numList)
    
    return somma

## MAIN ##
somma = 0
for i in range(1500):
    l = list(range(1, i+2))
    somma += victoryTotal(l)
    print(f"running average: {somma / (i+1)}")
    

    

        