'''
classes and functions to generate and handle room level interactions

'''

from item_gen import generate_loot

def generate_room(position, G_modifiers = None, rating = 0):
    
    Type = "room.type" # room type algorithm (none)
    name = "" # room name generator
    
    return Room(Type, position, name, G_modifiers if G_modifiers is not None else [], rating)


class Room():
    '''
    describes every aspect of the room
    attributes:
    - name (room specific name)
    - room_type (genaral name)
    - position
    - loot[] (loot class)
    - modifiers[]
    - paths[] (north, south, west, east)
    - tags[]
    '''
    def __init__(self, room_type, position, name = None, modifiers = None, G_rating = 0, paths = None, tags = None):
        
        self.room_type = room_type
        self.position = position
        self.name = name if name is not None else f"name.{room_type} {position}"
        self.modifiers = modifiers if modifiers is not None else []
        self.G_rating = G_rating
        self.paths = paths if paths is not None else ["north", "south", "west", "east"]
        self.tags = tags if tags is not None else []
        
        # loot generator
        # num of lootables = rating
        self.loot = [generate_loot("loot.type", G_rating)] * self.G_rating