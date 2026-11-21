"""
Track Mate - Student Task and Progress Tracker
Code in Place Final Project

I made this program to keep track of my study tasks in one place.
I can add tasks, choose how important they are, mark them as finished,
and check how much work I have completed.
"""

import random

# These are the three priority levels used in the program.
priorities = ["High", "Medium", "Low"]
priority_icons = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}

# Some example tasks to try the program without entering everything myself.
sample_tasks = [
    {"name": "Finish Code in Place final project", "subject": "Python", "priority": "High", "done": False},
    {"name": "Revise for circuits quiz", "subject": "Engineering", "priority": "High", "done": False},
    {"name": "Read chapter 4", "subject": "Physics", "priority": "Medium", "done": True},
    {"name": "Submit lab report", "subject": "Power Systems", "priority": "Medium", "done": True},
    {"name": "Organize notes", "subject": "General", "priority": "Low", "done": False}
]

# A few messages to make checking progress a little more encouraging.
start_messages = [
    "You can do it! Start with one small task. 🌱",
    "One step at a time. You've got this! 😊",
    "Even a little progress matters. ⏱️"
]
progress_messages = [
    "Good job! Keep going. 💪",
    "You're making progress! 🚀",
    "Every completed task counts. 🎯"
]
almost_messages = [
    "You're almost finished! 🏁",
    "Just a few more tasks to go! 🌟",
    "Keep it up. You're doing great! 🔥"
]
finished_messages = [
    "All your tasks are done! 🎉",
    "Great work! You completed everything. 🏆",
    "Time for a well-deserved break! ☕"
]


def ask_yes_no(question):
    # Keep asking until the answer is yes or no.
    while True:
        answer = input(question).strip().lower()
        if answer == "y" or answer == "yes":
            return True
        elif answer == "n" or answer == "no":
            return False
        else:
            print("Please enter y or n.")


def ask_priority():
    while True:
        answer = input("Priority (H for High, M for Medium, L for Low): ").strip().lower()
        if answer == "h" or answer == "high":
            return "High"
        elif answer == "m" or answer == "medium":
            return "Medium"
        elif answer == "l" or answer == "low":
            return "Low"
        else:
            print("Please choose H, M or L.")


def completed_count(tasks):
    count = 0
    for task in tasks:
        if task["done"]:
            count += 1
    return count


def progress_percent(tasks):
    if len(tasks) == 0:
        return 0
    return round(completed_count(tasks) / len(tasks) * 100)


def progress_bar(percent):
    # The bar has 20 blocks. More filled blocks means more work is done.
    filled = round(percent / 100 * 20)
    return "█" * filled + "░" * (20 - filled)


def motivation(percent):
    if percent == 100:
        return random.choice(finished_messages)
    elif percent >= 75:
        return random.choice(almost_messages)
    elif percent >= 25:
        return random.choice(progress_messages)
    else:
        return random.choice(start_messages)


def sorted_tasks(tasks):
    # Show unfinished tasks first. Within each group, High comes before Low.
    return sorted(tasks, key=lambda task: (task["done"], priorities.index(task["priority"])))


def show_task(number, task):
    if task["done"]:
        status = "✅"
    else:
        status = "⬜"
    icon = priority_icons[task["priority"]]
    print(f'{number}. {status} {icon} {task["name"]} [{task["subject"]}]')


def choose_task(tasks, question):
    # Display the available tasks so the user can pick one by number.
    for number, task in enumerate(tasks, start=1):
        show_task(number, task)

    while True:
        answer = input(f"{question} (1-{len(tasks)}, or Enter to cancel): ").strip()
        if answer == "":
            print("Cancelled.")
            return None
        if answer.isdigit():
            number = int(answer)
            if 1 <= number <= len(tasks):
                return tasks[number - 1]
        print("Please choose a number from the list.")


