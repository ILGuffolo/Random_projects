'''
creation, handling and processing of data
'''

import numpy as np

def build_dataset_list(inputs, outputs):
    dataset = []

    for x, y in zip(inputs, outputs):
        x_arr = np.array(x).reshape(-1, 1)
        y_arr = np.array(y).reshape(-1, 1)

        dataset.append([x_arr, y_arr])

    return dataset

def build_dataset_2dGraph(X, Y, Z):
    dataset = []

    for x, y, z in zip(X, Y, Z):
        x_arr = np.array([x, y], dtype=float).reshape(-1, 1)
        y_arr = np.array(z, dtype=float).reshape(-1, 1)

        dataset.append((x_arr, y_arr))

    return dataset

def Data(tag: str, size=100):
    match tag.lower():
        case "linear_test":
            X = [
                [1, 2, 3],
                [3, 4, 5],
                [5, 6, 7]
            ]

            Y = [
                [3, 5],
                [7, 10],
                [11, 15]
            ]  
            return [build_dataset_list(X, Y), X, Y]
        
        case "xor":
            X = [
                [0, 0],
                [0, 1],
                [1, 0],
                [1, 1]
            ]

            Y = [
                [0],
                [1],
                [1],
                [0]
            ]  
            return [build_dataset_list(X, Y), X, Y]
        
        case "2d_graph":
            f = lambda x, y: x**2 + np.sin(y)
            
            X = np.random.uniform(-1, 1, size=size)
            Y = np.random.uniform(-1, 1, size=size)
            
            Z = f(X,Y)
            
            return [build_dataset_2dGraph(X, Y, Z), zip(X, Y), Z]
        
        case _:
            print("invalid database")
            return None 
            
        
        
        
        
        