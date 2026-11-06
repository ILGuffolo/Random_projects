"""
Represents the player's current Yahtzee score sheet.

A category with value None is still available.
A category with an integer value has already been used.
"""

from dataclasses import dataclass
from typing import Optional

from constants import Category


@dataclass(frozen=True, slots=True)
class ScoreCard:
    """
    Current Yahtzee score card.

    None means category is unused.
    Integer means category has been scored.
    """

    ones: Optional[int] = None
    twos: Optional[int] = None
    threes: Optional[int] = None
    fours: Optional[int] = None
    fives: Optional[int] = None
    sixes: Optional[int] = None

    three_kind: Optional[int] = None
    four_kind: Optional[int] = None
    full_house: Optional[int] = None
    small_straight: Optional[int] = None
    large_straight: Optional[int] = None
    yahtzee: Optional[int] = None
    chance: Optional[int] = None


CATEGORY_FIELDS = {
    Category.ONES: "ones",
    Category.TWOS: "twos",
    Category.THREES: "threes",
    Category.FOURS: "fours",
    Category.FIVES: "fives",
    Category.SIXES: "sixes",
    Category.THREE_KIND: "three_kind",
    Category.FOUR_KIND: "four_kind",
    Category.FULL_HOUSE: "full_house",
    Category.SMALL_STRAIGHT: "small_straight",
    Category.LARGE_STRAIGHT: "large_straight",
    Category.YAHTZEE: "yahtzee",
    Category.CHANCE: "chance",
}


def available_categories(
    scorecard: ScoreCard,
) -> tuple[Category, ...]:
    """
    Return all unused categories.
    """

    available = []

    for category, field in CATEGORY_FIELDS.items():

        if getattr(scorecard, field) is None:
            available.append(category)

    return tuple(available)