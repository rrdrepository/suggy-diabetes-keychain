"""
insulin_page.py - the Insulin tab of the companion app.

This page is for a PARENT or guardian:
- Top half: set the reminder times, copied from the doctor's plan.
  Every kid's plan is different, so nothing is fixed. Tick the
  reminders the kid needs, type the times and press Save. The keychain
  then shows "Insulin time!" at those times.
- Bottom half: what the kid pressed on the keychain: when the insulin
  was taken, when they ate, and the minutes in between.

IMPORTANT: there is NO dose anywhere on this page or on the keychain,
and no advice. It only handles TIMES. Prototype, not a medical device.
"""

import datetime
import tkinter as tk
from tkinter import ttk

import state_store
from app_pages import GREEN, RED, GREY, nice_date

MAX_GAP = 30    # the biggest "minutes before eating" that can be typed


def clock(iso_text):
    """'2026-11-22T12:31:05' -> '12:31' ('-' if there is no time)."""
    try:
        return datetime.datetime.fromisoformat(iso_text).strftime("%H:%M")
    except (ValueError, TypeError):
        return "-"


def gap_text(entry):
    """The minutes between insulin and eating for one log row."""
    if not entry.get("with_meal"):
        return "no meal"
    try:
        taken = datetime.datetime.fromisoformat(entry.get("insulin_at"))
        ate = datetime.datetime.fromisoformat(entry.get("ate_at"))
    except (ValueError, TypeError):
        return "-"                       # not eaten yet
    return "%d min" % round((ate - taken).total_seconds() / 60)


class InsulinPage:
    COLUMNS = [("day", "Day", 70), ("what", "Reminder", 95),
               ("due", "Planned", 60), ("insulin", "Insulin", 60),
               ("ate", "Ate", 60), ("gap", "Gap", 70)]

    def __init__(self, parent):
        self.frame = tk.Frame(parent, padx=12, pady=8)
        tk.Label(self.frame, text="Insulin reminder",
                 font=("Arial", 13, "bold")).pack(anchor="w")
        tk.Label(self.frame, text="For a parent or guardian. Copy the times "
                 "from your child's doctor's plan. The keychain only "
                 "reminds about the time. It never shows a dose.",
                 fg=GREY, wraplength=440, justify="left").pack(anchor="w")
        tk.Label(self.frame, text="Prototype demo, not a medical device. "
                 "Always follow the doctor's plan.",
                 fg=RED, wraplength=440, justify="left").pack(anchor="w")

        # ---- The form: one row for each reminder -----------------------
        form = tk.Frame(self.frame)
        form.pack(anchor="w", pady=(6, 0))
        self.rows = []      # one (reminder id, on/off variable, time box) each
        self.form = form
        self.loaded = False  # the form is filled in once, on the first refresh

        gap_row = tk.Frame(self.frame)
        gap_row.pack(anchor="w", pady=(4, 0))
        tk.Label(gap_row, text="Minutes between insulin and eating:"
                 ).pack(side="left")
        self.gap = tk.Spinbox(gap_row, from_=0, to=MAX_GAP, width=4)
        self.gap.pack(side="left", padx=6)

        save_row = tk.Frame(self.frame)
        save_row.pack(anchor="w", pady=(4, 0))
        tk.Button(save_row, text="Save times", command=self.save
                  ).pack(side="left")
        self.message = tk.Label(save_row, text="", fg=GREEN)
        self.message.pack(side="left", padx=8)

        # ---- The log ---------------------------------------------------
        tk.Label(self.frame, text="Pressed on the keychain",
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(8, 0))
        self.table = ttk.Treeview(self.frame, show="headings", height=6,
                                  columns=[c[0] for c in self.COLUMNS])
        for key, title, width in self.COLUMNS:
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor="w")
        self.table.pack(pady=4)
        self.last_seen = None

    def _fill_form(self, state):
        """Put the saved times into the form (done once)."""
        for row, reminder in enumerate(state["insulin"]["reminders"]):
            on = tk.BooleanVar(value=bool(reminder.get("on")))
            tk.Checkbutton(self.form, text=reminder.get("label", "?"),
                           variable=on, width=10, anchor="w"
                           ).grid(row=row, column=0, sticky="w")
            box = tk.Entry(self.form, width=6)
            box.insert(0, reminder.get("time", ""))
            box.grid(row=row, column=1, padx=4)
            note = ("then a meal" if reminder.get("with_meal")
                    else "no meal after")
            tk.Label(self.form, text=note, fg=GREY).grid(row=row, column=2,
                                                         sticky="w")
            self.rows.append((reminder.get("id"), on, box))
        tk.Label(self.form, text="24-hour time, like 07:00 or 19:30",
                 fg=GREY).grid(row=len(self.rows), column=0, columnspan=3,
                               sticky="w")
        self.gap.delete(0, "end")
        self.gap.insert(0, str(state["insulin"]["gap_minutes"]))
        self.loaded = True

    def save(self):
        """Check what was typed, then save it for the keychain."""
        times = {}
        for reminder_id, on, box in self.rows:
            parsed = state_store.parse_time(box.get())
            if parsed is None:
                self.message.config(fg=RED, text="\"%s\" is not a time. "
                                    "Use 24-hour time like 07:00."
                                    % box.get().strip())
                return
            # Always save it tidy, as two digits each: "7:5" -> "07:05".
            times[reminder_id] = (on.get(), "%02d:%02d" % parsed)
            box.delete(0, "end")
            box.insert(0, times[reminder_id][1])

        gap = self.gap.get().strip()
        if not gap.isdigit() or int(gap) > MAX_GAP:
            self.message.config(fg=RED, text="Minutes must be a number "
                                             "from 0 to %d." % MAX_GAP)
            return

        def change(state):
            state["insulin"]["gap_minutes"] = int(gap)
            for reminder in state["insulin"]["reminders"]:
                if reminder.get("id") in times:
                    reminder["on"], reminder["time"] = times[reminder["id"]]
        state_store.update_state(change)

        switched_on = sum(1 for on, _time in times.values() if on)
        self.message.config(fg=GREEN, text="Saved. %d reminder%s on."
                            % (switched_on, "" if switched_on == 1 else "s"))

    def refresh(self, state):
        if not self.loaded:
            self._fill_form(state)

        log = state["insulin"]["log"]
        seen = (len(log), log[-1].get("insulin_at") if log else None,
                log[-1].get("ate_at") if log else None)
        if seen == self.last_seen:
            return
        self.last_seen = seen
        self.table.delete(*self.table.get_children())
        for entry in reversed(log):                      # newest first
            self.table.insert("", "end", values=(
                nice_date(entry.get("date"))[:6],        # "22 Nov"
                entry.get("label", "?"),
                entry.get("due") or "demo",
                clock(entry.get("insulin_at")),
                clock(entry.get("ate_at")) if entry.get("with_meal") else "-",
                gap_text(entry)))
