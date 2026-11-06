"""

Shared constants and enums used throughout the Yahtzee engine.

"""

from enum import IntEnum

# ==========================
# Game Rules
# ==========================

DICE_PER_ROLL: int = 5
DICE_SIDES: int = 6

UPPER_BONUS_THRESHOLD: int = 63
UPPER_BONUS_SCORE: int = 35

FULL_HOUSE_SCORE: int = 25
SMALL_STRAIGHT_SCORE: int = 30
LARGE_STRAIGHT_SCORE: int = 40
YAHTZEE_SCORE: int = 50


# ==========================
# Score Categories
# ==========================

class Category(IntEnum):
    """
    Every scoring category in Yahtzee.

    The integer values are intentionally fixed. (to modify later)


    """

    ONES = 0
    TWOS = 1
    THREES = 2
    FOURS = 3
    FIVES = 4
    SIXES = 5

    THREE_KIND = 6
    FOUR_KIND = 7
    FULL_HOUSE = 8
    SMALL_STRAIGHT = 9
    LARGE_STRAIGHT = 10
    YAHTZEE = 11
    CHANCE = 12