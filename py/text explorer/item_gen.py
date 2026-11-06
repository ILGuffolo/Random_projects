'''
classes and functions to generate and handle item level interactions

'''

def generate_loot(type, weight):
    # loot generator
    return Loot(type, G_rating=weight)

class Loot():
    '''
    contains all info of the lootable object:
    - type
    - items[]
    '''
    def __init__(self, Type, modifiers = None, G_rating = 0):
        
        self.type = Type
        self.modifiers = modifiers if modifiers is not None else []
        
        # loot algorithm
        # random item * rating
        self.items = [generate_item(0)] * G_rating
        
def generate_item(weight):
    
    Type = "item.type" # item gen algorithm
    mods = []
    attr = {}
    
    return Item(Type, mods, attr)
    
class Item():
    '''
    info about the item:
    - name
    - desc
    - type
    - modifiers []
    - attr {} (dmg, atk speed, armor, ecc...)
    - tags[]
    '''
    
    def __init__(self, Type, modifiers = None, attr = None, tags = None, name = None, desc = None):
        
        self.type = Type
        self.name = name if name is not None else "item.name"
        self.desc = desc if desc is not None else "item.desc"
        self.modifiers = modifiers if modifiers is not None else []
        self.attributes = attr if attr is not None else {}
        self.tags = tags if tags is not None else []