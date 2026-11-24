"""
insulin_screen.py - the insulin reminder pages on the keychain.

Two screens:

  ReminderScreen - pops up by itself when a reminder time comes.
      "insulin" page:  "Insulin time!"        OK = took it
      "eat" page:      "Eat in 15 min" (counts down), then
                       "Time to eat!"         OK = I ate
      "saved" page:    "Saved!"               OK = done
      The small Home button hides it for a few minutes (see main.py).

  InsulinScreen - opened from the menu. Shows today's reminder times
      and which ones are done. OK = back.

The times are set by a parent in the companion app, from the doctor's
plan. The rules live in insulin.py.

IMPORTANT: these pages never show a dose and never give advice. They
only remind about the TIME.
"""

import insulin
import pet_drawing
import state_store
from keychain_frame import SCREEN_INK, SCREEN_BG
from screens import (draw_pixel_background, draw_hints, text, MID, TINY,
                     SMALL, NORMAL, BIG)


class ReminderScreen:
    def __init__(self, canvas, on_done, reminder=None):
        """
        reminder: the reminder that is due. Leave it out to start on the
        "eat" page (insulin already taken, waiting for the meal).
        on_done: called when the kid has finished with the reminder.
        """
        self.canvas = canvas
        self.on_done = on_done
        self.reminder = reminder
        self.mode = "insulin" if reminder else "eat"
        self.last_drawn = None

    # ---- Drawing -----------------------------------------------------------

    def _countdown(self, state):
        """The words for the "eat" page: ("Eat in", "15 min") and so on."""
        entry = insulin.waiting_to_eat(state)
        seconds = insulin.seconds_until_meal(state, entry) if entry else 0
        if seconds <= 0:
            return ("Time to eat!", "")
        if seconds > 60:
            return ("Eat in", "%d min" % ((seconds + 59) // 60))
        return ("Eat in", "%d s" % seconds)

    def draw(self):
        c = self.canvas
        draw_pixel_background(c)
        state = state_store.load_state()
        accessories = state["pet"]["accessories"]

        if self.mode == "insulin":
            text(c, 16, "Insulin time!", NORMAL)
            pet_drawing.draw_bell(c, 40, 74)
            pet_drawing.draw_pet(c, 118, 76, "happy", accessories=accessories)
            # Which reminder this is, e.g. "Lunch 12:30".
            words = self.reminder["label"]
            if self.reminder.get("time"):
                words += " " + self.reminder["time"]
            text(c, 122, words)
            draw_hints(c, "took it")

        elif self.mode == "eat":
            title, big = self._countdown(state)
            self.last_drawn = (title, big)
            if big:
                text(c, 18, title, NORMAL)
                text(c, 52, big, BIG)
                pet_drawing.draw_food_icon(c, MID, 100, "brown_rice")
            else:
                text(c, 22, title, NORMAL)
                pet_drawing.draw_pet(c, 68, 82, "happy", mouth_open=True,
                                     accessories=accessories)
                pet_drawing.draw_food_icon(c, 146, 84, "brown_rice")
            draw_hints(c, "I ate")

        else:   # "saved"
            text(c, 18, "Saved!", NORMAL)
            pet_drawing.draw_pet(c, MID, 80, "happy", accessories=accessories)
            draw_hints(c, "done")

    def refresh(self):
        """Every second: keep the countdown on the "eat" page moving."""
        if self.mode == "eat":
            state = state_store.load_state()
            if self._countdown(state) != self.last_drawn:
                self.draw()

    # ---- Buttons -----------------------------------------------------------

    def ok(self):
        if self.mode == "insulin":
            # Save the time the insulin was taken.
            reminder = self.reminder
            state_store.update_state(
                lambda state: insulin.log_insulin(state, reminder))
            # With a meal: count down to eating. Without: just "Saved!".
            self.mode = "eat" if reminder.get("with_meal") else "saved"
            self.draw()
        elif self.mode == "eat":
            state_store.update_state(insulin.log_ate)   # save the meal time
            self.mode = "saved"
            self.draw()
        else:
            self.on_done()

    def left(self):
        pass  # nothing to choose on these pages

    def right(self):
        pass


class InsulinScreen:
    """Today's reminder times, with a tick on the ones that are done."""

    def __init__(self, canvas, on_back):
        self.canvas = canvas
        self.on_back = on_back
        self.last_seen = None

    def _what_to_show(self, state):
        """The things that change this page (so we know when to redraw)."""
        return [(r["label"], r["time"], status)
                for r, status in insulin.todays_reminders(state)]

    def draw(self):
        c = self.canvas
        draw_pixel_background(c)
        rows = self._what_to_show(state_store.load_state())
        self.last_seen = rows

        c.create_text(10, 12, text="INSULIN TODAY", anchor="w", font=SMALL,
                      fill=SCREEN_INK)
        if not rows:
            # Nothing switched on yet: a parent does that in the app.
            text(c, 56, "No times set yet.")
            text(c, 80, "A parent sets them", TINY)
            text(c, 96, "in the app.", TINY)
        for row, (label, time_text, status) in enumerate(rows):
            y = 37 + row * 24
            c.create_text(10, y, anchor="w", text=label, font=SMALL,
                          fill=SCREEN_INK)
            c.create_text(106, y, anchor="w", text=time_text, font=SMALL,
                          fill=SCREEN_INK)
            # The box at the end: ticked when done, "now" when it is time.
            if status == "now":
                c.create_rectangle(162, y - 9, 196, y + 9, fill=SCREEN_INK,
                                   outline=SCREEN_INK)
                c.create_text(179, y, text="now", font=TINY, fill=SCREEN_BG)
            else:
                c.create_rectangle(172, y - 8, 188, y + 8, fill=SCREEN_BG,
                                   outline=SCREEN_INK, width=2)
                if status == "done":
                    c.create_line(175, y, 179, y + 5, 186, y - 5,
                                  fill=SCREEN_INK, width=3)
        draw_hints(c, "back")

    def refresh(self):
        """Redraw when a time is changed in the app or a status changes."""
        if self._what_to_show(state_store.load_state()) != self.last_seen:
            self.draw()

    def ok(self):
        self.on_back()   # OK goes back to the menu

    def left(self):
        pass

    def right(self):
        pass
