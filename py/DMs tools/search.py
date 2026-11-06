import json
from pathlib import Path
import re

BASE_PATH = Path("5etool\data")

def load_category(path, key):
    entries = []
    full_path = BASE_PATH / path

    if not full_path.exists():
        print(f"Path not found: {full_path}")
        return []

    # Case 1: It's a directory
    if full_path.is_dir():
        for file in full_path.glob("*.json"):
            try:
                with open(file, encoding="utf-8") as f:
                    data = json.load(f)
                    if key in data:
                        entries.extend(data[key])
            except Exception as e:
                print(f"Error reading {file}: {e}")

    # Case 2: It's a single file
    elif full_path.is_file():
        try:
            with open(full_path, encoding="utf-8") as f:
                data = json.load(f)
                if key in data:
                    entries.extend(data[key])
        except Exception as e:
            print(f"Error reading {full_path}: {e}")

    return entries


print("Loading data...")

# === add categories here ===#
spells = load_category("spells", "spell")
monsters = load_category("bestiary", "monster")
classes = load_category("class", "class")
races = load_category("races.json", "race")
backgrounds = load_category("backgrounds.json", "background")
feats = load_category("feats.json", "feat")
items = load_category("items.json", "item")
skills = load_category("skills.json", "skill")

categories = [spells, monsters, classes, races, backgrounds, feats, items, skills]
catNames = ["spells", "monsters", "classes", "races", "backgrounds", "feats", "items", "skills"]

print("Done.\n")


def find_by_name(collection, name):
    name = name.strip().lower()
    for entry in collection:
        if entry["name"].lower() == name:
            return entry
    return None


def print_entry(entry, indent=0):
    """
    Nicely prints a 5etools entry (spell, monster, item, etc.)
    """
    spacer = "  " * indent

    # Print the name first
    print(f"\n{spacer}=== {entry.get('name', 'Unknown')} ===\n")

    for key, value in entry.items():
        if key == "name":
            continue  # already printed

        # Simple types
        if isinstance(value, (str, int, float, bool)):
            print(f"{spacer}{key.capitalize()}: {clean_value(value)}")

        # List of strings
        elif isinstance(value, list) and all(isinstance(v, str) for v in value):
            print(f"{spacer}{key.capitalize()}:")
            for v in value:
                print(f"{spacer}  - {clean_value(v)}")

        # List of dicts
        elif isinstance(value, list) and all(isinstance(v, dict) for v in value):
            print(f"{spacer}{key.capitalize()}:")
            for v in value:
                # If it has name and entries (like spell traits), print nicely
                if "name" in v and "entries" in v:
                    print(f"{spacer}  {clean_value(v['name'])}:")
                    for e in v["entries"]:
                        if isinstance(e, str):
                            print(f"{spacer}    {clean_value(e)}")
                        else:
                            # handle nested dicts inside entries
                            for k2, v2 in e.items():
                                print(f"{spacer}    {clean_value(k2)}: {clean_value(v2)}")
                else:
                    # generic dict print
                    for k2, v2 in v.items():
                        print(f"{spacer}  {clean_value(k2)}: {clean_value(v2)}")

        # Simple dict
        elif isinstance(value, dict):
            print(f"{spacer}{key.capitalize()}:")
            for k2, v2 in value.items():
                print(f"{spacer}  {clean_value(k2)}: {clean_value(v2)}")

        # Anything else
        else:
            print(f"{spacer}{key.capitalize()}: {clean_value(value)}")
            
def clean_5etools_text(text):
    if not isinstance(text, str):
        return text
    # Replace {@tag stuff|...|visible} → visible
    def repl(m):
        parts = m.group(0).strip('{}').split('|')
        return parts[0] if parts else ''
    text = re.sub(r'{@[^{}]+}', repl, text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'^@\w+\s+', '', text)
    text = re.sub(r'@[\w]+\s', '', text)
    text = re.sub(r'\|.*?\|', '', text)
    return text.strip()
    

def clean_value(value):
    """
    Recursively clean 5etools tags inside strings, lists, or dicts
    """
    if isinstance(value, str):
        return clean_5etools_text(value)
    elif isinstance(value, list):
        return [clean_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: clean_value(v) for k, v in value.items()}
    else:
        return value
    

def search(): 
    while True:
        
        print("\nSelect category:")
        for i in range(len(categories)):
            print(f"{i+1} - {catNames[i]}")
            
        print(f"---\n{i+2} - Exit")

        choice = int(input("> ").strip())

        if choice == len(categories)+1:
            break

        if choice > len(categories)+1:
            print("Invalid choice")
            continue

        # Convert choice to integer index (lists are 0-based)
        index = int(choice) - 1
        collection = categories[index]

        name = input("Enter name: ").strip()
        entry = find_by_name(collection, name)

        if entry:
            print_entry(entry)
        else:
            print("No entry found with that name.")
        
    

#===================================   MAIN   ===================================#

