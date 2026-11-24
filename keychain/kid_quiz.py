"""
kid_quiz.py - the Quiz feature on the keychain, for kids aged 6 to 14.

(The app has its own, harder quiz for parents. This one is separate.)

How it works:
- One round is 3 questions, picked at random from the list below.
- Every question has TWO answers, shown as two cards side by side.
  The arrows move between them, OK picks one.
- After each pick the screen says "Yes!" or "Not quite" with one short
  fact, so the kid learns something either way. No blame.
- At the end: "2 of 3 right!" and the points earned.
- Points: +5 for each right answer, but only for the FIRST round of the
  day. The kid can play again as often as they like for fun, but
  playing again gives no more points until tomorrow. (Otherwise points
  could be collected by repeating the quiz.)

The questions are simple things a 6 to 14 year old can know or guess.
They are general facts, not advice. To add one, copy a line and change
it. Keep the lines short so they fit the small screen:
    question   1 or 2 lines, at most 20 letters each
    answers    the RIGHT answer first, then the wrong one; each answer
               is 1 or 2 short lines (the screen mixes up the sides)
    fact       1 or 2 lines, at most 21 letters each

FOR THE TEAM TO REVIEW: please read the questions before the pitch.
"""

import random

import pet_drawing
import state_store
from keychain_frame import SCREEN_INK, SCREEN_BG
from screens import (draw_pixel_background, draw_hints, draw_card, text,
                     MID, TINY, SMALL, NORMAL)

QUESTIONS_PER_ROUND = 3
POINTS_PER_RIGHT_ANSWER = 5

# (question lines, right answer, wrong answer, fact lines)
QUESTIONS = [
    (["Which drink has", "no sugar?"],
     ["Water"], ["Soft", "drink"],
     ["Water has no sugar", "at all."]),
    (["Which gives slow,", "steady energy?"],
     ["Brown", "rice"], ["Sweets"],
     ["Whole grains give", "energy slowly."]),
    (["What does your body", "use sugar for?"],
     ["Energy"], ["Sleep"],
     ["Sugar in the blood", "is fuel for you."]),
    (["What helps sugar", "get into your cells?"],
     ["Insulin"], ["Water"],
     ["Insulin works like", "a key for sugar."]),
    (["Can you catch", "diabetes?"],
     ["No"], ["Yes"],
     ["Diabetes does not", "spread like a cold."]),
    (["Which has more", "fibre?"],
     ["Apple"], ["Apple", "juice"],
     ["Whole fruit keeps", "its fibre."]),
    (["Where is insulin", "made?"],
     ["Pancreas"], ["Heart"],
     ["The pancreas sits", "behind the stomach."]),
    (["Is active play", "good for you?"],
     ["Yes"], ["No"],
     ["Moving helps your", "whole body."]),
    (["Which has lots of", "added sugar?"],
     ["Bubble", "tea"], ["Plain", "milk"],
     ["Bubble tea is a", "very sweet drink."]),
    (["How many kidneys do", "most people have?"],
     ["Two"], ["Five"],
     ["Kidneys clean your", "blood."]),
    (["Do sweets cause", "type 1 diabetes?"],
     ["No"], ["Yes"],
     ["Type 1 is nobody's", "fault."]),
    (["Who helps people", "with diabetes?"],
     ["Doctors"], ["Pirates"],
     ["Doctors and nurses", "help every day."]),
]


def new_round():
    """
    Pick the questions of one round. Each one becomes a dict with the
    two answers on random sides, and "right" = which side is correct.
    """
    chosen = random.sample(QUESTIONS, QUESTIONS_PER_ROUND)
    quiz_round = []
    for question, right_answer, wrong_answer, fact in chosen:
        right_side = random.randint(0, 1)        # 0 = left card, 1 = right
        answers = [wrong_answer, wrong_answer]
        answers[right_side] = right_answer
        quiz_round.append({"question": question, "answers": answers,
                           "right": right_side, "fact": fact})
    return quiz_round


def give_points(state, right_answers):
    """
    Give the points for a finished round, if today's points were not
    given yet. Changes the state in place. Returns the points given
    (0 for a second round on the same day).
    """
    today = state_store.today_text()
    if state["kid_quiz"]["points_date"] == today:
        return 0
    state["kid_quiz"]["points_date"] = today
    points = right_answers * POINTS_PER_RIGHT_ANSWER
    state_store.add_points(state, points)
    return points


