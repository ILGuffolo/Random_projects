"""
Probability calculations for Yahtzee.

This module generates exact reroll outcomes.

No simulation is used.

Because Yahtzee has only five dice, exact enumeration is fast enough
and gives perfect probabilities.

A keep decision is represented by a 5-bit integer mask.
"""


from collections import Counter
from itertools import product
from typing import Iterator
from functools import lru_cache

from dice import Roll, make_roll
from constants import DICE_SIDES


KeepMask = int


def generate_keep_masks() -> Iterator[KeepMask]:
    """
    Generate all possible keep decisions.

    """

    for mask in range(32):
        yield mask


def dice_to_keep_mask(
    roll: Roll,
    kept_indices: list[int],
) -> KeepMask:
    """
    Convert dice positions into a keep mask.

    """

    mask = 0

    for index in kept_indices:
        mask |= 1 << index

    return mask


def kept_dice(
    roll: Roll,
    mask: KeepMask,
) -> tuple[int, ...]:
    """
    Extract kept dice from a roll.
    """

    result = []

    for index, die in enumerate(roll):
        if mask & (1 << index):
            result.append(die)

    return tuple(result)


def number_of_rerolls(
    mask: KeepMask,
) -> int:
    """
    Return how many dice need to be rolled again.

    Example:

        11100

        keeps 3 dice

        rerolls 2 dice
    """

    kept = 0

    for i in range(5):
        if mask & (1 << i):
            kept += 1

    return 5 - kept


def generate_reroll_outcomes(
    roll: Roll,
    mask: KeepMask,
) -> Iterator[Roll]:
    """
    Generate every possible final roll after rerolling.

    Results are canonical sorted rolls.

    Duplicate outcomes are intentionally allowed here.

    Later we collapse duplicates and count probabilities.
    """

    kept = kept_dice(roll, mask)

    rerolls = number_of_rerolls(mask)

    for new_dice in product(
        range(1, DICE_SIDES + 1),
        repeat=rerolls,
    ):
        yield make_roll(
            kept + new_dice
        )


def generate_unique_reroll_outcomes(
    roll: Roll,
    mask: KeepMask,
) -> dict[Roll, int]:
    """
    Generate unique outcomes and their frequencies.

    The values represent how many dice combinations
    produce that final roll.
    """

    outcomes = Counter(
        generate_reroll_outcomes(
            roll,
            mask,
        )
    )

    return dict(outcomes)

@lru_cache(maxsize=None)
def reroll_probability_distribution(
    roll: Roll,
    mask: KeepMask,
):
    """
    Return exact probabilities of all possible outcomes.

    Probabilities always sum to 1.0.
    """

    outcomes = generate_unique_reroll_outcomes(
        roll,
        mask,
    )

    total_outcomes = sum(
        outcomes.values()
    )

    return {
        result: count / total_outcomes
        for result, count in outcomes.items()
    }