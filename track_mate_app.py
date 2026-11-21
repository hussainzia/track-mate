"""
Track Mate - Student Task and Progress Tracker (window version)
Code in Place Final Project

This is the window version of Track Mate. It does the same things as the
terminal version (add tasks, pick a priority, tick them off and see my
progress), but with buttons and a real progress bar. It also saves my tasks
to a file, so they are still there the next time I open it.

Run it with:  python3 track_mate_app.py
"""

import json
import os
import random
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

# Colours. I picked these to match the dark look of my project screenshot.
BG = "#1b1e27"
CARD = "#222634"
PANEL = "#2c3142"
HOVER = "#282d3b"
BORDER = "#3a4054"
TEXT = "#f2f2f2"
MUTED = "#8a90a2"
BLUE = "#8cc8ff"
GREEN = "#4fd37a"
YELLOW = "#f2c94c"
RED = "#ef5a5a"

priorities = ["High", "Medium", "Low"]
priority_colors = {"High": RED, "Medium": YELLOW, "Low": GREEN}

# Tasks are saved in a file next to this program.
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

# Shown the very first time, so the app isn't empty.
sample_tasks = [
    {"name": "Finish Code in Place final project", "subject": "Python", "priority": "High", "done": False},
    {"name": "Revise for circuits quiz", "subject": "Engineering", "priority": "High", "done": False},
    {"name": "Read chapter 4", "subject": "Physics", "priority": "Medium", "done": True},
    {"name": "Submit lab report", "subject": "Power Systems", "priority": "Medium", "done": True},
    {"name": "Organize notes", "subject": "General", "priority": "Low", "done": False}
]

start_messages = [
    "You can do it! Start with one small task.",
    "One step at a time. You've got this!",
    "Even a little progress matters."
]
progress_messages = [
    "Good job! Keep going.",
    "You're making progress!",
    "Every completed task counts."
]
almost_messages = [
    "You're almost finished!",
    "Just a few more tasks to go!",
    "You're on fire today! Keep going."
]
finished_messages = [
    "All your tasks are done!",
    "Great work! You completed everything.",
    "Time for a well-deserved break!"
]


# ---------- Helpers for the task list ----------

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


def message_group(percent):
    # Pick which list of messages fits how much is done.
    if percent == 100:
        return finished_messages
    elif percent >= 75:
        return almost_messages
    elif percent >= 25:
        return progress_messages
    else:
        return start_messages


def sorted_tasks(tasks):
    # Unfinished tasks first. Within each group, High comes before Low.
    return sorted(tasks, key=lambda task: (task["done"], priorities.index(task["priority"])))


def load_tasks():
    # Use the saved tasks if there are any, otherwise start with the samples.
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, encoding="utf-8") as file:
                tasks = json.load(file)
            for task in tasks:
                if task["priority"] not in priorities:
                    task["priority"] = "Medium"
            return tasks
        except (OSError, ValueError, KeyError, TypeError):
            print("Could not read tasks.json, so starting with the sample tasks.")
    return [task.copy() for task in sample_tasks]


def save_tasks(tasks):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=2)
    except OSError:
        print("Could not save tasks to", SAVE_FILE)


# ---------- Drawing helpers ----------

def rounded_rect(canvas, x1, y1, x2, y2, radius, **options):
    # Tkinter has no rounded rectangle, so I draw a smooth polygon instead.
    r = radius
    points = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
              x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
              x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(points, smooth=True, **options)


def pick_font(root):
    # Use a nice monospace font if the computer has one.
    installed = tkfont.families(root)
    for name in ["Cascadia Mono", "Consolas", "Menlo", "SF Mono", "DejaVu Sans Mono", "Courier New"]:
        if name in installed:
            return name
    return "Courier"


