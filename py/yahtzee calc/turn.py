"""
turn.py

Evaluates a Yahtzee turn from a GameState.

Supports:
- 2 rerolls remaining
- 1 reroll remaining
- 0 rerolls remaining
"""

from dataclasses import dataclass
from functools import lru_cache

from constants import Category

from gamestate import GameState
from dice import Roll

from analysis import analyze_roll

from probabilities import (
    generate_keep_masks,
    reroll_probability_distribution,
)

from scoring import SCORERS

from scorecard import available_categories

from strategy import apply_keep_mask

from debug import ProgressTracker



@dataclass(frozen=True, slots=True)
class CategoryEvaluation:
    category: Category
    keep_mask: int
    expected_score: float
    success_probability: float



def evaluate_final_roll(
    roll: Roll,
    category: Category,
) -> tuple[float, float]:
    """
    Evaluate scoring immediately.

    Used when no rerolls remain.
    """

    score = SCORERS[category](
        analyze_roll(roll)
    )

    success = (
        1.0
        if score > 0
        else 0.0
    )

    return (
        float(score),
        success,
    )


@lru_cache
def evaluate_after_reroll(
    roll: Roll,
    category: Category,
    rerolls_left: int,
) -> tuple[float, float]:
    """
    Evaluate a position where rerolls remain.

    rerolls_left:
        1 -> one reroll then score
        2 -> two rerolls then score
    """

    if rerolls_left <= 0:

        return evaluate_final_roll(
            roll,
            category,
        )


    best_score = 0.0
    best_probability = 0.0


    for mask in generate_keep_masks():

        distribution = (
            reroll_probability_distribution(
                roll,
                mask,
            )
        )

        total_score = 0.0
        total_probability = 0.0


        for outcome, chance in distribution.items():

            score, probability = (
                evaluate_after_reroll(
                    outcome,
                    category,
                    rerolls_left - 1,
                )
            )


            total_score += (
                score *
                chance
            )

            total_probability += (
                probability *
                chance
            )


        if total_score > best_score:

            best_score = total_score
            best_probability = total_probability


    return (
        best_score,
        best_probability,
    )



def evaluate_category_turn(
    state: GameState,
    category: Category,
) -> CategoryEvaluation:
    """
    Evaluate one category from the
    current game state.
    """

    best_score = 0.0
    best_probability = 0.0
    best_mask = 0


    # No rerolls.
    if state.rolls_left == 0:

        score, probability = (
            evaluate_final_roll(
                state.roll,
                category,
            )
        )

        return CategoryEvaluation(
            category,
            0,
            score,
            probability,
        )


    for mask in generate_keep_masks():

        distribution = (
            reroll_probability_distribution(
                state.roll,
                mask,
            )
        )

        total_score = 0.0
        total_probability = 0.0


        for outcome, chance in distribution.items():

            score, probability = (
                evaluate_after_reroll(
                    outcome,
                    category,
                    state.rolls_left - 1,
                )
            )


            total_score += (
                score *
                chance
            )

            total_probability += (
                probability *
                chance
            )


        if total_score > best_score:

            best_score = total_score
            best_probability = total_probability
            best_mask = mask


    return CategoryEvaluation(
        category,
        best_mask,
        best_score,
        best_probability,
    )



def evaluate_turn(
    state: GameState,
) -> list[CategoryEvaluation]:
    """
    Evaluate every available category
    for the current game state.
    """

    categories = available_categories(
        state.scorecard
    )

    results = []

    tracker = ProgressTracker(
        total=len(categories),
        name="TURN",
    )


    for category in categories:

        results.append(
            evaluate_category_turn(
                state,
                category,
            )
        )

        tracker.update()


    tracker.finish()


    results.sort(
        key=lambda x: x.expected_score,
        reverse=True,
    )

    return results