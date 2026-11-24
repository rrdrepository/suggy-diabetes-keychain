"""
app_pages.py - the pages of the companion app after linking.

    HomePage     hello, points, Suggy (with cosmetics), insulin times
    FeedingPage  the saved feedings and the points they gave
(The Insulin, Shop, Vouchers and Quiz tabs are in their own files.)

Each page is a class with a refresh(state) method. main.py calls it
every second with the newest data from data/state.json, so anything done
on the keychain shows up here by itself.

These two pages only READ the data. They never change it.
"""

import datetime
import tkinter as tk
from tkinter import ttk

import fun
import pet_drawing

GREEN = "#2e7d32"
RED = "#b3261e"
GREY = "#6b6b6b"
MAX_HEARTS = 5

# The order of the sore marks, one for each heart Suggy has lost
# (the same order as BODY_PARTS in keychain/feeding.py).
SORE_ORDER = ["eyes", "hands", "legs", "kidney"]


def nice_time(iso_text):
    """'2026-11-21T07:45:00' -> '21 Nov 07:45'."""
    try:
        when = datetime.datetime.fromisoformat(iso_text)
    except (ValueError, TypeError):
        return str(iso_text)
    return when.strftime("%d %b %H:%M")


def nice_date(iso_text):
    """'2026-11-21' -> '21 Nov 2026'."""
    try:
        return datetime.date.fromisoformat(iso_text).strftime("%d %b %Y")
    except (ValueError, TypeError):
        return str(iso_text)


class SuggyView:
    """
    A small picture of Suggy, the same drawing as on the keychain screen,
    with the cosmetics, hearts and tired marks. Used on Home and in the
    Shop. Suggy bobs gently up and down, and jumps when clicked.
    """

    WIDTH, HEIGHT = 200, 110

    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, width=self.WIDTH, height=self.HEIGHT,
                                bg=pet_drawing.SCREEN_BG,
                                highlightthickness=2,
                                highlightbackground=pet_drawing.SCREEN_INK)
        self.last_seen = None
        self.pet = None                 # the newest pet data
        # The Bouncer calls self.draw(offset) to move Suggy up and down.
        self.bouncer = fun.Bouncer(self.canvas, self.draw)

    def refresh(self, state):
        pet = state["pet"]
        seen = (pet["awake"], pet["hearts"], tuple(pet["accessories"]))
        if seen == self.last_seen:
            return                      # nothing changed, no need to redraw
        self.last_seen = seen
        self.pet = dict(pet)
        self.bouncer.redraw = True      # draw the new look on the next frame

    def draw(self, offset=0):
        """Draw Suggy, moved up or down by offset pixels (the bobbing)."""
        pet = self.pet
        if pet is None:
            return
        c = self.canvas
        c.delete("all")
        pet_drawing.draw_hearts(c, self.WIDTH - 62, 6, pet["hearts"],
                                MAX_HEARTS)
        if pet["awake"]:
            lost = MAX_HEARTS - pet["hearts"]
            pet_drawing.draw_pet(c, self.WIDTH // 2, 64 + offset, "happy",
                                 accessories=pet["accessories"],
                                 sore=SORE_ORDER[:max(0, lost)])
        else:
            # Asleep after running out of hearts (woken up on the keychain).
            pet_drawing.draw_pet(c, self.WIDTH // 2, 64, "sleepy",
                                 accessories=pet["accessories"])


class HomePage:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, padx=12, pady=10)
        self.hello = tk.Label(self.frame, text="", font=("Arial", 15, "bold"))
        self.hello.pack(anchor="w")

        self.points = tk.Label(self.frame, text="", font=("Arial", 26, "bold"),
                               fg=GREEN)
        self.points.pack(anchor="w", pady=(6, 0))
        self.points_count = fun.CountUp(self.points, "%d points")
        tk.Label(self.frame, text="Spend them in the Shop or on Vouchers.",
                 fg=GREY).pack(anchor="w")

        self.suggy = SuggyView(self.frame)
        self.suggy.canvas.pack(pady=10)

        self.insulin = tk.Label(self.frame, text="", justify="left",
                                wraplength=440)
        self.insulin.pack(anchor="w")
        self.feedings = tk.Label(self.frame, text="", justify="left")
        self.feedings.pack(anchor="w", pady=(4, 0))

        tk.Label(self.frame,
                 text="How to earn points:\n"
                      "  +10 for each light food choice when feeding Suggy\n"
                      "  +5 for each right answer in the daily quiz\n"
                      "  +5 for each right answer in the keychain quiz "
                      "(first round of the day)",
                 fg=GREY, justify="left").pack(anchor="w", pady=(10, 0))

    def refresh(self, state):
        self.hello.config(text="Hello %s!" % (state["link"]["nickname"]
                                              or "friend"))
        self.points_count.set(state["points"]["balance"])   # counts up
        self.suggy.refresh(state)

        # The insulin reminder times that are switched on, earliest first.
        times = sorted((r.get("time", ""), r.get("label", ""))
                       for r in state["insulin"]["reminders"] if r.get("on"))
        if times:
            self.insulin.config(text="Insulin reminders: " + ", ".join(
                "%s %s" % (label, time_text) for time_text, label in times))
        else:
            self.insulin.config(text="Insulin reminders: none set "
                                     "(a parent sets them in the Insulin tab)")
        self.feedings.config(text="Feedings saved: %d" % len(state["feed_log"]))


class FeedingPage:
    COLUMNS = [("when", "When", 90), ("meal", "Meal", 95),
               ("drink", "Drink", 85), ("dessert", "Dessert", 85),
               ("points", "Points", 50)]

    def __init__(self, parent):
        self.frame = tk.Frame(parent, padx=12, pady=10)
        tk.Label(self.frame, text="Feeding history",
                 font=("Arial", 13, "bold")).pack(anchor="w")
        tk.Label(self.frame, text="Every feeding done on the keychain, "
                 "newest first. +10 points for each light choice.",
                 fg=GREY, wraplength=400, justify="left").pack(anchor="w")

        self.table = ttk.Treeview(self.frame, show="headings", height=11,
                                  columns=[c[0] for c in self.COLUMNS])
        for key, title, width in self.COLUMNS:
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor="w")
        self.table.pack(pady=8)

        self.summary = tk.Label(self.frame, text="", justify="left")
        self.summary.pack(anchor="w")
        self.last_seen = None

    def refresh(self, state):
        log = state["feed_log"]
        seen = (len(log), log[-1]["at"] if log else None)
        if seen == self.last_seen:
            return
        self.last_seen = seen

        self.table.delete(*self.table.get_children())
        for record in reversed(log):                     # newest first
            names = list(record.get("food_names", [])) + ["", "", ""]
            self.table.insert("", "end", values=(
                nice_time(record.get("at")), names[0], names[1], names[2],
                "+%d" % record.get("points", 0)))

        if log:
            sweet = sum(r.get("sweet_picks", 0) for r in log)
            light = 3 * len(log) - sweet
            self.summary.config(text="%d feedings: %d light choices, "
                                     "%d sweet choices."
                                     % (len(log), light, sweet))
        else:
            self.summary.config(text="No feedings yet. Feed Suggy on the "
                                     "keychain and it will show here.")