class TrackMateApp:
    def __init__(self, root):
        self.root = root
        self.tasks = load_tasks()
        self.filter = "All"
        self.new_priority = "High"
        self.message = ""
        self.message_list = None
        self.placeholders = {}

        root.title("Track Mate")
        root.geometry("640x800")
        root.minsize(520, 620)
        root.configure(bg=BG)

        family = pick_font(root)
        self.font_title = (family, 28, "bold")
        self.font_subtitle = (family, 13)
        self.font_body = (family, 12)
        self.font_done = tkfont.Font(family=family, size=12, overstrike=True)
        self.font_bold = (family, 12, "bold")
        self.font_small = (family, 10)

        # Everything sits on one dark card, like the screenshot.
        self.card = tk.Frame(root, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        self.card.pack(fill="both", expand=True, padx=22, pady=22)

        self.build_header()
        self.build_add_form()
        self.build_filter_bar()
        self.build_footer()      # packed before the list so it stays at the bottom
        self.build_task_list()
        self.refresh()

    # ---------- Building the window ----------

    def build_header(self):
        header = tk.Frame(self.card, bg=CARD)
        header.pack(fill="x", padx=28, pady=(26, 4))
        tk.Label(header, text="TRACK MATE", font=self.font_title, fg=TEXT, bg=CARD).pack(anchor="w")
        tk.Label(header, text="Your student task & progress tracker", font=self.font_subtitle,
                 fg=BLUE, bg=CARD).pack(anchor="w")

    def build_add_form(self):
        form = tk.Frame(self.card, bg=CARD)
        form.pack(fill="x", padx=28, pady=(18, 6))

        self.name_entry = self.make_entry(form, "What do you need to do?")
        self.name_entry.master.pack(fill="x")

        row = tk.Frame(form, bg=CARD)
        row.pack(fill="x", pady=(10, 0))

        self.subject_entry = self.make_entry(row, "Subject", width=13)
        self.subject_entry.master.pack(side="left")

        # Three small buttons to choose the priority.
        self.priority_buttons = {}
        for priority in priorities:
            button = self.make_button(row, priority, lambda p=priority: self.choose_priority(p))
            button.pack(side="left", padx=(8, 0))
            self.priority_buttons[priority] = button
        self.choose_priority(self.new_priority)

        add_button = self.make_button(row, "+ Add task", self.add_task, bg=GREEN, fg=BG, bold=True)
        add_button.pack(side="right")

        # Pressing Enter in either box adds the task too.
        self.name_entry.bind("<Return>", lambda event: self.add_task())
        self.subject_entry.bind("<Return>", lambda event: self.add_task())

    def build_filter_bar(self):
        bar = tk.Frame(self.card, bg=CARD)
        bar.pack(fill="x", padx=28, pady=(18, 4))

        self.filter_buttons = {}
        for name in ["All", "To do", "Done"]:
            button = self.make_button(bar, name, lambda n=name: self.choose_filter(n), small=True)
            button.pack(side="left", padx=(0, 6))
            self.filter_buttons[name] = button

        clear = tk.Label(bar, text="Clear done", font=self.font_small, fg=MUTED, bg=CARD, cursor="hand2")
        clear.pack(side="right")
        clear.bind("<Button-1>", lambda event: self.clear_done())
        clear.bind("<Enter>", lambda event: clear.config(fg=RED))
        clear.bind("<Leave>", lambda event: clear.config(fg=MUTED))

        self.left_label = tk.Label(bar, font=self.font_small, fg=MUTED, bg=CARD)
        self.left_label.pack(side="right", padx=(0, 14))

    def build_task_list(self):
        # A canvas with a frame inside it, so the list can scroll.
        holder = tk.Frame(self.card, bg=CARD)
        holder.pack(fill="both", expand=True, padx=20, pady=(4, 0))

        # A thin dark scrollbar. It only shows up when the list is too long.
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Vertical.TScrollbar", background=PANEL, troughcolor=CARD,
                        bordercolor=CARD, lightcolor=PANEL, darkcolor=PANEL,
                        arrowcolor=MUTED, gripcount=0, arrowsize=12)
        style.map("Dark.Vertical.TScrollbar", background=[("active", BORDER)])

        self.list_canvas = tk.Canvas(holder, bg=CARD, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(holder, orient="vertical", command=self.list_canvas.yview,
                                       style="Dark.Vertical.TScrollbar")
        self.list_canvas.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar_shown = False
        self.list_canvas.pack(side="left", fill="both", expand=True)
        self.list_frame = tk.Frame(self.list_canvas, bg=CARD)
        self.list_window = self.list_canvas.create_window(0, 0, window=self.list_frame, anchor="nw")

        self.list_frame.bind("<Configure>", lambda event: self.update_scroll_area())
        self.list_canvas.bind("<Configure>", self.on_list_resize)
        self.list_canvas.bind("<Enter>", lambda event: self.set_mouse_wheel(True))
        self.list_canvas.bind("<Leave>", lambda event: self.set_mouse_wheel(False))

    def build_footer(self):
        footer = tk.Frame(self.card, bg=CARD)
        footer.pack(side="bottom", fill="x", padx=28, pady=(10, 24))

        tk.Frame(footer, bg=BORDER, height=1).pack(fill="x", pady=(0, 16))

        row = tk.Frame(footer, bg=CARD)
        row.pack(fill="x")
        tk.Label(row, text="Progress:", font=self.font_body, fg=TEXT, bg=CARD).pack(side="left")
        self.percent_label = tk.Label(row, font=(self.font_bold[0], 15, "bold"), fg=GREEN, bg=CARD, width=5, anchor="e")
        self.percent_label.pack(side="right")
        self.bar = tk.Canvas(row, height=24, bg=CARD, highlightthickness=0)
        self.bar.pack(side="left", fill="x", expand=True, padx=(14, 6))
        self.bar.bind("<Configure>", lambda event: self.draw_progress_bar())

        self.breakdown = tk.Frame(footer, bg=CARD)
        self.breakdown.pack(fill="x", pady=(12, 0))

        self.tip_label = tk.Label(footer, font=self.font_small, fg=MUTED, bg=CARD, anchor="w")
        self.tip_label.pack(fill="x", pady=(8, 0))

        self.message_label = tk.Label(footer, font=self.font_body, fg=YELLOW, bg=CARD, anchor="w")
        self.message_label.pack(fill="x", pady=(6, 0))

    # ---------- Small reusable widgets ----------

    def make_entry(self, parent, placeholder, width=None):
        # The entry sits inside a frame so the text gets some space around it.
        # The frame's border turns blue while I'm typing in the box.
        box = tk.Frame(parent, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        entry = tk.Entry(box, font=self.font_body, bg=PANEL, fg=MUTED, insertbackground=TEXT,
                         relief="flat", borderwidth=0, highlightthickness=0)
        if width:
            entry.config(width=width)
        entry.pack(fill="x", padx=10, pady=7)
        entry.insert(0, placeholder)
        self.placeholders[entry] = placeholder
        entry.bind("<FocusIn>", lambda event: self.clear_placeholder(entry))
        entry.bind("<FocusOut>", lambda event: self.show_placeholder(entry))
        box.bind("<Button-1>", lambda event: entry.focus_set())
        return entry

    def clear_placeholder(self, entry):
        entry.master.config(highlightbackground=BLUE)
        if entry.cget("fg") == MUTED:
            entry.delete(0, "end")
            entry.config(fg=TEXT)

    def show_placeholder(self, entry):
        entry.master.config(highlightbackground=BORDER)
        if entry.get().strip() == "":
            entry.delete(0, "end")
            entry.insert(0, self.placeholders[entry])
            entry.config(fg=MUTED)

    def entry_text(self, entry):
        # The grey hint text doesn't count as something the user typed.
        if entry.cget("fg") == MUTED:
            return ""
        return entry.get().strip()

    def make_button(self, parent, text, command, bg=PANEL, fg=TEXT, bold=False, small=False):
        # I use Labels as buttons because normal buttons ignore colours on a Mac.
        font = self.font_bold if bold else (self.font_small if small else self.font_body)
        button = tk.Label(parent, text=text, font=font, bg=bg, fg=fg, padx=12, pady=6, cursor="hand2")
        button.bind("<Button-1>", lambda event: command())
        return button

    # ---------- Actions ----------

    def choose_priority(self, priority):
        self.new_priority = priority
        for name, button in self.priority_buttons.items():
            if name == priority:
                button.config(bg=priority_colors[name], fg=BG)
            else:
                button.config(bg=PANEL, fg=MUTED)

    def choose_filter(self, name):
        self.filter = name
        self.refresh()

    def add_task(self):
        name = self.entry_text(self.name_entry)
        if name == "":
            self.name_entry.focus_set()
            self.flash(self.name_entry)
            return
        subject = self.entry_text(self.subject_entry)
        if subject == "":
            subject = "General"

        self.tasks.append({"name": name, "subject": subject, "priority": self.new_priority, "done": False})
        save_tasks(self.tasks)

        self.name_entry.delete(0, "end")
        self.name_entry.focus_set()
        if self.filter == "Done":
            self.filter = "All"
        self.refresh()

    def toggle_task(self, task):
        task["done"] = not task["done"]
        save_tasks(self.tasks)
        if task["done"]:
            self.message = ""   # pick a fresh message as a small reward
        self.refresh()

    def delete_task(self, task):
        if messagebox.askyesno("Delete task", f'Delete "{task["name"]}"?', parent=self.root):
            self.tasks.remove(task)
            save_tasks(self.tasks)
            self.refresh()

    def clear_done(self):
        done = completed_count(self.tasks)
        if done == 0:
            return
        if messagebox.askyesno("Clear finished tasks", f"Remove {done} finished task(s)?", parent=self.root):
            self.tasks = [task for task in self.tasks if not task["done"]]
            save_tasks(self.tasks)
            self.refresh()

    def flash(self, entry):
        # Briefly turn the border red to show something is missing.
        entry.master.config(highlightbackground=RED)
        self.root.after(700, lambda: entry.master.config(highlightbackground=BLUE))

    # ---------- Showing everything ----------

    def refresh(self):
        self.show_tasks()
        self.show_progress()

        for name, button in self.filter_buttons.items():
            if name == self.filter:
                button.config(bg=BLUE, fg=BG)
            else:
                button.config(bg=PANEL, fg=MUTED)

        left = len(self.tasks) - completed_count(self.tasks)
        self.left_label.config(text=f"{left} left")

    def show_tasks(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        visible = []
        for task in sorted_tasks(self.tasks):
            if self.filter == "All" or (self.filter == "Done") == task["done"]:
                visible.append(task)

        if len(visible) == 0:
            if len(self.tasks) == 0:
                text = "No tasks yet. Add your first one above!"
            elif self.filter == "Done":
                text = "Nothing finished yet. You can do it!"
            else:
                text = "Nothing left to do. Nice work!"
            tk.Label(self.list_frame, text=text, font=self.font_body, fg=MUTED, bg=CARD).pack(pady=30)

        for task in visible:
            self.make_task_row(task)

        self.list_canvas.yview_moveto(0)

    def make_task_row(self, task):
        row = tk.Frame(self.list_frame, bg=CARD, cursor="hand2")
        row.pack(fill="x", pady=1)

        # Tick box
        box = tk.Canvas(row, width=24, height=24, bg=CARD, highlightthickness=0)
        box.pack(side="left", padx=(8, 12), pady=9)
        if task["done"]:
            rounded_rect(box, 2, 2, 22, 22, 6, fill=GREEN, outline=GREEN)
            box.create_line(6, 12, 10, 17, 18, 7, fill=BG, width=3, capstyle="round", joinstyle="round")
        else:
            rounded_rect(box, 2, 2, 22, 22, 6, fill="", outline=MUTED, width=2)

        # Priority dot
        dot = tk.Canvas(row, width=14, height=14, bg=CARD, highlightthickness=0)
        dot.pack(side="left", padx=(0, 12))
        dot.create_oval(1, 1, 13, 13, fill=priority_colors[task["priority"]], outline="")

        # Delete button and subject go on the right
        delete = tk.Label(row, text="✕", font=self.font_body, fg=CARD, bg=CARD, padx=8)
        delete.pack(side="right", padx=(4, 4))

        subject = tk.Label(row, text=task["subject"], font=self.font_small, fg=MUTED, bg=PANEL, padx=8, pady=2)
        subject.pack(side="right")

        if task["done"]:
            name = tk.Label(row, text=task["name"], font=self.font_done, fg=MUTED, bg=CARD, anchor="w", justify="left")
        else:
            name = tk.Label(row, text=task["name"], font=self.font_body, fg=TEXT, bg=CARD, anchor="w", justify="left")
        name.pack(side="left", fill="x", expand=True, padx=(0, 10))
        name.bind("<Configure>", lambda event: name.config(wraplength=max(event.width - 4, 50)))

        # Clicking anywhere on the row (except the X) ticks or unticks the task.
        for widget in [row, box, dot, name, subject]:
            widget.bind("<Button-1>", lambda event: self.toggle_task(task))
        delete.bind("<Button-1>", lambda event: self.delete_task(task))

        # Highlight the row when the mouse is over it, and show the X.
        parts = [row, box, dot, name, delete]

        def highlight(on):
            colour = HOVER if on else CARD
            for widget in parts:
                widget.config(bg=colour)
            delete.config(fg=MUTED if on else CARD)

        def on_leave(event):
            # Moving onto a child widget also counts as "leaving" the row,
            # so only remove the highlight if the mouse really left.
            under = self.root.winfo_containing(event.x_root, event.y_root)
            if under not in parts and under is not subject:
                highlight(False)

        for widget in parts + [subject]:
            widget.bind("<Enter>", lambda event: highlight(True), add="+")
            widget.bind("<Leave>", on_leave, add="+")
        delete.bind("<Enter>", lambda event: delete.config(fg=RED), add="+")

    def show_progress(self):
        percent = progress_percent(self.tasks)
        self.percent_label.config(text=f"{percent}%")
        self.draw_progress_bar()

        # Count per priority, e.g. "High 1/2"
        for widget in self.breakdown.winfo_children():
            widget.destroy()
        for priority in priorities:
            group = [task for task in self.tasks if task["priority"] == priority]
            if len(group) == 0:
                continue
            dot = tk.Canvas(self.breakdown, width=10, height=10, bg=CARD, highlightthickness=0)
            dot.pack(side="left", padx=(0, 6))
            dot.create_oval(1, 1, 9, 9, fill=priority_colors[priority], outline="")
            tk.Label(self.breakdown, text=f"{priority} {completed_count(group)}/{len(group)}",
                     font=self.font_small, fg=MUTED, bg=CARD).pack(side="left", padx=(0, 18))

        high_left = 0
        for task in self.tasks:
            if task["priority"] == "High" and not task["done"]:
                high_left += 1
        if high_left > 0:
            self.tip_label.config(text=f"Tip: {high_left} high-priority task(s) left. Try those first!")
        else:
            self.tip_label.config(text="")

        # Only change the message when progress moves into a new range,
        # so it doesn't jump around every time I click something.
        if len(self.tasks) == 0:
            self.message_label.config(text="> Add a task to get started.")
            return
        group = message_group(percent)
        if group is not self.message_list or self.message == "":
            self.message_list = group
            self.message = random.choice(group)
        self.message_label.config(text="> " + self.message)

    def draw_progress_bar(self):
        bar = self.bar
        bar.delete("all")
        width = bar.winfo_width()
        height = int(bar.cget("height"))
        if width < 10:
            return
        rounded_rect(bar, 0, 0, width, height, 8, fill=PANEL, outline=PANEL)
        percent = progress_percent(self.tasks)
        filled = int(width * percent / 100)
        if filled > 0:
            rounded_rect(bar, 0, 0, max(filled, 16), height, 8, fill=GREEN, outline=GREEN)

    # ---------- Scrolling ----------

    def on_list_resize(self, event):
        self.list_canvas.itemconfig(self.list_window, width=event.width)
        self.update_scroll_area()

    def update_scroll_area(self):
        content = self.list_frame.winfo_reqheight()
        visible = self.list_canvas.winfo_height()
        self.list_canvas.config(scrollregion=(0, 0, 0, max(content, visible)))

        needs_scrollbar = content > visible > 1
        if needs_scrollbar and not self.scrollbar_shown:
            self.scrollbar.pack(side="right", fill="y")
            self.scrollbar_shown = True
        elif not needs_scrollbar and self.scrollbar_shown:
            self.scrollbar.pack_forget()
            self.scrollbar_shown = False

    def set_mouse_wheel(self, on):
        if on:
            self.root.bind_all("<MouseWheel>", self.on_mouse_wheel)
            self.root.bind_all("<Button-4>", self.on_mouse_wheel)
            self.root.bind_all("<Button-5>", self.on_mouse_wheel)
        else:
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")

    def on_mouse_wheel(self, event):
        if self.list_frame.winfo_reqheight() <= self.list_canvas.winfo_height():
            return
        if event.num == 4:
            step = -1
        elif event.num == 5:
            step = 1
        elif abs(event.delta) >= 120:      # Windows
            step = -int(event.delta / 120)
        else:                              # Mac
            step = -event.delta
        self.list_canvas.yview_scroll(step, "units")


def main():
    root = tk.Tk()
    TrackMateApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
