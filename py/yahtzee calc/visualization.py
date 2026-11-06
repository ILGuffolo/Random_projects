"""
visualization.py

Yahtzee assistant dashboard.

Single matplotlib window containing:
- current roll
- best recommendation
- expected score chart
- probability chart
- alternative strategies
"""

from typing import Sequence

import matplotlib.pyplot as plt

from turn import CategoryEvaluation
from strategy import apply_keep_mask
from dice import Roll


# -----------------------------
# Theme
# -----------------------------

BACKGROUND = "#121212"
CARD = "#1E1E1E"

TEXT = "#EEEEEE"
SUBTEXT = "#AAAAAA"

GREEN = "#4CAF50"
BLUE = "#42A5F5"
ORANGE = "#FFB74D"


# -----------------------------
# Helpers
# -----------------------------


def dice_string(
    roll: Roll,
) -> str:
    """
    Convert dice values into readable symbols.
    """

    faces = {
        1: "⚀",
        2: "⚁",
        3: "⚂",
        4: "⚃",
        5: "⚄",
        6: "⚅",
    }

    return " ".join(
        faces[value]
        for value in roll
    )



def style_axis(
    ax,
) -> None:

    ax.set_facecolor(
        CARD
    )

    ax.tick_params(
        colors=TEXT,
        labelsize=10,
    )

    for spine in ax.spines.values():
        spine.set_visible(False)



def add_value_labels(ax, values, suffix=""):

    xmax = ax.get_xlim()[1]

    for y, value in enumerate(values):

        xpos = min(value + xmax * 0.02, xmax * 0.96)

        ax.text(
            xpos,
            y,
            f"{value:.1f}{suffix}",
            va="center",
            ha="left",
            fontsize=10,
            color="white",
        )


# -----------------------------
# Main dashboard
# -----------------------------


def show_turn_dashboard(
    roll: Roll,
    results: Sequence[CategoryEvaluation],
    rolls_left: int,
) -> None:

    if not results:
        return


    best = results[0]

    kept = apply_keep_mask(
        roll,
        best.keep_mask,
    )


    # only show useful amount
    chart_results = results[:8]


    categories = [
        r.category.name.replace("_", " ").title()
        for r in chart_results
    ]

    expected = [
        r.expected_score
        for r in chart_results
    ]

    probability = [
        r.success_probability * 100
        for r in chart_results
    ]


    # reverse for horizontal chart
    categories.reverse()
    expected.reverse()
    probability.reverse()


    # -----------------------------
    # Figure
    # -----------------------------

    fig = plt.figure(
        figsize=(13, 9),
        facecolor=BACKGROUND,
    )


    fig.suptitle(
        "🎲 YAHTZEE ASSISTANT",
        fontsize=22,
        color=TEXT,
        weight="bold",
    )


    layout = fig.add_gridspec(
        3,
        2,
        height_ratios=[
            1.2,
            3,
            1.35,
        ],
        hspace=0.42,
        wspace=0.45,
)


    # -----------------------------
    # Top information
    # -----------------------------

    info = fig.add_subplot(
        layout[0, :]
    )

    info.axis(
        "off"
    )

    info.set_facecolor(
        CARD
    )


    info.text(
        0.03,
        0.75,
        "CURRENT ROLL",
        color=SUBTEXT,
        fontsize=11,
    )


    info.text(
        0.03,
        0.42,
        dice_string(roll),
        fontsize=30,
        color="white",
        fontweight="bold",
    )
    
    info.text(
        0.03,
        0.15,
        "   ".join(str(d) for d in roll),
        fontsize=13,
        color="#DDDDDD",
        family="monospace",
    )


    info.text(
        0.38,
        0.75,
        "BEST STRATEGY",
        color=SUBTEXT,
        fontsize=11,
    )


    info.text(
        0.38,
        0.47,
        best.category.name.replace("_", " ").title(),
        color="#6CFF6C",
        fontsize=22,
        weight="bold",
    )


    kept_str = " ".join(str(v) for v in kept)

    reroll = tuple(d for d in roll if d not in kept or kept.count(d) < roll[:roll.index(d)+1].count(d))
    reroll_str = " ".join(str(v) for v in reroll)

    info.text(
        0.38,
        0.22,
        "KEEP",
        fontsize=10,
        color=SUBTEXT,
        weight="bold",
    )

    info.text(
        0.38,
        0.08,
        kept_str,
        fontsize=14,
        color=GREEN,
        family="monospace",
    )


    info.text(
        0.72,
        0.55,
        f"Expected\n{best.expected_score:.2f}",
        color=BLUE,
        fontsize=13,
        ha="center",
    )


    info.text(
        0.87,
        0.55,
        f"Chance\n{best.success_probability*100:.1f}%",
        color=GREEN,
        fontsize=13,
        ha="center",
    )


    info.text(
        0.87,
        0.15,
        f"Rerolls: {rolls_left}",
        color=TEXT,
        fontsize=11,
        ha="center",
    )


    # -----------------------------
    # Expected score chart
    # -----------------------------

    ax1 = fig.add_subplot(
        layout[1,0]
    )

    style_axis(ax1)


    ax1.barh(
        categories,
        expected,
        color=BLUE,
    )


    ax1.set_title(
        "Expected Score (EV)",
        fontsize=15,
        color="white",
        pad=12,
        weight="bold",
    )


    ax1.set_xlim(
        0,
        max(expected) * 1.25,
    )


    add_value_labels(
        ax1,
        expected,
    )


    # -----------------------------
    # Probability chart
    # -----------------------------

    ax2 = fig.add_subplot(
        layout[1,1]
    )

    style_axis(ax2)


    ax2.barh(
        categories,
        probability,
        color=GREEN,
    )


    ax2.set_title(
        "Success Probability (%)",
        fontsize=15,
        color="white",
        pad=12,
        weight="bold",
    )

    ax2.set_xlim(
        0,
        100,
    )


    add_value_labels(
        ax2,
        probability,
        "%",
    )


    # -----------------------------
    # Alternatives
    # -----------------------------

    alt = fig.add_subplot(
        layout[2,:]
    )

    alt.axis(
        "off"
    )


    alt.text(
        0.02,
        0.85,
        "ALTERNATIVE STRATEGIES",
        color=SUBTEXT,
        fontsize=12,
    )


    y = 0.68


    for rank, result in enumerate(
        results[1:6],
        start=2,
    ):

        alt.text(
            0.05,
            y,
            f"{rank}. {result.category.name.replace('_', ' ').title()}",
            color=TEXT,
            fontsize=11,
        )

        alt.text(
            0.45,
            y,
            f"EV {result.expected_score:.2f}",
            color=BLUE,
            fontsize=11,
        )


        alt.text(
            0.70,
            y,
            f"{result.success_probability*100:.1f}%",
            color=GREEN,
            fontsize=11,
        )

        y -= 0.11



    plt.show()