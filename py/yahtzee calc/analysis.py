"""
analysis.py

Computes reusable information about a Yahtzee roll.

Many scoring functions require the same data:
    - total
    - face counts
    - maximum count
    - number of unique faces
    - bit mask of present faces

Instead of recomputing these values in every scoring function,
we compute them once and reuse the result.
"""

from dataclasses import dataclass
from functools import lru_cache

from dice import Roll, count_faces, face_mask, roll_total


FaceCounts = tuple[int, int, int, int, int, int, int]


@dataclass(frozen=True, slots=True)
class RollAnalysis:
    """
    Immutable analysis of a single roll.
    """

    roll: Roll
    total: int
    counts: FaceCounts
    mask: int
    max_count: int
    unique_faces: int


@lru_cache(maxsize=None)
def analyze_roll(
    roll: Roll,
) -> RollAnalysis:
    """
    Analyze a roll and return all commonly used information.

    """

    counts = count_faces(roll)

    return RollAnalysis(
        roll=roll,
        total=roll_total(roll),
        counts=counts,
        mask=face_mask(roll),
        max_count=max(counts),
        unique_faces=sum(1 for count in counts if count > 0),
    )