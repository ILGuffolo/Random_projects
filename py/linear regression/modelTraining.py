import csvLinReg as reg
import numpy as np
import pandas as pd
import os

### parameters ###
outDir = "out_dir"
inputDir = "enhanced_student_habits_performance_dataset.csv"

'''
### compiling ###
reg.split_csv_columns_to_files(inputDir, outDir)
reg.index_column_values(outDir)

### classyfy ###
reg.classify_files(outDir)
'''
### least squares ###
inHeaders, inMatrix = reg.build_numpy_matrix_from_files(outDir + '\input')
outHeaders, outMatrix = reg.build_numpy_matrix_from_files(outDir + '\output')
model = reg.solve_least_squares(inMatrix, outMatrix)

### test ###
def test_evaluate(testID):
    testDict = reg.create_dictionary_for_testing(testID, outDir + '\input')
    testmodel = np.insert(model['solution'], 0, [0]) #adding "intercept"? bho nn so proviamo
    predictions = reg.predict_from_coefficients(testmodel, testDict, inHeaders)
    print(predictions)
    return predictions

### run ###
def evaluateModel():
    entry = {}
    for category in inHeaders:
        if os.path.exists(f"{outDir}\map\{category}.txt"):
            with open(f"{outDir}\map\{category}.txt") as indexMap:
                print(f"insert {category} :\n")
                lines = indexMap.readlines()
                for l in lines:
                    print(l)
        entry[category] = float(input(f"{category} : value = "))
        print('\n')

    interceptedModel = np.insert(model['solution'], 0, [0]) #adding "intercept"? bho nn so proviamo
    predictions = reg.predict_from_coefficients(interceptedModel, entry, inHeaders)
    print(predictions)
    
    return predictions

### accuracy ###
def accuracyCalc():
    
    with open(inputDir, 'r') as file:
        contents = file.read()
        line_count = contents.count('\n') -1
        
        with open(f"out_Dir\output\{outHeaders[0]}.txt", 'r') as outFile:  #temp
            lines = outFile.readlines()
            
            accuracySamples = float(input("insert accuracy sample percentage: ")) / 100.0
            
            step = int(1 / accuracySamples)
            counter = 0
            accuracy = 0

            for ID in range(1,line_count,step):
                counter += 1
                
                accuracy += (test_evaluate(ID) - float(lines[ID])) / 100 #temp
                
                print("counter: " + str(counter))
                print("ID: " + str(ID))
            accuracy /= counter
            accuracy *= 100
            print("error% = ", accuracy)
