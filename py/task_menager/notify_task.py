
import json
from pathlib import Path
from datetime import date, datetime

from winotify import Notification

BASE_DIR = Path(__file__).resolve().parent
TASKS_FILE = BASE_DIR / "tasks.json"


def calculate_priority(task):
    today = date.today()
    due = date.fromisoformat(task["due"])
    days_left = (due - today).days

    # Higher importance means a higher score.
    score = int(task.get("importance", 3)) * 10

    # Deadline urgency: overdue tasks receive a strong boost.
    if days_left < 0:
        score += min(60, 30 + abs(days_left) * 5)
    elif days_left == 0:
        score += 35
    elif days_left == 1:
        score += 25
    elif days_left <= 3:
        score += 15
    elif days_left <= 7:
        score += 5

    # Small preference for tasks that are quick to complete.
    minutes = int(task.get("estimated_minutes", 30))
    if minutes <= 15:
        score += 5

    return score


def main():
    if not TASKS_FILE.exists():
        raise FileNotFoundError(f"Missing file: {TASKS_FILE}")

    with TASKS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    tasks = [
        task for task in data.get("tasks", [])
        if task.get("status", "open") == "open"
    ]

    if not tasks:
        title = "Your to-do list"
        message = "No open tasks. You're all caught up!"
    else:
        tasks.sort(
            key=lambda task: (
                calculate_priority(task),
                task.get("due", "9999-12-31"),
                -int(task.get("importance", 3))
            ),
            reverse=True
        )

        top_tasks = tasks[:3]
        lines = []

        for i, task in enumerate(top_tasks, start=1):
            due = date.fromisoformat(task["due"])
            due_text = due.strftime("%d %b")
            score = calculate_priority(task)

            lines.append(
                f"{i}. {task['title']} (due {due_text}, score {score})"
            )

        title = "Your top priorities today"
        message = "\n".join(lines)

    toast = Notification(
        app_id="Personal Task Priorities",
        title=title,
        msg=message,
        duration="long"
    )
    toast.show()


if __name__ == "__main__":
    main()
