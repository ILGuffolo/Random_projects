class Command:
    """An action the player can take in the game world.

    This class wraps a string to represent the parsed version of a player's command.
GameRunner itself is responsible for:
1. determining whether a command is valid, and
2. carrying out a valid command."""

    def __init__(self, name):
        self.name = name

# key: what the player enters
# val: the object representing a Command
# a general solution for two-word command synonyms was out of scope,
# but special cases for common two-word synonyms are implemented.
# see GameRunner.main_loop
COMMANDS = {"look" : Command("look"),
            "take" : Command("take"),
            "activate" : Command("activate"),
            "inventory" : Command("inventory"),
            "go" : Command("go"),
            "help" : Command("help"),
            "open" : Command("open")
}

# synonyms which the player can use to name each command
SYNONYMS = {"t" : "take",
            "get" : "take",
            "grab" : "take",
            "nab" : "take",
            "carry" : "take",

            "a" : "activate",
            "engage" : "activate",
            "switch" : "activate",
            "use" : "activate",

            "l" : "look",
            "x" : "look",
            "examine" : "look",

            "h" : "help",
            "?" : "help",
            "actions" : "help",

            "move" : "go",

            "i" : "inventory",
            "inv" : "inventory",
            "invent" : "inventory",
            "items" : "inventory",
            "holding" : "inventory",
            
            "o" : "open",
            "loot" : "open",
}

def synonyms_for(command_name):
    "Return all the synonyms for a command."
    return [k for k,v in SYNONYMS.items() if v == command_name]
