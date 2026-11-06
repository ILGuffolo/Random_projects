"""
actions.py

Pure game actions.

No mutation.
Every function returns a new state.
"""

import random

from dice import Roll, make_roll
from gamestate import GameState
from constants import DICE_PER_ROLL, DICE_SIDES
from config import SIMULATE_REROLLS



def reroll_dice(
    roll: Roll,
    keep_mask: int,
) -> Roll:
    """
    Reroll all dice not marked in keep_mask.

    Bit convention:

    bit 0 -> first die
    bit 1 -> second die
    ...
    """

    new_roll = []
    
    
    for index, die in enumerate(roll):

        keep = (
            keep_mask &
            (1 << index)
        )


        if keep:
                new_roll.append(die)

        else:
            if SIMULATE_REROLLS:
                new_roll.append(
                    random.randint(
                        1,
                        DICE_SIDES,
                    )
                )
            else:
                new_roll.append( int(input(
                    "Enter rolled value: "
                )))


    return make_roll(new_roll)



def apply_reroll(
    state: GameState,
    keep_mask: int,
) -> GameState:
    """
    Apply one reroll to a game state.

    Returns a new state.
    """

    if state.rolls_left <= 0:

        raise ValueError(
            "No rerolls remaining"
        )


    return GameState(
        scorecard=state.scorecard,
        roll=reroll_dice(
            state.roll,
            keep_mask,
        ),
        rolls_left=(
            state.rolls_left - 1
        ),
        turn_number=state.turn_number,
    )