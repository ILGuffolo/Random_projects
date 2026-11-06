"""
Lightweight debug/progress reporting.
"""

import time

from config import DEBUG_PROGRESS


class ProgressTracker:
    """
    Prints periodic progress updates.
    """

    def __init__(
        self,
        total: int,
        name: str,
        interval: float = 5.0,
    ) -> None:

        self.total = total
        self.name = name
        self.interval = interval

        self.current = 0
        self.start_time = time.time()
        self.last_print = self.start_time


    def update(
        self,
        amount: int = 1,
    ) -> None:

        self.current += amount

        now = time.time()

        if (
            DEBUG_PROGRESS
            and
            now - self.last_print >= self.interval
        ):
            self.print_status()
            self.last_print = now


    def print_status(self) -> None:

        elapsed = (
            time.time()
            -
            self.start_time
        )

        if self.current:

            rate = (
                self.current /
                (elapsed + 0.0001)
            )

            remaining = (
                self.total -
                self.current
            )

            eta = (
                remaining /
                rate
                if rate > 0
                else 0
            )

        else:
            eta = 0


        percentage = (
            self.current /
            self.total *
            100
            if self.total
            else 100
        )


        print(
            f"[{self.name}] "
            f"{self.current}/{self.total} "
            f"({percentage:.1f}%) "
            f"elapsed={elapsed:.1f}s "
            f"ETA={eta:.1f}s"
        )


    def finish(self) -> None:

        if DEBUG_PROGRESS:
            self.print_status()

            print(
                f"[{self.name}] COMPLETE"
            )