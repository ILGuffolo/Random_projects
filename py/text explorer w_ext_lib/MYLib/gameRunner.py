from helper import *
from objects import *

def parse_action(user_input, reachable_instances):
    """
    user_input: raw string
    get_action: helper function -> returns canonical action name or None
    reachable_instances: list of objects with .name
    """

    user_input = user_input.lower()
    
    #Action
    # split into words to check each individually
    # also check multi-word segments (e.g. "pick up")
    words = user_input.split()

    action_found = None
    # check single words
    for w in words:
        a = get_action(w)
        if a:
            action_found = a
            break

    # if still no action, check for multi-word phrases
    if not action_found:
        for i in range(len(words)-1):
            phrase = words[i] + " " + words[i+1]
            a = get_action(phrase)
            if a:
                action_found = a
                break

    if not action_found:
        return None, None  # no valid action found

    #Target
    target_found = None
    for inst in reachable_instances:
        # match by instance name string
        if inst.name.lower() in user_input:
            target_found = inst
            break
        
     if not target_found:
        target_found = reachable_instances[0]  #default target

    return action_found, target_found


#--- Game Runner ---#
# handles every aspect of a dungeon run
class GameRunner:
    def __init__(self, Player_info):
        class player:
            def __init__(self, Player_info):
                for k, v in Player_info.items():
                    setattr(player, k, v)
        
        self.player = player(Player_info)
        
        self.hp = 100
        self.inventory = {}
        self.posistion = []
        self.in_base = True
        self.current_room = None 
        
        
        
    
    def Dungeon_generator():
        
    
    def Start_game():
        
    
