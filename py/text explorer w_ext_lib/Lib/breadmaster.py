# Welcome, game designer!
# "Bread Master" shows, by example, how to use this library to make your own game.

from runner import *

intro = """
,-----.                          ,--.           
|  |) /_,--.--. ,---.  ,--,--. ,-|  |           
|  .-.  \  .--'| .-. :' ,-.  |' .-. |           
|  '--' /  |   \   --.\ '-'  |\ `-' |           
`------'`--'    `----' `--`--' `---'            
,--.   ,--.                ,--.                 
|   `.'   | ,--,--. ,---.,-'  '-. ,---. ,--.--. 
|  |'.'|  |' ,-.  |(  .-''-.  .-'| .-. :|  .--' 
|  |   |  |\ '-'  |.-'  `) |  |  \   --.|  |    
`--'   `--' `--`--'`----'  `--'   `----'`--'

You are Shenandoah Yeasty, apprentice baker -- and your stomach is grumbling."""

def activate_breadulator(runner):
    """Custom 'activate' Command for the breadulator.
    This function mutates :runner: attributes!"""
    if "rye" in runner.inventory:
        print("The breadulator hums strangely. A beam of blue light engulfs your rye, and transforms it into bread.")
        runner.inventory.remove("rye")
        runner.inventory.append("bread")
        runner.flags["activated_breadulator"] = True
    else:
        raise CantActivateError("The breadulator cannot be activated if you lack the proper ingredients.")

def activate_hat(runner):
    """Custom 'activate' Command for the chef's hat.
    This function mutates :runner: attributes!"""
    if runner.flags.get("has_puppeted", False):
        raise CantActivateError("You've had quite enough of hat puppetry.")
    else:
        print("You amuse yourself by using the hat like a hand puppet, but quickly tire of this game.")
        runner.flags["has_puppeted"] = True

items = [Item("breadulator",
              "A squat steel device. How could you make bread without it?",
              ["activate"],
              activate_fn=activate_breadulator,
              synonyms=["device"]),
         Item("rye",
              "A superior bread ingredient.",
              ["take"]),
         Item("hat",
              "White and towering chef's hat.",
              ["take", "activate"],
              activate_fn=activate_hat,
              synonyms=["cap"]),
         Item("bread",
              "Delicious.",
              ["take"])]

rooms = [Room("kitchen",
              "This is where dreams are made.",
              {Direction.NORTH : "field"},
              ["breadulator"]),
         Room("field",
              "It's a blustery day. The rye wobbles in the wind.",
              {Direction.SOUTH : "kitchen"},
              ["rye"])]

def win_condition(runner):
    "Decides whether or not player has become the Bread Master."
    return runner.flags.get("activated_breadulator", False)
    
def main():
    gr = GameRunner(intro=intro,
                    rooms=rooms,
                    items=items,
                    current_room="kitchen",
                    win_condition=win_condition,
                    win_message="You win!\nYou are the true bread master now...\n",
                    inventory=["hat"])
    
    gr.begin_game()

if __name__ == "__main__":
    main()
