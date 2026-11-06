"""
strategy.py

Yahtzee decision engine.

Current version:
- Searches only available categories.
- Searches every possible keep.
- Returns ranked recommendations.
"""

from dataclasses import dataclass

from analysis import analyze_roll
from constants import Category
from dice import Roll
from probabilities import (
    KeepMask,
    generate_keep_masks,
    reroll_probability_distribution,
)
from scorecard import ScoreCard, available_categories
from scoring import SCORERS


@dataclass(frozen=True, slots=True)
class StrategyResult:
    category: Category
    keep_mask: KeepMask
    expected_score: float


def apply_keep_mask(
    roll: Roll,
    mask: KeepMask,
) -> tuple[int, ...]:

    return tuple(
        die
        for index, die in enumerate(roll)
        if mask & (1 << index)
    )


def calculate_expected_score(
    roll: Roll,
    mask: KeepMask,
    category: Category,
) -> float:

    scorer = SCORERS[category]

    probabilities = reroll_probability_distribution(
        roll,
        mask,
    )

    total = 0.0

    for outcome, probability in probabilities.items():

        total += (
            scorer(
                analyze_roll(outcome)
            )
            *
            probability
        )

    return total


def find_best_moves(
    roll: Roll,
    scorecard: ScoreCard,
) -> list[StrategyResult]:
    """
    For every available category, find the
    single best keep strategy.

    Returns categories ranked by their
    highest possible expected score.
    """

    results = []

    categories = available_categories(
        scorecard
    )

    for category in categories:

        best_mask = 0
        best_score = -1.0

        for mask in generate_keep_masks():

            expected = calculate_expected_score(
                roll,
                mask,
                category,
            )

            if expected > best_score:
                best_score = expected
                best_mask = mask

        results.append(
            StrategyResult(
                category=category,
                keep_mask=best_mask,
                expected_score=best_score,
            )
        )

    results.sort(
        key=lambda result: result.expected_score,
        reverse=True,
    )

    return results