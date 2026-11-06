import random as rd
import csv

'''
Function needed for data ghathering and polishing 
'''


#Generated Values for testing
def DataTest (name, test= False, Nin= 1):
    if test or string(type(name)) == "<class 'int'>":
        match int(name):
            case 1:
                #test 1
                # Linear function
                m0 = 10
                m = []
                q = 3
                X = []
                
                for i in range(Nin):
                    X.append(rd.randrange(-10, 10))
                    m.append(m0-i)
                
                F = q
                for j in range(len(X)):
                    F += m[j]*X[j]
                
                return ([[X], [F]])
            
            case 2:
                #test 2
                # sigmoid approx
                x = rd.random()*2-1 #number in {-1, 1}
                return [[x], [1 if x>0 else 0]]
            
            case 3:
                #test 3
                # Multi output (sign and magnitude)
                x = rd.random()*2-1 #number in {-1, 1}
                return [[x], [1 if x>0 else 0, abs(x)]]
            case _:
                #test General
                print("Invalid test code")
                
    else:
        pass
        
    return NotImplemented


#Get Data from CSV
def DataGet(dataIndex):
    match dataIndex:
        case 1:
            data = []
            with open("Datasets/Gender.csv", "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert numeric fields to float/int if needed
                    row = {k: float(v) if v.replace('.', '', 1).isdigit() else v for k, v in row.items()}
                    data.append(row)
            
            remove_column(data, "Likeness")
            Normalize_to_bool(data, "Gender")
            
            return RefineData(data, ["Gender"])
        
        case _:
            print("invalid index")
    
def Normalize_to_bool(data, column):

    # get all unique string values for that column
    values = [row[column] for row in data]
    uniques = list(dict.fromkeys(values))  # preserve order, no duplicates

    if len(uniques) != 2:
        raise ValueError(f"Column '{column}' must have exactly 2 unique values, found {uniques}")

    mapping = {uniques[0]: 1, uniques[1]: 0}

    # replace in place
    for row in data:
        row[column] = mapping[row[column]]

    return mapping

def remove_column(data, column):
    for row in data:
        if column in row:
            del row[column]
            
def RefineData(data, output_columns):
    DT = []

    for row in data:
        # Inputs: all columns except the output columns
        input_row = [v for k, v in row.items() if k not in output_columns]

        # Outputs: all specified output columns
        output_row = [row[k] for k in output_columns]
        
        DT.append([input_row, output_row])

    return DT

