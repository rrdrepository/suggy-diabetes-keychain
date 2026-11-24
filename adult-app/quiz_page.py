"""
quiz_page.py - the Quiz tab: 5 questions a day about diabetes.

One question at a time, with 4 answer buttons. After an answer the page
shows whether it was right, the explanation and the source, then a
"Next question" button. After the 5th it shows today's score. A right
answer gives 5 points. Tomorrow there are 5 new questions.

The questions are in quiz.py.
"""

import tkinter as tk

import fun
import quiz
import state_store
from app_pages import GREEN, RED, GREY


class QuizPage:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, padx=12, pady=8)
        tk.Label(self.frame, text="Daily quiz",
                 font=("Arial", 13, "bold")).pack(anchor="w")
        tk.Label(self.frame, text="For parents and guardians. 5 questions a "
                 "day, +%d points for each right answer. General facts "
                 "only, not medical advice."
                 % quiz.POINTS_PER_RIGHT_ANSWER, fg=GREY, wraplength=430,
                 justify="left").pack(anchor="w")

        self.progress = tk.Label(self.frame, text="",
                                 font=("Arial", 10, "bold"))
        self.progress.pack(anchor="w", pady=(8, 0))
        self.question = tk.Label(self.frame, text="", wraplength=430,
                                 justify="left", font=("Arial", 11))
        self.question.pack(anchor="w", pady=(2, 6))

        # The 4 answer buttons.
        self.option_buttons = []
        for i in range(4):
            # White answer cards (they light up under the mouse, see fun.py).
            button = tk.Button(self.frame, text="", wraplength=410,
                               justify="left", anchor="w", width=58,
                               bg=fun.CARD, pady=5,
                               command=lambda pick=i: self.pick(pick))
            button.pack(anchor="w", pady=2)
            self.option_buttons.append(button)

        self.verdict = tk.Label(self.frame, text="",
                                font=("Arial", 11, "bold"))
        self.verdict.pack(anchor="w", pady=(8, 0))
        self.why = tk.Label(self.frame, text="", wraplength=430,
                            justify="left")
        self.why.pack(anchor="w")
        self.source = tk.Label(self.frame, text="", wraplength=430,
                               justify="left", fg=GREY, font=("Arial", 8))
        self.source.pack(anchor="w", pady=(2, 0))
        self.next_button = tk.Button(self.frame, text="Next question",
                                     command=self.next_question)

        self.showing = None        # what is on the page now
        self.reviewing = None      # question whose explanation is showing

    # ---- What to show ------------------------------------------------------

    def refresh(self, state):
        today = state_store.today_text()
        questions = quiz.questions_for(today)
        answers = quiz.todays_answers(state)
        if self.reviewing is not None:
            return                 # leave the explanation up until "Next"
        showing = (today, len(answers))
        if showing == self.showing:
            return                 # nothing changed
        self.showing = showing
        if len(answers) >= len(questions):
            self._show_score(answers)
        else:
            self._show_question(questions[len(answers)], len(answers))

    def _show_question(self, question, number):
        self.progress.config(text="Question %d of %d"
                             % (number + 1, quiz.QUESTIONS_PER_DAY))
        self.question.config(text=question["q"])
        for i, button in enumerate(self.option_buttons):
            button.config(text=question["options"][i], state="normal",
                          fg=fun.INK, bg=fun.CARD)
            button.pack(anchor="w", pady=2, before=self.verdict)
        self.verdict.config(text="")
        self.why.config(text="")
        self.source.config(text="")
        self.next_button.pack_forget()
        self.current = question

    def _show_score(self, answers):
        right = sum(1 for a in answers if a.get("correct"))
        self.progress.config(text="Today's quiz is done")
        self.question.config(text="You got %d of %d right and earned %d "
                             "points.\nCome back tomorrow for 5 new "
                             "questions."
                             % (right, len(answers),
                                right * quiz.POINTS_PER_RIGHT_ANSWER))
        for button in self.option_buttons:
            button.pack_forget()
        self.verdict.config(text="")
        self.why.config(text="")
        self.source.config(text="")
        self.next_button.pack_forget()

    # ---- Buttons -----------------------------------------------------------

    def pick(self, pick):
        """An answer button was pressed."""
        question = self.current
        correct = quiz.answer(question["id"], pick)
        self.reviewing = question
        for i, button in enumerate(self.option_buttons):
            button.config(state="disabled")
        # Mark the right answer in the list.
        right_button = self.option_buttons[question["answer"]]
        right_button.config(text="✓ " + question["options"]
                            [question["answer"]], disabledforeground=GREEN,
                            bg="#dff3df")           # soft green behind it
        if correct:
            self.verdict.config(text="Right! +%d points"
                                % quiz.POINTS_PER_RIGHT_ANSWER, fg=GREEN)
        else:
            self.verdict.config(text="Not quite. The answer is marked "
                                "above.", fg=RED)
        self.why.config(text=question["why"])
        self.source.config(text="Source: " + quiz.SOURCES[question["source"]])
        self.next_button.pack(anchor="w", pady=(8, 0))

    def next_question(self):
        for button in self.option_buttons:
            button.config(disabledforeground=GREY)
        self.reviewing = None
        self.showing = None
        self.refresh(state_store.load_state())
