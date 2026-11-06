"""
gamestate.py

Complete immutable Yahtzee game state.

This module handles:
- current game information
- empty game creation
- applying scores
"""

from dataclasses import dataclass, replace

from constants import Category
from dice import Roll
from scorecard import (
    ScoreCard,
    available_categories,
    CATEGORY_FIELDS,
)


@dataclass(frozen=True, slots=True)
class GameState:
    """
    Complete Yahtzee position.

    scorecard:
        Current used/unused categories.

    roll:
        Current dice.

    rolls_left:
        Number of rerolls remaining this turn.

    turn_number:
        Completed turns.
    """

    scorecard: ScoreCard
    roll: Roll
    rolls_left: int
    turn_number: int



def empty_game_state(
    roll: Roll,
) -> GameState:
    """
    Create a new game at the beginning
    of a turn.

    All categories are empty.
    Two rerolls are available.
    """

    return GameState(
        scorecard=ScoreCard(),
        roll=roll,
        rolls_left=2,
        turn_number=0,
    )



def get_available_categories(
    state: GameState,
) -> tuple[Category, ...]:
    """
    Return categories that have not
    been scored yet.
    """

    return available_categories(
        state.scorecard
    )



def apply_score(
    state: GameState,
    category: Category,
    value: int,
) -> GameState:
    """
    Apply a score and return a new state.

    The original state is unchanged.

    Example:

        new_state = apply_score(
            state,
            Category.YAHTZEE,
            50,
        )
    """

    field = CATEGORY_FIELDS[category]

    new_scorecard = replace(
        state.scorecard,
        **{
            field: value
        },
    )

    return GameState(
        scorecard=new_scorecard,
        roll=state.roll,
        rolls_left=2,
        turn_number=state.turn_number + 1,
    )

def start_new_turn(
    state: GameState,
    roll: Roll,
) -> GameState:
    """
    Start a new turn after scoring.

    Keeps the scorecard.
    Resets rerolls.
    """

    return GameState(
        scorecard=state.scorecard,
        roll=roll,
        rolls_left=2,
        turn_number=state.turn_number,
    )