import logging
from directions import *
from items import *
from commands import *
from helpers import *
from errors import *

logging.basicConfig()
logger = logging.getLogger("GameLogger")
# to be turned back on during development
# I treat DEBUG logging like "print-statement debugging 2.0"
# can turn off and on without having to go around commenting them in/out
# logger.setLevel("DEBUG")
logger.setLevel(0)

class GameRunner:
    """Maintains game state and calls the main game loop."""

    def __init__(self, intro, rooms, items, current_room, win_condition, win_message, inventory=None, flags=None):
        """:intro: str. Text printed once, at beginning of game.

        :rooms: set or list of Rooms which player can explore.
        Room.name must be unique across all Rooms.

        :items: set or list of Items which player can interact with.
        Item.name must be unique across all Items.

        :current_room: str. Name of Room where player starts game.
        Updated as player explores the world with "go" Command.

        :win_condition: function accepting one argument, the GameRunner instance itself.
        Returns True if game's win conditions are satisfied; otherwise False.

        :win_message: str. Text printed when player wins game.

        :inventory: list of strings which are Item.names.
        Player starts game with these items on their person.
        Updated as player acquires Items with "take" Command.

        :flags: dictionary with string keys. Value types may vary.
        Used to maintain any state not stored in other GameRunner attributes.
        Game designers using this library can store data here, especially as result of "activate" Commands.
        The designer's :win_condition: function will typically access :flags: data to decide whether player has won.
"""
        self.intro = intro
        self.rooms = {r.name:r for r in rooms}
        self.items = {i.name:i for i in items}
        self.current_room = self.rooms[current_room]
        self.win_condition = win_condition
        self.win_message = win_message
        if not inventory:
            self.inventory = []
        else:
            self.inventory = inventory
        if not flags:
            self.flags = {}
        else:
            self.flags = flags
        self.help_prompt = "If you don't know what to do, type 'help' (no quotes)."
        # map from Items' synonyms to their names
        self.item_synonyms = {}
        for i in self.items.values():
            for s in i.synonyms:
                logger.debug("Adding synonym %s for item named %s", s, i.name)
                self.item_synonyms[s] = i.name
        # map from Rooms' synonyms to their names
        self.room_synonyms = {}
        for r in self.rooms.values():
            for s in r.synonyms:
                logger.debug("Adding synonym %s for room named %s", s, r.name)
                self.room_synonyms[s] = r.name

    def parse_target(self, tokens):
        "Remove any :tokens: elements which are not meaningful for target validation. THIS FUNCTION ALTERS ITS ARGUMENT."
        # ignore certain words before the target
        while tokens[0] in set(["the", "teh", "a", "an", "at"]):
            article = tokens.pop(0)
            logger.debug("Removing article %s from tokens", article)
        return tokens[0]

    def begin_game(self):
        """Prints introductory information and enters the game loop."""
        print(self.intro, "\n")
        print(self.current_room.name.capitalize())
        self.current_room.describe()
        self.game_loop()

    def game_loop(self):
        """Repeatedly queries for, validates, and executes or rejects the commands entered by player.

:raises: GameError if command.name hits the last branch (for explicit failure in case more Commands are added in future, but I/the designer forget to handle them in this function.)"""
        if not self.flags:
            self.flags = {"moved" : False}
        while True:
            # CHECK WORLD STATE
            # win?
            if self.win_condition(self):
                print(self.win_message)
                exit()

            # moved last turn?
            if self.flags["moved"]:
                self.flags["moved"] = False
                print(self.current_room.name.capitalize())
                self.current_room.describe()

            # have remaining multi-command input to process?
            if self.flags.get("multi", False):
                player_input = self.flags["multi"].pop(0)
                # note: flags["multi"] may now be empty
                logger.debug("Using multi-command input item %s", player_input)
                # printed line visually separates output of this command from that of previous one
                # normally that separation is accomplished when command prompt is printed,
                # but no command prompt printed between multi-commands
                print()
            else:
                # READ INPUT
                player_input = input(">")

            logger.debug("Received input %s", player_input)

            # handle "out of world" command
            if player_input == "quit":
                exit()

            # handle empty input and prompt for help
            if not player_input:
                print("Please enter a command. " + self.help_prompt)
                continue

            # preprocess input
            player_input = player_input.strip().lower()
            # if multiple commands are indicated, split them up and store extras
            if "." in player_input:
                multiple_command_input = player_input.split(".")
                logger.debug("Received multiple commands %s", multiple_command_input)
                # common player habit to include "." on last command in list, which leaves an empty string in this list
                # so, filter to remove empty string if present
                multiple_command_input = list(filter(len, multiple_command_input))
                player_input = multiple_command_input.pop(0)
                if self.flags.get("multi", False):
                    # list already there: append to it
                    # should be empty list since a "." would only be in player input if they enter multiple commands at once, which means the value of player_input was entered by the player this turn and wasn't popped from flags["multi"] whch means flags["multi"] is empty list
                    self.flags["multi"].append(multiple_command_input)
                else:
                    self.flags["multi"] = multiple_command_input

            # tokenize input
            tokens = player_input.split(" ")

            # PRE-PARSING
            # alter tokens to allow special-case two-word command synonyms (a bit repetitive, but not hacky IMO)
            if len(tokens) >= 2:
                if tokens[0] in ("switch", "turn") and tokens[1] == "on":
                    logger.debug("Special two-word command: replacing %s and %s", tokens[0], tokens[1])
                    tokens = tokens[2:]
                    tokens.insert(0, "activate")
                elif tokens[0] == "pick" and tokens[1] == "up":
                    logger.debug("Special two-word command: replacing %s and %s", tokens[0], tokens[1])
                    tokens = tokens[2:]
                    tokens.insert(0, "take")

            # alter tokens to allow use of Direction names/abbreviations as equivalent to "go [that direction]"
            if tokens[0] in [str.lower(m) for m in list(Direction.__members__)]:
                logger.debug("Directional abbreviation: inserting 'go' before %s", tokens[0])
                tokens.insert(0, "go")

            # VALIDATION
            # validate command
            maybe_command = tokens.pop(0)
            # canonicalize synonyms
            maybe_command = SYNONYMS.get(maybe_command, maybe_command)
            try:
                command = COMMANDS[maybe_command]
                logger.debug("Valid command %s", command.name)
            except KeyError:
                print("I don't recognize that command. " + self.help_prompt)
                continue

            # HANDLING
            # commands are arrangd here roughly in order of complexity
            #inventory
            if command.name == "inventory":
                print("You have " + format_string_list(self.inventory) + ".")
            #help
            elif command.name == "help":
                print("Available commands (and their synonyms):")
                print("quit")
                for c in COMMANDS.keys():
                    syns = synonyms_for(c)
                    if not syns:
                        print(c)
                    else:
                        formatted_syns = "(" + ", ".join(syns) + ")"
                        print(c, formatted_syns)
            #look
            elif command.name == "look":
                if not tokens or tokens[0] == self.current_room.name:
                    # target not supplied
                    # interpret as looking at the room
                    print(self.current_room.name.capitalize())
                    self.current_room.describe()
                else:
                    # target supplied
                    target = self.parse_target(tokens)
                    # try canonicalizing name as both an Item and a Room
                    # I'd do these assignments closer to the if-else branches where they're used, but Python doesn't admit comments between branches
                    maybe_item = self.item_synonyms.get(target, target)
                    maybe_room = self.room_synonyms.get(target, target)
                    # special case for looking at self
                    if target in player_synonyms:
                        print("Such a handsome devil!")
                    elif maybe_item in (self.current_room.items + self.inventory):
                        # target is a visible item
                        self.items[maybe_item].describe()
                    elif maybe_room in [self.current_room.name, "surroundings", "environment", "environs", "around", "room", "here"]:
                        # target is the current room
                        print(self.current_room.name.capitalize())
                        self.current_room.describe()
                    else:
                        print("You can't see " + with_article(target) + " here.")
            #go
            elif command.name == "go":
                if len(tokens) == 0:
                    print("Which direction? Choose one:" + self.current_room.announce_exits())
                    maybe_dir = input(">")
                else:
                    maybe_dir = tokens.pop()
                # validate whether it's a dir at all
                try:
                    # use upper() so e.g. "n" becomes "N", an alias for "NORTH"
                    dir = Direction[maybe_dir.upper()]
                    logger.debug("Valid direction %s", dir)
                except:
                    print("I don't recognize that direction.")
                    continue
                # can you go that way from this room?
                try:
                    destination = self.current_room.exits[dir]
                    logger.debug("Can go %s from %s", dir, self.current_room.name)
                except KeyError:
                    print("You can't go {} from here.".format(dir.name.lower()))
                    continue
                # all checks passed, carry out logic
                # move player to new room
                self.current_room = self.rooms[destination]
                # describe new room on next turn
                self.flags["moved"] = True
            #take
            elif command.name == "take":
                if len(tokens) == 0:
                    if len(self.current_room.items) == 0:
                        print("There's nothing to take here.")
                        continue
                    else:
                        # target not supplied
                        print("Which thing? Choose one: " + ", ".join(self.current_room.items))
                        maybe_target = input(">")
                else:
                    # target supplied
                    maybe_target = self.parse_target(tokens)

                # canonicalize name
                maybe_target = self.item_synonyms.get(maybe_target, maybe_target)

                if maybe_target in player_synonyms:
                    print("You can hardly take yourself!")
                    continue

                # does player already have that?
                # warning: if you relax the condition that Items have unique names, this code won't work
                if maybe_target in self.inventory:
                    print("You already have that.")
                    continue
                
                # is there such a target here?
                try:
                    idx = self.current_room.items.index(maybe_target)
                    target = self.current_room.items[idx]
                    logger.debug("Valid item %s", target)
                except ValueError:
                    print("You can't see {} here.".format(with_article(maybe_target)))
                    continue
                # is target takeable?
                if self.items[target].allows("take"):
                    # all checks passed, carry out logic
                    self.inventory.append(target)
                    self.current_room.items.remove(target)
                    print("You take the {}.".format(target))
                else:
                    print("You can't pick up the {}.".format(target))
                    continue
            #activate
            elif command.name == "activate":
                # I'd use list.extend, but it returns None
                possible_targets = self.current_room.items + self.inventory
                if len(tokens) == 0:
                    if len(possible_targets) == 0:
                        print("There's nothing to activate here.")
                        continue
                    else:
                        # target not supplied
                        print("Which thing? Choose one: " + ", ".join(self.current_room.items))
                        maybe_target = input(">")
                else:
                    # target supplied
                    maybe_target = self.parse_target(tokens)

                # canonicalize name
                maybe_target = self.item_synonyms.get(maybe_target, maybe_target)
                if maybe_target in player_synonyms:
                    print("You're already plenty active.")
                    continue

                # is there such a target here?
                try:
                    idx = possible_targets.index(maybe_target)
                    target = possible_targets[idx]
                    logger.debug("Valid item %s", target)
                except ValueError:
                    print("You can't see {} here.".format(with_article(maybe_target)))
                    continue

                # is target activatable?
                if self.items[target].allows("activate"):
                    # all checks passed, carry out logic
                    try:
                        self.items[target].activate(self)
                    except CantActivateError as e:
                        # it is currently impossible to activate this thing, but that might change
                        report = "You are not currently able to activate the {}.".format(target)
                        if e.message:
                             report += " "
                             report += e.message
                        print(report)
                else:
                    # it is totally impossible to activate this thing
                    print("It's not possible to activate the {}.".format(target))
                    continue
            #open
            elif command.name == "open":
                #reveals items inside it ("spilling" them in the room)
                if !target.inventory
                
            else:
                # Instead of writing "elif command.name == 'activate'" above, I could have just written "else". But then the if-else cascade on command names would implicitly shunt ANY future command into that final branch, even if it's not supposed to go there. Such are the results of being implicit instead of explicit.
                # I chose instead to raise an error here, so that Future You or Future Me would instantly say 'Aha! I forgot my if-else'.
                raise GameError("You should only hit this error if you implement a custom Command and forget to account for it inside GameRunner.game_loop.")
