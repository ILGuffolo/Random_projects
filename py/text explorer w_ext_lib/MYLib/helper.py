

def debug(srt):
    with open("debug.txt", "a") as f:
        f.write(text + "\n")
        
def debug_reset():
    with open("debug.txt", "w") as f:
        f.write("")
        
        
action_list = {#--- Action List ---#
        "look": ["look", "l", "inspect", "examine"],
        "take": ["take", "t", "grab", "pick", "pick up"],
        "explore" : ["explore", "e"],
        "use" : ["use", "u"]
        "move" : ["move", "m"]
    }

def get_action(word):
    for act, syns in action_list.items():
        if word in syns:
            return act
    return None

def do_((action, target), GameRunner):
    actlist = list(action_list)
    
    if action in target.allowed_actions:
        match action:
            case actlist[0]:#look
                print(f"\n---\n{target.name.upper()}\n{target.description}\n---\n")

            case actlist[1]:#take
                if target.name in list(GameRunner.inventory):
                    GameRunner.inventory[target.name] +=1
                else:
                    GameRunner.inventory.update({target.name: 1})

            case actlist[2]:#explore
                if target.explorable:
                    GameRunner.current_room.content.extend(target.explorable)

            case actlist[3]:#use
                target.use()
                if target.is_consumable:
                    GameRunner.inventory[target.name] -= 1
                    if GameRunner.inventory[target.name] <= 0:
                        GameRunner.inventory.pop(target.name)
            
            case actlist[4]:#move
                match target.name:
                    case "north":
                        if GameRunner.current_room.exit("north"):
                            GameRunner.current_room = GameRunner.current_room.exit("north")
                            GameRunner.position[1] += +1
                        else:
                            print("cannot move there")
                            
                    case "west":
                        if GameRunner.current_room.exit("north"):
                            GameRunner.current_room = GameRunner.current_room.exit("west")
                            GameRunner.position[0] += -1
                        else:
                            print("cannot move there")
                            
                    case "south":
                        if GameRunner.current_room.exit("north"):
                            GameRunner.current_room = GameRunner.current_room.exit("south")
                            GameRunner.position[1] += -1
                        else:
                            print("cannot move there")
                            
                    case "east":
                        if GameRunner.current_room.exit("north"):
                            GameRunner.current_room = GameRunner.current_room.exit("east")
                            GameRunner.position[0] += +1
                        else:
                            print("cannot move there")

            # --------------------------------------------
            # Default unreachable case unless you forgot to code something:
            case _:
                print("\n------\nACTION ERROR\nend of list\nYou can encounter this error only if you forgot to code the action!!\n------\n")
        else:
            print(f"\nThis action cannot be performed on {target.name}\n")


