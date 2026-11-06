"""
main.py

Yahtzee helper prototype.
"""

from dice import random_roll, make_roll
from display import (
    print_header,
    print_roll,
    print_turn_evaluation,
)
from turn import evaluate_turn
from gamestate import (
    empty_game_state,
    apply_score,
    GameState,
)
from config import AUTO_RANDOM_ROLL, SHOW_PYPLOT

from visualization import show_turn_dashboard
from constants import Category

from actions import apply_reroll

def main():

    print_header()
    choice = "" 
    if not AUTO_RANDOM_ROLL:
        choice = input(
            "Random roll? (y/n): "
        )
    else: print("auto random roll selected:")

    if choice.lower() == "y" or AUTO_RANDOM_ROLL:
        roll = random_roll()

    else:
        values = input(
            "Enter five dice: "
        )

        roll = make_roll(
            map(int, values.split())
        )


    # Example scorecard
    #
    # Later this will be loaded
    # from the actual game.

    state = empty_game_state(
        roll
    )
    state = apply_score(state, Category(12), 23)


    print_roll(
        roll
    )


    results = evaluate_turn(
        state,
    )

    print_turn_evaluation(
        roll,
        results,
    )
    
    if SHOW_PYPLOT:
        show_turn_dashboard(
            state.roll,
            results,
            state.rolls_left,
        )


if __name__ == "__main__":
    main()