"""
dice.py

Utility functions for creating and working with Yahtzee dice rolls.

Every roll is stored in a canonical form:
reduces the number of unique states the engine must
consider later.
"""

from typing import Iterable, Tuple
import random

from constants import DICE_PER_ROLL, DICE_SIDES

Roll = Tuple[int, int, int, int, int]


def random_roll() -> Roll:
    """
    Generate a random Yahtzee roll.
    """

    return make_roll(
        random.randint(1, DICE_SIDES)
        for _ in range(DICE_PER_ROLL)
    )

def validate_roll(dice: Iterable[int]) -> Roll:
    """
    Validate a roll and return it as a tuple.

    Raises
    ------
    ValueError
        If the roll is invalid.
    """

    values = tuple(dice)

    if len(values) != DICE_PER_ROLL:
        raise ValueError(
            f"A roll must contain exactly {DICE_PER_ROLL} dice."
        )

    for die in values:
        if not 1 <= die <= DICE_SIDES:
            raise ValueError(
                f"Invalid die value: {die}"
            )

    return values


def make_roll(dice: Iterable[int]) -> Roll:
    """
    Create the canonical representation of a roll.

    The returned roll is

        - validated
        - sorted
        - immutable
    """

    return tuple(sorted(validate_roll(dice)))  # type: ignore


def roll_total(roll: Roll) -> int:
    """
    Return the total value of the roll.
    """

    return sum(roll)


def count_faces(roll: Roll) -> Tuple[int, int, int, int, int, int, int]:
    """
    Count how many times each face appears.

    Index 0 is intentionally unused.

    """

    counts = [0] * (DICE_SIDES + 1)

    for die in roll:
        counts[die] += 1

    return tuple(counts)


def face_mask(roll: Roll) -> int:
    """
    Return a bit mask representing which faces appear.
    
    """

    mask = 0

    for die in roll:
        mask |= 1 << die

    return mask