class KidQuizScreen:
    """
    What the screen shows (self.mode):
      "ask"     the question and the two answer cards (OK = pick)
      "answer"  "Yes!" or "Not quite" and the fact (OK = next)
      "end"     how many were right and the points (OK = done, back to
                the menu)
    """

    def __init__(self, canvas, on_back):
        self.canvas = canvas
        self.on_back = on_back
        self.questions = new_round()
        self.number = 0           # which question we are on (0 = first)
        self.side = 0             # 0 = left card chosen, 1 = right card
        self.was_right = False    # was the last pick right?
        self.score = 0
        self.points = None        # points given for this round (None = not yet)
        self.points_already = False   # True if today's points were given before
        self.mode = "ask"

    # ---- Drawing -----------------------------------------------------------

    def draw(self):
        c = self.canvas
        draw_pixel_background(c)
        if self.mode == "ask":
            self._draw_question()
        elif self.mode == "answer":
            self._draw_answer()
        else:
            self._draw_end()

    def _draw_question(self):
        c = self.canvas
        current = self.questions[self.number]
        # The question, on 1 or 2 lines at the top.
        lines = current["question"]
        y = 22 - (len(lines) - 1) * 8
        for line in lines:
            text(c, y, line, TINY)
            y += 16
        # The two answer cards. The chosen one is dark.
        for i, answer in enumerate(current["answers"]):
            x1 = 6 + i * 96
            chosen = (i == self.side)
            draw_card(c, x1, 42, x1 + 92, 104, chosen)
            if chosen:
                c.create_rectangle(x1 + 3, 45, x1 + 89, 101, fill=SCREEN_INK,
                                   outline=SCREEN_INK)
            y = 73 - (len(answer) - 1) * 9
            # A long word (like "Pancreas") uses the smaller font.
            font = SMALL if max(len(line) for line in answer) > 7 else NORMAL
            for line in answer:
                c.create_text(x1 + 46, y, text=line, font=font,
                              fill=SCREEN_BG if chosen else SCREEN_INK)
                y += 18
        # Which question this is, e.g. "1/3", and what OK does.
        c.create_text(8, 144, anchor="w", font=TINY, fill=SCREEN_INK,
                      text="%d/%d" % (self.number + 1, len(self.questions)))
        draw_hints(c, "pick")

    def _draw_answer(self):
        c = self.canvas
        current = self.questions[self.number]
        # A smile for a right answer, a calm face otherwise. No blame.
        text(c, 16, "Yes!" if self.was_right else "Not quite", NORMAL)
        pet_drawing.draw_pet(c, MID, 58,
                             "happy" if self.was_right else "okay")
        y = 104
        for line in current["fact"]:
            text(c, y, line, TINY)
            y += 15
        draw_hints(c, "next")

    def _draw_end(self):
        c = self.canvas
        text(c, 18, "%d of %d right!" % (self.score, len(self.questions)),
             NORMAL)
        pet_drawing.draw_pet(c, MID, 68, "happy")
        if self.points:
            text(c, 114, "+%d points!" % self.points)
        elif self.points_already:
            # A second round today: fun only, points come back tomorrow.
            text(c, 114, "More points tomorrow", TINY)
        draw_hints(c, "done")

    def _save_points(self):
        """The round is finished: give the points (first round of the day)."""
        today = state_store.today_text()
        before = state_store.load_state()["kid_quiz"]["points_date"]
        self.points_already = (before == today)
        result = {}

        def change(state):
            result["points"] = give_points(state, self.score)
        state_store.update_state(change)
        self.points = result["points"]

    # ---- Buttons -----------------------------------------------------------

    def left(self):
        if self.mode == "ask":
            self.side = 0
            self.draw()

    def right(self):
        if self.mode == "ask":
            self.side = 1
            self.draw()

    def ok(self):
        if self.mode == "ask":
            self.was_right = (self.side == self.questions[self.number]["right"])
            if self.was_right:
                self.score += 1
            self.mode = "answer"
            self.draw()
        elif self.mode == "answer":
            if self.number < len(self.questions) - 1:
                self.number += 1
                self.side = 0
                self.mode = "ask"
            else:
                self.mode = "end"
                self._save_points()
            self.draw()
        else:
            self.on_back()       # round finished: back to the menu
