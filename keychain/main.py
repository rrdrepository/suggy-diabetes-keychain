"""
main.py - the simulated keychain (prototype).

Run it from the keychain folder with:  python main.py

It opens a window with the 3D keychain. Drag it with the mouse to turn
it and look at every side. The screen and buttons are on its back.

Three buttons, with the same job on every page:
    left arrow, right arrow = move between the choices
    OK                      = pick it / carry on
    Home (small, above the screen) = back to the first page, from anywhere
Keyboard: the Left and Right arrow keys, Enter (or Space) for OK, and
H (or Esc) for Home.

A playful way to learn about food and sugar, with a reminder for kids
who take insulin. Four features: feeding Suggy, the insulin reminder,
checking on Suggy and a short quiz for kids.
Flow:  Hello page -> Menu (Feed, Insulin, Check, Quiz).
When a reminder time comes, "Insulin time!" pops up by itself. The
times are set by a parent in the companion app. No dose is ever shown.
Everything works offline. The keychain is for kids aged 6 to 14. If a parent links the keychain in the
companion app (adult-app/), the Welcome page says "Hello <nickname>!"
and data from the app shows up here. This window re-reads
data/state.json every second.
"""

import time
import tkinter as tk

import insulin
import state_store
from check_screen import CheckScreen
from insulin_screen import InsulinScreen, ReminderScreen
from kid_quiz import KidQuizScreen
from keychain_frame import KeychainFrame
from pet_screen import PetFeedingScreen
from screens import WelcomeScreen, MainMenuScreen

CHECK_EVERY_MS = 1000   # how often we re-read state.json
QUIET_SECONDS = 300     # Home hides a reminder for this long (5 minutes)
INSULIN_MENU_INDEX = 1  # where Insulin sits in the menu


