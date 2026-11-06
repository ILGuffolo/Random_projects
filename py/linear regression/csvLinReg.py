import os
import shutil
import numpy as np

def split_csv_columns_to_files(csv_path: str, output_dir: str) -> None:
    """
    Splits columns of a CSV-formatted TXT file into separate TXT files.
    Each file is named after its column header.
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    headers = lines[0].split(',')
    columns = [[] for _ in headers]

    for line in lines[1:]:
        values = line.split(',')
        for i, val in enumerate(values):
            columns[i].append(val)

    for i, header in enumerate(headers):
        with open(os.path.join(output_dir, f"{header}.txt"), 'w', encoding='utf-8') as f:
            f.write(header + '\n')
            f.write('\n'.join(columns[i]))

def index_column_values(directory: str):
    """
    Replaces each unique string value in every TXT file with a consistent integer index.
    """
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not filename.endswith('.txt') or os.path.isdir(filepath):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            if not is_number(lines[1]): #test for numerical values to leave intact
                header, *values = lines
                mapping = {}
                counter = 0
                indexed = []
                for val in values:
                    if val not in mapping:
                        mapping[val] = counter
                        counter += 1
                    indexed.append(str(mapping[val]))
                
                print_mapping(mapping, header) #index reference
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(header + '\n')
                    f.write('\n'.join(indexed))
        
def print_mapping(mapping: dict, header):
    os.makedirs("out_dir\map", exist_ok=True )
    with open(f"out_dir\map\{header}.txt", 'w') as mapFile:
        for key in mapping:
            mapFile.write(str(key) + ',' + str(mapping[key]) + '\n')

def classify_files(directory: str) -> None:
    """
    Asks the user to classify each file as 'input' or 'output',
    then moves it into a corresponding subdirectory.
    """
    input_dir = os.path.join(directory, "input")
    output_dir = os.path.join(directory, "output")
    ignore_dir = os.path.join(directory, "ignore")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not filename.endswith('.txt') or os.path.isdir(filepath):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            header = f.readline().strip()

        print(f"\nFile: {filename}\nHeader: {header}")
        while True:
            classification = input("Classify this file as 'input' or 'output': ").strip().lower()
            if classification in ("input", "output", "ignore"):
                break
            print("Invalid input. Please type 'input', 'output' or 'ignore'.")

        if classification == 'input': dest = input_dir
        elif classification == 'output': dest = output_dir
        else :dest = ignore_dir
        shutil.move(filepath, os.path.join(dest, filename))

def build_numpy_matrix_from_files(directory: str):
    """
    Builds a NumPy matrix and header list from indexed TXT files in the directory.
    """
    file_list = sorted(
        [f for f in os.listdir(directory) if f.endswith('.txt') and os.path.isfile(os.path.join(directory, f))]
    )
    headers, columns = [], []

    for filename in file_list:
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        headers.append(lines[0])
        data = [float(val) for val in lines[1:]]
        columns.append(data)

    min_len = min(len(col) for col in columns)
    trimmed = [col[:min_len] for col in columns]
    matrix = np.array(trimmed).T
    return headers, matrix


def solve_least_squares(A: np.ndarray, b: np.ndarray):
    """
    Solves Ax = b using the Least Squares Method and returns full result.
    """
    x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    return {
        'solution': x,
        'residuals': residuals,
        'rank': rank,
        'singular_values': s
    }

def predict_from_coefficients(coefficients: np.ndarray, input_values: dict, headers: list) -> float:
    """
    Predicts a value based on coefficients and a dict of input values.
    Assumes first coefficient is intercept.
    """
    #print(len(coefficients))
    #print(len(headers) +1)
    if len(coefficients) != len(headers) +1 : 
        raise ValueError("Coefficient count must include intercept and match number of headers.")

    prediction = coefficients[0]  # intercept
    for i, header in enumerate(headers):
        if header not in input_values:
            raise ValueError(f"Missing input for header: {header}")
        prediction += coefficients[i + 1] * input_values[header]

    return prediction

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def create_dictionary_for_testing(line_number, directory):
    result = {}

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path) and filename.endswith(('.txt', '.csv')):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    
                    if len(lines) == 0:
                        continue  # Skip empty files

                    header = lines[0].strip()
                    if line_number < len(lines):
                        value = float(lines[line_number].strip())
                    else:
                        value = None  # Line number out of range
                    
                    result[header] = value
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    return result
