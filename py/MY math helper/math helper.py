'''
my custom math helper
with symbolic function tools (hopefully)(some day...)

with now 200% ethimological accuarte BackHopping (bc my gf hates me...)

###              edge cases / QoL / To Do (Better)
<green comment>  debug
#                comment


examle funtion to test :   5+(2^(3+4/x)*a)-x/y

raw postfix :   5+(2^(3+4/x]])*]a])-x/y]]]
correct postfix:   5234x/+*a^xy/-+


!!! only single character numbers/variables !!! (for now)
'''
#-----------------------------------------------------------------------------------------------------------#
#functions#

#--- insert back par -------------------------------------------------------#

def insBackPar(func, idx, backParChar):
    #insert back par    ##find better method than redefining "function"
    '''print("sobstitution = ",func[:idx] + backParChar + func[idx:])'''
    return func[:idx] + backParChar + func[idx:]

#--- insert back par -------------------------------------------------------#


#--- postfix encoding ---------------------------------------------------------#

def PostFixEncoder(function):
    
    # Reference list of characters
    opSet = ('+', '-', '*', '/', '^', '&')  # add, sub, mul, div, pow, log
    parSet = ('(', ')')
    backPar = (']')

    opList = []
    numList = []

    #subdivide into subsets
    for char in function :
        if char in opSet:
            opList.append(char)
        elif char not in parSet and char not in backPar :
            numList.append(char)
            
    #- Backhoping -#

    for op in opSet[::-1 ]: #reverse order for priority
        opindex =0 # op counter
        while op in function[opindex+1:] :
            opindex += function[opindex +1:].index(op) +1 # op counter
            '''print("loop at:", opindex,op)'''
        
            i = opindex+1 # reference index
            swim = 0 # is swimming
            
            #hopping
            for hop in function[i:] :
                '''print("hop: ",hop,"    op: ", op)'''
                #EoS check
                if i +1>= len(function) :
                    function += backPar
                    '''print("sub at EoS")'''
                    break 
                
                #par swim
                if hop == parSet[0] :
                    swim +=1
                if hop == parSet[1]:
                    if swim > 0 :
                        swim -=1
                    else:
                        function = insBackPar(function, i, backPar)
                        '''print("sub at close par")'''
                        break
                
                #operand priority check
                if swim <= 0 and hop in opSet:
                    if opSet.index(op) > opSet.index(hop) :
                        function = insBackPar(function, i+1, backPar)
                        '''print("sub at opP",i)'''
                        break  
                    
                i += 1

    #- end Backhoping -#

    #- postfix writing -#

    numIdx = -1
    opIdx = -1
    postFunc = ""

    for step in function : 
        
        #add number to postfix funcion if encountered
        if numIdx +1 < len(numList) and step == numList[numIdx+1] :
            postFunc += step
            numIdx += 1
        
        # operand counter
        if opIdx +1 < len(opList) and step == opList[opIdx+1] :
            opIdx += 1
        
        #add operand at counter then pop it
        if opIdx < len(opList) and step == backPar :
            postFunc += opList[opIdx]
            opList.pop(opIdx)
            opIdx -= 1

    #- end postfix writing -#
    return postFunc
    
#--- postfix encoding ---------------------------------------------------------#

''' !!! #--- function evaluator ---# !!! '''
### manual variables 
def Evaluate(function) :
    funcList = [x for x in function]
    for

#--- function evaluator ---#

#-----------------------------------------------------------------------------------------------------------#

Func = input("insert your function: ")
### Normalize input to standard input set

print("postfix encoded function:",PostFixEncoder(Func))