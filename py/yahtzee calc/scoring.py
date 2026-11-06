"""
scoring.py

All official Yahtzee scoring rules.

Every function is pure:
    input  -> RollAnalysis
    output -> score (int)

No function modifies anything.
"""

from typing import Callable

from analysis import RollAnalysis
from constants import (
    Category,
    FULL_HOUSE_SCORE,
    LARGE_STRAIGHT_SCORE,
    SMALL_STRAIGHT_SCORE,
    YAHTZEE_SCORE,
)

# ==========================================================
# Upper Section
# ==========================================================


def score_ones(a: RollAnalysis) -> int:
    return a.counts[1]


def score_twos(a: RollAnalysis) -> int:
    return a.counts[2] * 2


def score_threes(a: RollAnalysis) -> int:
    return a.counts[3] * 3


def score_fours(a: RollAnalysis) -> int:
    return a.counts[4] * 4


def score_fives(a: RollAnalysis) -> int:
    return a.counts[5] * 5


def score_sixes(a: RollAnalysis) -> int:
    return a.counts[6] * 6


# ==========================================================
# Lower Section
# ==========================================================


def score_three_kind(a: RollAnalysis) -> int:
    if a.max_count >= 3:
        return a.total
    return 0


def score_four_kind(a: RollAnalysis) -> int:
    if a.max_count >= 4:
        return a.total
    return 0


def score_full_house(a: RollAnalysis) -> int:
    frequencies = sorted(a.counts)

    if frequencies[-1] == 3 and frequencies[-2] == 2:
        return FULL_HOUSE_SCORE

    return 0


def score_small_straight(a: RollAnalysis) -> int:
    straights = (
        0b00011110,  # 1-2-3-4
        0b00111100,  # 2-3-4-5
        0b01111000,  # 3-4-5-6
    )

    for straight in straights:
        if (a.mask & straight) == straight:
            return SMALL_STRAIGHT_SCORE

    return 0


def score_large_straight(a: RollAnalysis) -> int:
    return (
        LARGE_STRAIGHT_SCORE
        if a.mask in (
            0b00111110,  # 1-2-3-4-5
            0b01111100,  # 2-3-4-5-6
        )
        else 0
    )


def score_yahtzee(a: RollAnalysis) -> int:
    if a.max_count == 5:
        return YAHTZEE_SCORE
    return 0


def score_chance(a: RollAnalysis) -> int:
    return a.total


# ==========================================================
# Lookup Table
# ==========================================================

ScoringFunction = Callable[[RollAnalysis], int]

SCORERS: dict[Category, ScoringFunction] = {
    Category.ONES: score_ones,
    Category.TWOS: score_twos,
    Category.THREES: score_threes,
    Category.FOURS: score_fours,
    Category.FIVES: score_fives,
    Category.SIXES: score_sixes,
    Category.THREE_KIND: score_three_kind,
    Category.FOUR_KIND: score_four_kind,
    Category.FULL_HOUSE: score_full_house,
    Category.SMALL_STRAIGHT: score_small_straight,
    Category.LARGE_STRAIGHT: score_large_straight,
    Category.YAHTZEE: score_yahtzee,
    Category.CHANCE: score_chance,
}