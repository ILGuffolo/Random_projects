
import json
from pathlib import Path
from datetime import date

# Always use the JSON file in the same folder as this script
TASKS_FILE = Path(__file__).resolve().parent / "tasks.json"


def load_tasks():
    """Load tasks from JSON, creating the file if necessary."""
    if not TASKS_FILE.exists():
        save_tasks({"tasks": []})

    try:
        with TASKS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
            raise ValueError("Expected a JSON object containing a tasks list.")

        return data

    except (json.JSONDecodeError, ValueError) as error:
        print(f"\nError reading tasks.json: {error}")
        print("Fix the JSON file before continuing.")
        return None


def save_tasks(data):
    """Save tasks to JSON."""
    with TASKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def display_tasks(data):
    """Display all tasks."""
    tasks = data["tasks"]

    if not tasks:
        print("\nNo tasks found.")
        return

    print("\n========== YOUR TASKS ==========")

    for task in tasks:
        print(f"\nID:          {task.get('id', '?')}")
        print(f"Title:       {task.get('title', 'Untitled')}")
        print(f"Due:         {task.get('due', 'Not set')}")
        print(f"Importance:  {task.get('importance', 3)}/5")
        print(f"Duration:    {task.get('estimated_minutes', 30)} minutes")
        print(f"Status:      {task.get('status', 'open')}")
        print(f"Tags:        {', '.join(task.get('tags', []))}")

    print("\n================================")


def add_task(data):
    """Ask for task details and add a new task."""
    print("\n========== ADD TASK ==========")

    title = input("Task title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    # Validate deadline
    while True:
        due = input("Due date (YYYY-MM-DD): ").strip()
        try:
            date.fromisoformat(due)
            break
        except ValueError:
            print("Invalid date. Example: 2026-10-30")

    # Validate importance
    while True:
        try:
            importance = int(input("Importance (1-5): "))
            if 1 <= importance <= 5:
                break
            print("Enter a number from 1 to 5.")
        except ValueError:
            print("Enter a valid integer.")

    # Validate estimated duration
    while True:
        try:
            minutes = int(input("Estimated minutes: "))
            if minutes > 0:
                break
            print("Duration must be greater than zero.")
        except ValueError:
            print("Enter a valid integer.")

    tags_input = input("Tags (comma-separated, optional): ").strip()
    tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

    # Generate a unique ID
    existing_ids = [
        task["id"] for task in data["tasks"]
        if isinstance(task.get("id"), int)
    ]
    new_id = max(existing_ids, default=0) + 1

    task = {
        "id": new_id,
        "title": title,
        "due": due,
        "importance": importance,
        "estimated_minutes": minutes,
        "status": "open",
        "tags": tags
    }

    data["tasks"].append(task)
    save_tasks(data)

    print(f"\nTask added successfully! ID: {new_id}")


def delete_task(data):
    """Delete a task using its ID."""
    display_tasks(data)

    if not data["tasks"]:
        return

    try:
        task_id = int(input("\nEnter the ID of the task to delete: "))
    except ValueError:
        print("Invalid ID.")
        return

    for task in data["tasks"]:
        if task.get("id") == task_id:
            print(f"\nTask: {task.get('title', 'Untitled')}")
            confirm = input("Delete this task? (y/n): ").strip().lower()

            if confirm == "y":
                data["tasks"].remove(task)
                save_tasks(data)
                print("Task deleted.")
            else:
                print("Deletion cancelled.")
            return

    print("No task found with that ID.")


def main():
    while True:
        data = load_tasks()

        if data is None:
            return

        print("\n========== TASK MANAGER ==========")
        print("1. Display tasks")
        print("2. Add task")
        print("3. Delete task")
        print("4. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            display_tasks(data)
        elif choice == "2":
            add_task(data)
        elif choice == "3":
            delete_task(data)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Select 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
