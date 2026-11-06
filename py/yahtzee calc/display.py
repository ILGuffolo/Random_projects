"""
Terminal formatting functions.
"""

from strategy import StrategyResult
from dice import Roll
from strategy import apply_keep_mask
from turn import CategoryEvaluation


def print_header() -> None:
    print(
        "\n========================="
    )
    print(
        "       YAHTZEE BOT"
    )
    print(
        "=========================\n"
    )


def print_roll(
    roll: Roll,
) -> None:

    print(
        f"Roll: 🎲 {' '.join(map(str, roll))}"
    )

def print_turn_evaluation(
    roll,
    results: list[CategoryEvaluation],
    amount: int = 5,
) -> None:

    print(
        "\nTURN EVALUATION"
    )

    print(
        "========================="
    )


    for index, result in enumerate(
        results[:amount],
        start=1,
    ):

        print(
            f"\n{index}) "
            f"{result.category.name}"
        )

        print(
            f"Keep: "
            f"{apply_keep_mask(roll, result.keep_mask)}"
        )

        print(
            f"Expected score: "
            f"{result.expected_score:.2f}"
        )

        print(
            f"Success chance: "
            f"{result.success_probability*100:.2f}%"
        )

def print_recommendations(
    roll: Roll,
    results: list[StrategyResult],
    amount: int = 5,
) -> None:

    print(
        "\nBEST STRATEGIES"
    )
    print(
        "-------------------------"
    )

    for index, result in enumerate(
        results[:amount],
        start=1,
    ):

        kept = apply_keep_mask(
            roll,
            result.keep_mask,
        )

        print(
            f"\n{index}) "
            f"{result.category.name}"
        )

        print(
            f"Keep: {kept}"
        )

        print(
            f"Expected score: "
            f"{result.expected_score:.2f}"
        )