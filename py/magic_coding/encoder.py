from enum import Enum
import json
import os

'''
custom gliph combo creator

'''

# GLOBAL INDEXES
GlyphCategory = [
    "essence",
    "form",
    "modifier",
    "control",
    ]

CATEGORY_FILES = {
    GlyphCategory[0]: "glyphs/essence.txt",
    GlyphCategory[1]: "glyphs/form.txt",
    GlyphCategory[2]: "glyphs/modifier.txt",
    GlyphCategory[3]: "glyphs/control.txt",
}



class GlyphDefinition: # define rules for a given glyph
    def __init__(
        self,
        name: str,
        category: str,
        input_count: int = 0,
        input_categories: list = [],
        custom_validator=None
    ):
        self.name = name                           # "Fire", "Ball", "fast"
        self.category = category                   # essence, form, modifier, control, etc
        self.input_count = input_count             # 2 or (1,3)
        self.input_categories = input_categories
        self.custom_validator = custom_validator
    
    def to_text_block(self): # convert definition into formatted text
        lines = [f"[{self.name}]"]
        lines.append(f"inputs = {self.input_count}")
        if self.input_categories:
            cats = ",".join(c for c in self.input_categories)
            lines.append(f"input_categories = {cats}")
        lines.append(f"output = {self.category}")
        return "\n".join(lines)
    
# writes definition to txt
def write_definition(definition: GlyphDefinition):
    path = CATEGORY_FILES[definition.category]

    # ensure file exists
    open(path, "a").close()

    with open(path, "r", encoding="utf8") as f:
        content = f.read()

    if f"[{definition.name}]" in content:
        return  # already defined

    with open(path, "a", encoding="utf8") as f:
        f.write("\n\n" + definition.to_text_block())
        
    
class GlyphRegistry: # rules dict
    def __init__(self):
        self._defs = {}
        self.load_all()

    def register(self, definition: GlyphDefinition): #add definition 
        self._defs[definition.name] = definition

    def get(self, name): #get definition
        return self._defs[name]
    
    def load_all(self): #load all definition from files
        for category, path in CATEGORY_FILES.items():
            try:
                with open(path, "r", encoding="utf8") as f:
                    content = f.read()
            except FileNotFoundError:
                continue

            blocks = content.split("\n\n")
            for block in blocks:
                block = block.strip()
                if not block.startswith("["):
                    continue
                definition = parse_block(block, category)
                self.register(definition)
    
    
def parse_block(block: str, category): # text block to definition
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    name = lines[0][1:-1]

    data = {}
    for line in lines[1:]:
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()

    input_count = int(data["inputs"])

    input_categories_raw = data.get("input_categories", "").strip()
    if input_categories_raw.lower() == "none" or input_categories_raw == "":
        input_categories = None
    else:
        cats = []
        for c in input_categories_raw.split(","):
            c = c.strip()
            if c.startswith("GlyphCategory."):
                c = c.split(".")[1]
            cats.append(GlyphCategory[GlyphCategory.index(c.lower())])
        input_categories = cats

    return GlyphDefinition(
        name=name,
        category=category,
        input_count=input_count,
        input_categories=input_categories,
    )


class GlyphNode: # node of a spell
    def __init__(self, name, inputs=None, meta=None):
        self.name = name
        self.inputs = inputs or []
        self.meta = meta or {}
        

# test functions
def testReg():
    registry = GlyphRegistry()

    print("Loaded glyphs:")
    for name, definition in registry._defs.items():
        print(
            name,
            definition.category,
            definition.input_count,
            definition.input_categories,
        )
    
    
def testWrite():
    fire = GlyphDefinition(
    name="TestFire",
    category=GlyphCategory[0],
    input_count=0,
    input_categories=None,
    )

    write_definition(fire)

    registry = GlyphRegistry()
    print("TestFire" in registry._defs)


def testTree():
    spell = GlyphNode(
        "Shoot",
        inputs=[
            GlyphNode(
                "Ball",
                inputs=[
                    GlyphNode("Fire")
                ]
            )
        ]
    )

    print(spell.name)
    print(spell.inputs[0].name)
    print(spell.inputs[0].inputs[0].name)

def testRecursion():
    inner = GlyphNode("ball", [GlyphNode("fire")])
    outer = GlyphNode("shoot", [inner])
    spell = outer
    print(spell.name)
    print(spell.inputs[0].name)
    print(spell.inputs[0].inputs[0].name)
    
def test_all():
    print("\n-registry test:")
    testReg()
    
    print("\n-tree test:")
    testTree()
    
    print("\n-write test:")
    testWrite()
    
    print("\n-recursion test:")
    testRecursion()

# helper

