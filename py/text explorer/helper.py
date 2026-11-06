'''
some general helper functions
'''

import json

def load_entry(filename, index):# read JSON files
    try:
        with open("data/" + filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON root must be a list")

        return data[index]

    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None

    except IndexError:
        print(f"Invalid index: {index}")
        return None

    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {filename}")
        print(e)
        return None
