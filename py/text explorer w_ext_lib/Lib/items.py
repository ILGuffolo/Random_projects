from helpers import format_string_list

class Item:
    "An entity in the game world which can be targeted by Commands."
    # Subclassing Item is done even for things you might not think of as 'in-game entities', such as Rooms.
    # Apart from Room, here's another example of how to usefully subclass Item: you could borrow from Inform 7 and implement a 'Scenery' subclass for background Items like "the sky." Instances of Scenery can never be picked up and are not listed when a room is described [in this system, such restrictions would most likely be implemented within the Scenery constructor.]
    # Scenery are good for the player because they provide a response when s/he types "look sky" or "look sun" in a Room with description "The sun shines in the sky" even though we don't want those to be ordinary interactable items, just background flavor. They are also good for the end user programming a game with this library, because they can rely on the class system to avoid accidentally e.g. making the sun pick-up-able with Item("sun", "Big and hot.", ["take"]) by instead writing Scenery("sun", "Big and hot.").

    def __init__(self, name, desc, allowed_commands=None, activate_fn=None, synonyms=None):
        if name == "":
            raise ValueError("Item.name cannot be empty string")
        else:
            self.name = name
        if desc == "":
            raise ValueError("Item.desc cannot be empty string")
        else:
            self.desc = desc
        if not allowed_commands:
            # minimal command set: look is always allowed
            self.allowed_commands = set("look")
        elif "look" not in allowed_commands:
            # add look so the library user doesn't have to remember
            self.allowed_commands = set(allowed_commands).union(set(["look"]))
        else:
            self.allowed_commands = allowed_commands
        if activate_fn:
             if not self.allows("activate"):
                 raise ValueError("Item must allow the 'activate' Command to override the activate() method")
             else:
                 self.activate = activate_fn
        # no matching else - activate() method already has default implementation
        if not synonyms:
            self.synonyms = set()
        else:
            self.synonyms = set(synonyms)


    def describe(self):
        print(self.desc)

    def activate(self, runner):
        "Activate Item. The runner argument is required because activation can have side effects on the game world state."
        # by default, Items cannot be activated
        raise CantActivateError

    def allows(self, command):
        "Decides whether :command: can be used on this item."
        # although merely a wrapper around 'if command in allowed_commands', calling this function makes programmer intent self-documenting
        # 'if x in y' is a Python construct that is used all over; 'allows' is a library concept meaning exactly one thing
        # using allows also means you need only refactor one location if logic needs changing. Good luck search-and-replacing exactly and only the correct instances of 'for x in y' if that time comes!
        # finally, even though 'allows' exists, it would be inappropriate to make allowed_commands a private variable, i.e. _allowed_commands
        # game logic might legitimately require changing the commands to which an item responds, but designers would discouraged from doing so if they see Item.__init__ assigns to a private var
        # the only downside, as far as I can see, is that you have to be diligent about using this instead of 'if command in self.allowed_commands'
        if command in self.allowed_commands:
            return True
        else:
            return False


class Room(Item):
    """A location in the game world."""
    # Rooms are subclasses of Item so that implementation logic for Commands like "look" can apply to both Rooms and ordinary Items. In addition, since the "go" command internally targets a Direction (as seen in Room.exits), I've implemented the effect method "go" only on Rooms, not on all Items. [You are at your own risk if you implement it on something that's not a Room.]

    # In other game engines, Directions are sometimes implemented as commands so that Rooms respond to them just like Items normally respond to commands. I will not take such steps for this library. Instead, the player issuing 'n' or 'north' is just syntactic sugar for typing 'go north'; see GameRunner's code for command parsing."""

    def __init__(self, name, desc, exits, items=None):
        """Construct a new room."""
        if not exits:
            # exits should be of the form {Direction : room_name}
            # this error won't guard against ill-formed exits parameters, but it will at least prevent one obvious user error
            raise ValueError("Room.exits cannot be empty")
        else:
            self.exits = exits
        if not items:
            self.items = []
        else:
            self.items = items
        super().__init__(name, desc, ["go"])

    def describe(self):
        "Give the room's description, its exits, and items within it."
        begin = self.desc + self.announce_exits()
        if len(self.items) == 0:
            print(begin)
        else:
            print(begin + "\n\n" + self.announce_items())

    def announce_exits(self):
        "Give a listing of exits from this room."
        if not self.exits:
            return ""
        else:
            return " [exits: " + " ".join([q.value for q in self.exits.keys()]) + "]"

    def announce_items(self):
        "Give a listing of the items in this room."
        count = len(self.items)
        if count > 2:
            listing = "There are "
        else:
            listing = "There is "
        listing += format_string_list(self.items)
        listing += " here."
        return listing
