

class Blueprint:
    def __init__(self, blueprint_name, blueprint_description, allowed_actions = [], required_for_object = [], required_for_instance_bp = [], **blueprint_data):
        self.blueprint_name = blueprint_name
        self.blueprint_description = blueprint_description
        self.allowed_actions = allowed_actions
        if "look" not in allowed_actions: self.allowed_actions.append("look")
        
        self.blueprint_data = blueprint_data
        
        self.required_for_object = set(required_for_object)
        self.required_for_instance_bp = set(required_for_instance_bp)

    def __call__(self, object_name, object_description, required_for_instance = [], **object_data):
        # instance-level init
        def instance_init(self, name, description, **instance_data):
            self.name = name
            self.description = description
            
            # check for manadatory custom arguments (instance level)
            missing2 = required_for_instance - instance_data.keys()
            if missing2:
                print(f"Missing instance properties: {missing2}")
            missing3 = required_for_instance_bp - instance_data.keys()
            if missing2:
                print(f"Missing instance properties: {missing3}")
            
            # copy object-level attributes (class attributes)
            for k, v in object_data.items():
                setattr(self, k, v)
            # copy instance-specific attributes 
            for k, v in instance_data.items():
                setattr(self, k, v)

        # attributes of the object class (mid-layer)
        attrs = {
            "required_for_instance" : set(required_for_instance),
            "required_for_instance_bp" : self.required_for_instance_bp,
            "object_description" : object_description,
            "allowed_actions": self.allowed_actions,
            "__init__": instance_init
        }

        # copy blueprint-level data into the object class
        for k, v in self.blueprint_data.items():
            attrs[k] = v
        
        # check for mandatory custom arguments (obj level)
        missing = self.required_for_object - object_data.keys()
        if missing:
            print(f"Missing object properties: {missing}")
        # add object-level attributes
        for k, v in object_data.items():
            attrs[k] = v

        # return the object class
        return type(object_name, (), attrs)


#--- Blueprints ---#
room = Blueprint("room", "part of a dungeon that contains loot",
                 ["explore"],
                 [], ["explorable", "content", "exits"],
                 hasWalls=True )

item = Blueprint("item", "an item you can collect",
                 ["take"],
                 ["rarity"])

tresure = Blueprint("tresure", "a pile of trasure with some loot",
                    ["explore"],
                    [], ["explorable"])


#--- Objects ---#
#rooms
common_room = room("common room", "a common room containing some basic loot")
tresure_room = room("tresure room", "a rare room containing some tresure inside")
#item
sword = item("sword", "a normal looking sword", ["attack damage"], rarity=2)
torch = item("torch", "an fiery stick to light up dark places", [], rarity=1)
#tresure
tresure_chest = tresure("chest", "a chest containing some quality loot")
garbage_pile = tresure("pile of junk", "a pile uf useless item but maybe there's something of value inside")