class KeychainApp:
    """Connects the keychain drawing to whichever screen is showing."""

    def __init__(self, root):
        self.root = root
        root.title("Keychain pet - prototype (simulated)")
        root.resizable(False, False)

        # Honest label: this is a simulation, not real hardware.
        tk.Label(root, text="PROTOTYPE - simulated keychain, not a real device",
                 font=("Arial", 9), fg="#6b6b6b").pack(pady=(6, 0))

        # Make sure this keychain's reference number is saved, so the
        # companion app can check it when linking.
        state = state_store.load_state()
        if state["keychain_ref"] != state_store.KEYCHAIN_REF:
            def save_ref(s):
                s["keychain_ref"] = state_store.KEYCHAIN_REF
            state = state_store.update_state(save_ref)

        self.frame = KeychainFrame(root, on_button=self.handle_button,
                                   ref_number=state["keychain_ref"])

        # Demo-only controls, OUTSIDE the keychain picture.
        demo_bar = tk.Frame(root)
        demo_bar.pack(pady=(0, 10))
        # Spins the keychain between its face and its back.
        tk.Button(demo_bar, text="Turn around",
                  command=lambda: self.frame.flip()).pack(side="left", padx=2)
        tk.Label(demo_bar, text="Demo only:", font=("Arial", 9),
                 fg="#6b6b6b").pack(side="left", padx=4)
        # Shows an insulin reminder straight away, without waiting for
        # the time set in the app (for the pitch).
        tk.Button(demo_bar, text="Insulin reminder now",
                  command=self.demo_reminder).pack(side="left", padx=2)

        self.current_screen = None
        self.quiet_until = 0     # no reminder pops up before this moment
        self.show_welcome()
        self.check_for_changes()

    # ---- Watching state.json -----------------------------------------------

    def check_for_changes(self):
        """
        Runs every second:
        - shows the insulin reminder when its time has come
        - lets the current screen redraw if the data changed
        """
        self.check_reminders()

        if hasattr(self.current_screen, "refresh"):
            self.current_screen.refresh()
        self.root.after(CHECK_EVERY_MS, self.check_for_changes)

    # ---- Choosing screens --------------------------------------------------

    def show(self, screen):
        """Make this screen the active one and draw it."""
        # Tell the old screen to stop any timers it was running.
        if self.current_screen is not None and hasattr(self.current_screen,
                                                       "stop"):
            self.current_screen.stop()
        self.current_screen = screen
        screen.draw()

    def show_welcome(self):
        self.show(WelcomeScreen(self.frame.screen, on_start=self.show_menu))

    def show_menu(self, start_index=0):
        """Show the menu, highlighting the choice at start_index."""
        self.show(MainMenuScreen(self.frame.screen,
                                 on_select=self.open_feature,
                                 on_back=self.show_welcome,
                                 start_index=start_index))

    def open_feature(self, name, menu_index):
        """
        Called by the menu when OK is pressed on a choice.
        menu_index is remembered so "back" returns to the same choice.
        """
        def back():
            self.show_menu(start_index=menu_index)

        canvas = self.frame.screen
        if name == "insulin":
            state = state_store.load_state()
            reminder = insulin.due_reminder(state)
            if insulin.waiting_to_eat(state):
                # Insulin taken, meal not eaten yet: show the countdown.
                self.show(ReminderScreen(canvas, on_done=back))
            elif reminder:
                self.show(ReminderScreen(canvas, on_done=back,
                                         reminder=reminder))
            else:
                self.show(InsulinScreen(canvas, on_back=back))
        elif name == "check":
            self.show(CheckScreen(canvas, on_back=back))
        elif name == "quiz":
            self.show(KidQuizScreen(canvas, on_back=back))
        else:
            self.show(PetFeedingScreen(canvas, on_back=back))

    # ---- Demo buttons ------------------------------------------------------

    def demo_reminder(self):
        """Demo button: pretend a reminder time has come right now."""
        self.show(ReminderScreen(self.frame.screen,
                                 on_done=self.back_to_insulin,
                                 reminder=insulin.DEMO_REMINDER))
        self.root.bell()

    def back_to_insulin(self):
        """After a reminder: the menu, with Insulin chosen."""
        self.show_menu(start_index=INSULIN_MENU_INDEX)

    # ---- The insulin reminder ----------------------------------------------

    def check_reminders(self):
        """
        Show "Insulin time!" when a reminder is due, or "Time to eat!"
        when the wait after the insulin is over.
        We never interrupt a feeding or a reminder that is already
        showing, and we stay quiet for a while after Home was pressed.
        """
        if isinstance(self.current_screen, (ReminderScreen, PetFeedingScreen)):
            return
        if time.time() < self.quiet_until:
            return

        state = state_store.load_state()
        reminder = insulin.due_reminder(state)
        waiting = insulin.waiting_to_eat(state)
        if waiting and insulin.seconds_until_meal(state, waiting) == 0:
            self.show(ReminderScreen(self.frame.screen,
                                     on_done=self.back_to_insulin))
        elif reminder and not waiting:
            self.show(ReminderScreen(self.frame.screen,
                                     on_done=self.back_to_insulin,
                                     reminder=reminder))
        else:
            return
        self.root.bell()    # a little sound, like the real keychain would make

    # ---- Buttons -----------------------------------------------------------

    def handle_button(self, label):
        """
        Send the press to the screen that is showing.
        The jobs are the same everywhere: arrows move, OK picks, and the
        small Home button always goes back to the first page.
        """
        if label == "HOME":
            if (isinstance(self.current_screen, ReminderScreen)
                    and self.current_screen.mode != "saved"):
                # Home hides a reminder for a few minutes, then it
                # comes back (unless it was finished).
                self.quiet_until = time.time() + QUIET_SECONDS
            self.show_welcome()
        elif label == "LEFT":
            self.current_screen.left()
        elif label == "RIGHT":
            self.current_screen.right()
        else:
            self.current_screen.ok()


def main():
    root = tk.Tk()
    KeychainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
