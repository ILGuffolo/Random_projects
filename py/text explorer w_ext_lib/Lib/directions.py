from enum import Enum

class Direction(Enum):
    "The geographic relation between two Rooms."
    # in a full-fledged game development tool, these might be user-extensible, which would probably require abandoning single-letter shortcodes
    NORTH = "n"
    N = "n"
    SOUTH = "s"
    S = "s"
    WEST = "w"
    W = "w"
    EAST = "e"
    E = "e"
