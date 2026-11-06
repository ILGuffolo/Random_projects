import random
import re
from pathlib import Path
from datetime import datetime
import json

#=== roller ===

def roll_dice_expression(expr):
    """
    Rolls a dice expression like:
    3d4 + 2 + 4d6 -1
    Returns total and detailed breakdown.
    """

    expr = expr.replace(" ", "")
    total = 0
    breakdown = []

    # Split into + and - tokens while keeping the sign
    tokens = re.findall(r'[+-]?[^+-]+', expr)

    for token in tokens:
        sign = -1 if token.startswith('-') else 1
        token = token.lstrip('+-')

        # Dice term
        if 'd' in token:
            num, faces = token.split('d')
            num = int(num) if num else 1
            faces = int(faces)

            rolls = [random.randint(1, faces) for _ in range(num)]
            subtotal = sum(rolls)

            total += sign * subtotal
            breakdown.append(f"{'-' if sign==-1 else ''}{num}d{faces} {rolls}")

        # Flat number
        else:
            value = int(token)
            total += sign * value
            breakdown.append(f"{'-' if sign==-1 else ''}{value}")

    return total, breakdown


def roll(expr):
    """
    Supports optional N prefix:
    N 3d6+4
    """

    expr = expr.strip()

    # Check if expression starts with repetition number
    match = re.match(r'^(\d+)\s+(.*)', expr)
    if match:
        times = int(match.group(1))
        expr = match.group(2)
    else:
        times = 1

    results = []

    for _ in range(times):
        total, breakdown = roll_dice_expression(expr)
        results.append((total, breakdown))

    return results

def print_roll(results, name = "Undefined"):
    roll_format = f"({len(results)}) " if len(results) != 1 else ""
    for token in results[0][1]:
        roll_format += f"+{token.split()[0]}"
    roll_format = roll_format.replace("+", "", 1)
    
    
    print(f"=== {name}:{roll_format} ===")
    for i, (total, details) in enumerate(results, 1):
        print(f"\n- Roll {i}:")
        print("  Details:", details)
        print("  Total:", total)
    print("\n=========\n")


# === logger ===

LOG_BASE = Path("logs")

def write_log(key, message, timestamp=True):

    LOG_BASE.mkdir(exist_ok=True)
    file_path = LOG_BASE / f"{key}.txt"

    # Standard timestamp format
    ts_format = "%Y-%m-%d %H:%M:%S"
    TS_WIDTH = len(datetime.now().strftime(ts_format)) +2 # fixed width

    if timestamp == True:
        ts =f"[{datetime.now().strftime(ts_format)}]"
    elif timestamp == False:
        # Fill with spaces of same length
        ts = " " * TS_WIDTH
    else:
        # If user passes a custom string
        ts =f"[{str(timestamp)}]".ljust(TS_WIDTH, '-')


    line = f"{ts} {message}\n"

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{ts} {message}\n")
        


# === tracker ===

INFO_BASE = Path("info")
INFO_BASE.mkdir(exist_ok=True)

def set_info(key, attribute, value):
    """
    Sets or updates an attribute in a key's info file.
    
    Parameters:
        key (str): Name of the info file (without extension)
        attribute (str): Name of the attribute to store
        value: Value to store
    """
    file_path = INFO_BASE / f"{key}.json"

    # Load existing data
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    # Update attribute
    data[attribute] = value

    # Save back
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_info(key, attribute=None):
    """
    Retrieves info from a key's info file.
    
    Parameters:
        key (str): Name of the info file (without extension)
        attribute (str or None): Specific attribute to get. If None, returns all.
    """
    file_path = INFO_BASE / f"{key}.json"

    if not file_path.exists():
        return None if attribute else {}

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if attribute:
        return data.get(attribute)
    return data

def remove_info(key, attribute):
    """
    Removes an attribute from a key's info file.

    Parameters:
        key (str): Name of the info file (without extension)
        attribute (str): Name of the attribute to remove
    """
    file_path = INFO_BASE / f"{key}.json"

    if not file_path.exists():
        return  # Nothing to remove

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if attribute in data:
        del data[attribute]

        # Save updated file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
def remove_key(key):
    """
    Deletes the entire info file for a key.

    Parameters:
        key (str): Name of the info file (without extension)

    Returns:
        bool: True if file was deleted, False if file did not exist
    """
    file_path = INFO_BASE / f"{key}.json"
    if file_path.exists():
        file_path.unlink()  # Delete the file
        return True
    return False


# === combat tracker ===
class CombatTracker:
    def __init__(self, encounter_name):
        self.encounter_name = encounter_name
        self.participants = []  # list of dicts: {"name": ..., "initiative": ..., "hp": ..., "status": ...}
        self.turn_index = 0
        write_log(encounter_name, f"=== {encounter_name} ===")

    def add_participant(self, name, initiative, hp=None, status=None):
        """Add a participant to the combat."""
        self.participants.append({
            "name": name,
            "initiative": initiative,
            "hp": hp,
            "status": status or []
        })
        # Keep sorted by initiative (highest first)
        self.participants.sort(key=lambda x: x["initiative"], reverse=True)

    def next_turn(self):
        log_key=self.encounter_name
        """Move to the next participant, ask for their action, and log it."""
        if not self.participants:
            return None

        participant = self.participants[self.turn_index]
        self.turn_index = (self.turn_index + 1) % len(self.participants)

        # Ask for action
        action = input(f"Action for {participant['name']} (HP: {participant['hp']}): ")
        write_log(log_key, f"{participant['name']} -> {action}")

        return participant

        participant = self.participants[self.turn_index]
        self.turn_index = (self.turn_index + 1) % len(self.participants)
        return participant

    def remove_participant(self, name):
        """Remove a participant from combat."""
        self.participants = [p for p in self.participants if p["name"] != name]
        self.turn_index = self.turn_index % len(self.participants)

    def update_hp(self, name, new_hp):
        """Update a participant's HP."""
        for p in self.participants:
            if p["name"] == name:
                p["hp"] = new_hp
                break

    def add_status(self, name, status):
        """Add a status effect to a participant."""
        for p in self.participants:
            if p["name"] == name:
                if status not in p["status"]:
                    p["status"].append(status)
                break

    def remove_status(self, name, status):
        """Remove a status effect from a participant."""
        for p in self.participants:
            if p["name"] == name:
                if status in p["status"]:
                    p["status"].remove(status)
                break

    def current_order(self):
        """Return the current initiative order with status."""
        return [
            f"{p['initiative']:>3} | {p['name']} | HP: {p['hp']} | Status: {', '.join(p['status'])}"
            for p in self.participants
        ]
    
    def log_order(self):
        lines = self.current_order()
        for line in lines:
            write_log(self.encounter_name, line)
        print("\n".join(self.current_order()))
        
    def log_end(self):
        print(f"=== {self.encounter_name} ended ===")
        write_log(self.encounter_name, "=== encounter ended ===")
        
    