def add_task(tasks):
    print("\n➕ ADD A TASK")
    name = input("Enter task name: ").strip()
    while name == "":
        name = input("Please give your task a name: ").strip()

    subject = input("Enter subject (or press Enter for General): ").strip()
    if subject == "":
        subject = "General"

    priority = ask_priority()
    new_task = {"name": name, "subject": subject, "priority": priority, "done": False}
    tasks.append(new_task)
    print(f"Task added: {name} ({priority} priority) {priority_icons[priority]}")


def view_tasks(tasks):
    print("\n📋 YOUR TASKS")
    if len(tasks) == 0:
        print("You don't have any tasks yet. Add one from the menu!")
        return

    for number, task in enumerate(sorted_tasks(tasks), start=1):
        show_task(number, task)


def complete_task(tasks):
    print("\n✅ COMPLETE A TASK")
    unfinished = []
    for task in sorted_tasks(tasks):
        if not task["done"]:
            unfinished.append(task)

    if len(unfinished) == 0:
        print("There are no unfinished tasks. Great job!")
        return

    selected = choose_task(unfinished, "Which task did you finish?")
    if selected is None:
        return

    selected["done"] = True
    print(f'Well done! "{selected["name"]}" is now complete. {random.choice(progress_messages)}')
    if completed_count(tasks) == len(tasks):
        print("🎉 You finished all your tasks!")


def delete_task(tasks):
    print("\n🗑️ DELETE A TASK")
    if len(tasks) == 0:
        print("There are no tasks to delete.")
        return

    selected = choose_task(sorted_tasks(tasks), "Which task do you want to delete?")
    if selected is None:
        return

    if ask_yes_no(f'Delete "{selected["name"]}"? (y/n): '):
        tasks.remove(selected)
        print("Task deleted.")
    else:
        print("No changes made.")


def progress_report(tasks):
    print("\n📊 PROGRESS REPORT")
    if len(tasks) == 0:
        print("Add a few tasks first to see your progress.")
        return

    done = completed_count(tasks)
    percent = progress_percent(tasks)
    print(f"Overall progress: {progress_bar(percent)} {percent}%")
    print(f"Completed tasks: {done} out of {len(tasks)}")

    print("\nProgress by priority:")
    for priority in priorities:
        group = []
        for task in tasks:
            if task["priority"] == priority:
                group.append(task)
        if len(group) > 0:
            print(f"{priority_icons[priority]} {priority}: {completed_count(group)}/{len(group)} completed")

    high_remaining = 0
    for task in tasks:
        if task["priority"] == "High" and not task["done"]:
            high_remaining += 1
    if high_remaining > 0:
        print(f"\nTip: You still have {high_remaining} high-priority task(s). Try those first!")

    print("\n💬 " + motivation(percent))


def show_menu(tasks):
    print("\n" + "-" * 42)
    if len(tasks) > 0:
        percent = progress_percent(tasks)
        print(f"Progress: {progress_bar(percent)} {percent}%")
        print("-" * 42)
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Complete Task")
    print("4. Delete Task")
    print("5. Progress Report")
    print("6. Quit")


def main():
    print("=" * 42)
    print("              📋 TRACK MATE")
    print("      Student Task & Progress Tracker")
    print("=" * 42)

    tasks = []
    if ask_yes_no("Would you like to try some sample tasks? (y/n): "):
        for task in sample_tasks:
            tasks.append(task.copy())
        print(f"Added {len(tasks)} sample tasks.")

    # Keep showing the menu until the user chooses to quit.
    while True:
        show_menu(tasks)
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            progress_report(tasks)
        elif choice == "6":
            print("\n👋 Thanks for using Track Mate!")
            if len(tasks) > 0:
                print(f"You completed {completed_count(tasks)} out of {len(tasks)} tasks ({progress_percent(tasks)}%).")
                print(motivation(progress_percent(tasks)))
            print("See you next time!")
            break
        else:
            print("Please choose a number from 1 to 6.")


if __name__ == "__main__":
    main()