def print_aviable_glpyh(registry, categories = None): #prints avaible glyphs
    printMatrix = [[] for i in GlyphCategory]
    for g in registry._defs.keys():
        idx = GlyphCategory.index(registry.get(g).category)
        printMatrix[idx].append(g)
    
    print("\nAvailable glyphs:")
    for c in GlyphCategory:
        if (not categories or c in categories) and printMatrix[GlyphCategory.index(c.lower())] != []:
            print(f"\n-{c.upper()}")
            for g in printMatrix[GlyphCategory.index(c.lower())]:
                print(f"    -{g}")
    

def user_glyph():
    # Ask for basic info
    name = input("Enter glyph name: ").strip()

    # Category
    print("\nChoose category from:", [c for c in GlyphCategory])
    while True:
        cat_input = input("Enter category: ").strip().lower()
        if cat_input in GlyphCategory:
            category = cat_input
            break
        else:
            print("Invalid category. Try again.")

    # Input count
    while True:
        try:
            input_count = int(input("\nEnter number of inputs (0 for none): ").strip())
            if input_count >= 0:
                break
            else:
                print("Input count cannot be negative.")
        except ValueError:
            print("Please enter an integer.")

    # Input categories
    if input_count > 0:
        print("\nEnter input categories separated by commas, or 'None' if no restriction")
        print("Available categories:", [c for c in GlyphCategory])
        inp_cats_raw = input("Input categories: ").strip()
        if inp_cats_raw.lower() == "none" or inp_cats_raw == "":
            input_categories = None
        else:
            input_categories = []
            for c in inp_cats_raw.split(","):
                c = c.strip().lower()
                if c in GlyphCategory:
                    input_categories.append(c)
                else:
                    print(f"Invalid category {c}, skipping")
            if len(input_categories) == 0:
                input_categories = None
    else:
        input_categories = None


    # Build GlyphDefinition
    definition = GlyphDefinition(
        name=name,
        category=category,
        input_count=input_count,
        input_categories=input_categories,
    )

    # Write to file
    write_definition(definition)
    print(f"\nGlyph '{name}' written to file under category {category}")
    

# visualize text
def print_spell(node, indent=0):
    """Prints the spell tree in a human-readable format."""
    prefix = "  " * indent
    print(f"{prefix}- {node.name}")
    if node.inputs:
        for child in node.inputs:
            print_spell(child, indent + 1)
            

#spell builder
def spell_builder(registry, glyph_name=None, categories = None):
    """
    Recursively build a GlyphNode from user input.

    Args:
        registry: GlyphRegistry instance (for available glyphs)
        glyph_name: If given, start with this glyph, else ask user
    Returns:
        GlyphNode object representing the spell tree
    """

    # Step 1: Choose glyph
    if glyph_name is None:
        print_aviable_glpyh(registry, categories)
        while True:
            glyph_name_input = input("Enter glyph name for this node: ").strip()
            if glyph_name_input in registry._defs:
                glyph_name = glyph_name_input
                break
            else:
                print("Invalid glyph name, try again.")

    # Get the definition
    definition = registry._defs[glyph_name]

    # Step 2: Build inputs recursively
    inputs = []
    if definition.input_count > 0:
        print(f"Glyph '{glyph_name}' requires {definition.input_count} inputs.")
        for i in range(definition.input_count):
            # Show allowed categories if defined
            allowed = (
                [c for c in definition.input_categories]
                if definition.input_categories else None
            )
            if allowed:
                print(f"Input {i+1} must be one of: {allowed}")
                
            child_node = spell_builder(registry, categories=allowed)
            while(allowed != None and registry.get(child_node.name).category not in allowed): #type validation
                print("invalid glyph type, retry")
                child_node = spell_builder(registry, categories=allowed)
            inputs.append(child_node)

    # Step 3: Create GlyphNode
    node = GlyphNode(name=glyph_name, inputs=inputs)
    return node


SPELLS_FOLDER = "spells"

# Ensure spells folder exists
os.makedirs(SPELLS_FOLDER, exist_ok=True)

# --- Save spell to file ---
def save_spell(spell: GlyphNode, filename: str):
    """
    Save a GlyphNode (spell tree) to a JSON file.
    """
    def node_to_dict(node: GlyphNode):
        return {
            "name": node.name,
            "inputs": [node_to_dict(child) for child in node.inputs]
        }

    filepath = os.path.join(SPELLS_FOLDER, filename)
    if not filepath.lower().endswith(".json"):
        filepath += ".json"
    
    with open(filepath, "w", encoding="utf8") as f:
        json.dump(node_to_dict(spell), f, indent=2)
    
    print(f"Spell saved to {filepath}")


# --- Load spell from file ---
def load_spell(filename: str) -> GlyphNode:
    """
    Load a GlyphNode (spell tree) from a JSON file.
    """
    def dict_to_node(d):
        return GlyphNode(
            name=d["name"],
            inputs=[dict_to_node(child) for child in d.get("inputs", [])]
        )

    filepath = os.path.join(SPELLS_FOLDER, filename)
    if not filepath.lower().endswith(".json"):
        filepath += ".json"

    with open(filepath, "r", encoding="utf8") as f:
        data = json.load(f)
    
    return dict_to_node(data)